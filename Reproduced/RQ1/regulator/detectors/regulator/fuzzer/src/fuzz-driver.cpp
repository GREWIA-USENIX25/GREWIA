#include "src/execution/isolate.h"

#include "fuzz-driver.hpp"

#include "fuzz/corpus.hpp"
#include "fuzz/work-queue.hpp"

#include "regexp-executor.hpp"
#include "interesting-char-finder.hpp"
#include "flags.hpp"

#include <memory>
#include <cstring>
#include <random>
#include <chrono>
#include <iostream>
#include <iomanip>
#include <mutex>
#include <condition_variable>
#include <thread>


namespace f = regulator::flags;

namespace regulator
{
namespace fuzz
{

/**
 * The number of mutant children to produce for each
 * selected parent
 */
static const size_t N_CHILDREN_PER_PARENT = 200;


/**
 * Represents the in-progress information about a fuzzing campaign.
 */
template<typename Char>
class FuzzCampaign
{
public:
    FuzzCampaign(size_t strlen, regulator::executor::V8RegExp *regexp)
        : executions_since_last_render(0),
          num_generations(0),
          regexp(regexp),
          strlen(strlen),
          max_total(0),
          last_screen_render(std::chrono::steady_clock::now() - std::chrono::hours(100)),
          exec_since_last_progress(std::chrono::seconds(0)),
          exec_overall(std::chrono::seconds(0))
        {};
    ~FuzzCampaign()
    {
    }
#ifdef REG_PROFILE
    /**
     * Amount of time spent executing regexp since last render
     */
    std::chrono::steady_clock::duration exec_dur;

    /**
     * Amount of time spent generating children since last render
     */
    std::chrono::steady_clock::duration gen_child_dur;

    /**
     * Amount of time spent economizing the corpus
     */
    std::chrono::steady_clock::duration econo_dur;
#endif // REG_PROFILE

    /**
     * How much active work-time has passed since the last time
     * the corpus expanded.
     */
    std::chrono::steady_clock::duration exec_since_last_progress;

    /**
     * How much active work-time has passed in total.
     */
    std::chrono::steady_clock::duration exec_overall;

    /**
     * The length of the string to fuzz
     */
    const size_t strlen;

    int32_t max_total;

    /**
     * The regular expression to fuzz
     */
    regulator::executor::V8RegExp *regexp;

    /**
     * The active Corpus for this campaign
     */
    Corpus<Char> corpus;

    /**
     * The number of regular expression executions which
     * took place since last screen render
     */
    uintmax_t executions_since_last_render;

    /**
     * The number of generation rounds completed
     */
    uintmax_t num_generations;

    /**
     * The queue of parents to fuzz
     */
    regulator::fuzz::Queue<Char> work_queue;

    /**
     * When the last screen render occurred
     */
    std::chrono::steady_clock::time_point last_screen_render;
};


/**
 * A linked-list element which holds a fuzz campaign description.
 */
struct fuzz_campaign_ll {
    /**
     * Previous linked-list element
     */
    struct fuzz_campaign_ll *prev;

    /**
     * Next linked-list element
     */
    struct fuzz_campaign_ll *next;

    /**
     * A pointer to either a FuzzCampaign<uint8_t> or a
     * FuzzCampaign<uint16_t> ... consult `is_one_byte`
     * to disambiguate.
     */
    void *campaign;

    /**
     * True when this is a 8-bit Char, False when it is
     * 16-bit Char.
     */
    bool is_one_byte;
};


/**
 * Contains context about the entire active fuzzing campaign
 */
typedef struct {
    /**
     * When the fuzzing campaign began
     */
    std::chrono::steady_clock::time_point begin;

    /**
     * When the fuzzing campaign must exit
     */
    std::chrono::steady_clock::time_point deadline;

    /**
     * A linked-list of campaigns to work on
     */
    struct fuzz_campaign_ll *work_ll;

    std::mutex global_mutex;

    std::condition_variable work_ll_waiter;

    std::chrono::steady_clock::duration individual_timeout;

    int32_t max_total;

    /**
     * The number of active (non-quit) fuzz campaigns; used
     * to indicate when all worker-threads should quit because
     * no work remains.
     */
    size_t n_active_campaigns;

    /**
     * When true, the fuzzing loop should exit as soon as possible
     */
    bool exit_requested;
} fuzz_global_context;


/**
 * A work-interrupt point for printing status about a
 * fuzzing campaign.
 */
template<typename Char>
inline void work_interrupt(FuzzCampaign<Char> *campaign)
{
    auto now  = std::chrono::steady_clock::now();
    // Print stuff to screen if we haven't done that lately
    if ((now - campaign->last_screen_render) > std::chrono::milliseconds(500))
    {

        auto elapsed_since_last_render = now - campaign->last_screen_render;
        double seconds_elapsed_since_last_render = elapsed_since_last_render.count() / (static_cast<double>(std::nano::den));

        double seconds_elapsed_work_time = campaign->exec_overall.count() / (static_cast<double>(std::nano::den));

        std::ostringstream to_print;
        to_print << "SUMMARY ";
        to_print << (sizeof(Char) == 1 ? "1-byte " : "2-byte ");
        to_print << "len=" << std::dec << campaign->strlen << " ";

        double execs_per_second = campaign->executions_since_last_render / seconds_elapsed_since_last_render;
        to_print << "Exec/s: "
            << std::setprecision(5) << std::setw(4) << execs_per_second << " "
            << std::setw(0)
            << "Corpus Size: " << campaign->corpus.Size() << " "
            << "Work-Time: "
            << std::setprecision(7) << std::setw(4) << seconds_elapsed_work_time << " s "
            << "Slowest(1-byte): " << campaign->corpus.MaxOpcount()->ToString();

#ifdef REG_PROFILE
        // Print and reset profiling stats. VERY UGLY.
        double seconds_exec = 0;
        double seconds_gen_child = 0;
        double seconds_econo = 0;

        seconds_exec += campaign->exec_dur.count()
            / static_cast<double>(std::nano::den);
        seconds_gen_child += campaign->gen_child_dur.count()
            / static_cast<double>(std::nano::den);
        seconds_econo += campaign->econo_dur.count()
            / static_cast<double>(std::nano::den);

        campaign->gen_child_dur =
            ctx.campaign_one_byte->exec_dur =
            ctx.campaign_one_byte->econo_dur =
                std::chrono::steady_clock::duration::zero();

        to_print << std::setprecision(7) << std::setw(0)
                  << "\nPROFILE Exec: " << seconds_exec << " "
                  << "GenChild: " << seconds_gen_child << " "
                  << "Econo: " << seconds_econo << " "
                  << "Other: " << (seconds_elapsed_since_last_render - (seconds_exec + seconds_gen_child + seconds_econo));
#endif

        if (f::FLAG_debug)
        {
            to_print << "\nDEBUG ";

            // Print the residency of the upper-bound coverage map
            double residency = campaign->corpus.Residency() * 100;
            to_print << "residency=";
            to_print << std::setprecision(4) << std::setw(5) << std::setfill(' ') << residency
                << "% ";
        }

        campaign->last_screen_render = now;
        campaign->executions_since_last_render = 0;
        to_print << "\n";
        std::cout << to_print.str() << std::flush;
    }
}


/**
 * Seed the corpus, returns true on success
 */
template<typename Char>
inline bool seed_corpus(
    Corpus<Char> &corpus,
    regulator::executor::V8RegExp *regexp,
    size_t strlen,
    std::vector<std::string> &seeds
    )
{
    if (f::FLAG_debug)
    {
        std::cout << "DEBUG Seeding corpus" << std::endl;
    }
    Char *baseline = new Char[strlen];
    for (size_t i=0; i<strlen; i++)
    {
        baseline[i] = 'a';
    }

    // we need to execute them to get the initial coverage tracker
    regulator::executor::V8RegExpResult result(strlen);
    if (f::FLAG_debug)
    {
        std::cout << "DEBUG executing seed to establish baseline" << std::endl;
    }
    regulator::executor::Result result_code = regulator::executor::Exec(
        regexp,
        baseline,
        strlen,
        result,
        10000,
#if defined REG_COUNT_PATHLENGTH
        UINT64_MAX,
#endif
        regulator::executor::kOnlyOneByte
    );

    if (result_code != regulator::executor::kSuccess && result_code != regulator::executor::kViolateMaxTotal)
    {
        std::cout << "Baseline execution failed!!!" << std::endl;
        return false;
    }

    CorpusEntry<Char> *entry = new CorpusEntry<Char>(
        baseline,
        strlen,
        new CoverageTracker(*result.coverage_tracker.get())
    );

    corpus.Record(entry);

    // now, repeat that for all seeds which are no longer than this strlen
    for (std::string seed : seeds)
    {
        if (seed.size() > strlen)
        {
            continue;
        }

        std::string derived_seed = seed;
        while (derived_seed.size() < strlen)
        {
            derived_seed += "1";
        }

        Char *buf = new Char[derived_seed.size()];
        for (size_t i=0; i < derived_seed.size(); i++)
        {
            buf[i] = derived_seed[i];
        }

        regulator::executor::Result result_code = regulator::executor::Exec(
            regexp,
            buf,
            strlen,
            result,
            10000,
#if defined REG_COUNT_PATHLENGTH
            UINT64_MAX,
#endif
            regulator::executor::kOnlyOneByte
        );

        if (result_code != regulator::executor::kSuccess && result_code != regulator::executor::kViolateMaxTotal)
        {
            std::cout << "Baseline execution failed!!!" << std::endl;
            return false;
        }

        CorpusEntry<Char> *entry = new CorpusEntry<Char>(
            buf,
            strlen,
            new CoverageTracker(*result.coverage_tracker.get())
        );

        corpus.Record(entry);
    }

    corpus.FlushGeneration();

    return true;
}


/**
 * Make a FuzzCampaign object, seed it, and add it to the linked-list
 * of campaigns.
 *
 * Returns false when creation or seed fails.
 */
template <typename Char>
inline bool make_campaign(
    struct fuzz_campaign_ll *&head,
    regulator::executor::V8RegExp *regexp,
    size_t strlen,
    std::vector<std::string> &seeds,
    int32_t max_total)
{
    FuzzCampaign<Char> *campaign_out = new FuzzCampaign<Char>(strlen, regexp);
    campaign_out->max_total = max_total;

    if (!seed_corpus(campaign_out->corpus, regexp, strlen, seeds))
    {
        std::cerr << "ERROR: failed to seed corpus" << std::endl;
        return false;
    }

    if (f::FLAG_debug)
    {
        std::cout << "DEBUG finished seeding a campaign" << std::endl;
    }

    std::vector<Char> *interesting = new std::vector<Char>();
    if (!fuzz::ExtractInteresting(*regexp, *interesting))
    {
        std::cerr << "ERROR: failed to extract interesting chars" << std::endl;
        return false;
    }
    campaign_out->corpus.SetInteresting(interesting);

    struct fuzz_campaign_ll *new_elem = new fuzz_campaign_ll;
    new_elem->campaign = campaign_out;
    new_elem->is_one_byte = sizeof(Char) == 1;

    // add the new linked-list elem to the circular linked list
    if (head == nullptr)
    {
        head = new_elem;
        new_elem->next = new_elem;
        new_elem->prev = new_elem;
    }
    else
    {
        //
        // +-- new_elem <-----+
        // |                  |
        // +---> HEAD ---> <stuff>
        //
        new_elem->next = head;
        new_elem->prev = head->prev;
        head->prev->next = new_elem;
        head->prev = new_elem;
    }

    return true;
}


/**
 * Evaluate a child solution on a given regexp and evaluate
 * whether it is worth keeping. If so the new CorpusEntry
 * is returned, and the known-worst entry is updated.
 */
template<typename Char>
inline bool evaluate_child(
    Char *child,
    size_t strlen,
    regulator::executor::V8RegExp *regexp,
    regulator::executor::V8RegExpResult &result, // share this memory to avoid re-allocing all the time
    FuzzCampaign<Char> *campaign,
    CorpusEntry<Char> *parent)
{
#ifdef REG_PROFILE
    std::chrono::steady_clock::time_point exec_start = std::chrono::steady_clock::now();
#endif
    constexpr auto enforce_encoding =
        sizeof(Char) == 1
        ? regulator::executor::kOnlyOneByte
        : regulator::executor::kOnlyTwoByte;

    regulator::executor::Result result_code = regulator::executor::Exec(
        regexp,
        child,
        strlen,
        result,
        campaign->max_total,
#if defined REG_COUNT_PATHLENGTH
        UINT64_MAX,
#endif
        enforce_encoding
    );

#ifdef REG_PROFILE
    campaign->exec_dur += (std::chrono::steady_clock::now() - exec_start);
#endif

    if (result_code == regulator::executor::kSuccess)
    {
        // Execution succeeded, proceed to analyze how 'good' this was
        campaign->executions_since_last_render++;

        result.coverage_tracker->Bucketize();

        // If this child uncovered new behavior, then add it to new_children
        // (later added to corpus, which assumes ownership)
        if (
                campaign->corpus.HasNewPath(result.coverage_tracker.get()) &&
                !campaign->corpus.IsRedundant(result.coverage_tracker.get())
            )
        {
            campaign->corpus.BumpStaleness(result.coverage_tracker.get());

            campaign->corpus.Record(
                new CorpusEntry<Char>(
                    child,
                    strlen,
                    new CoverageTracker(*result.coverage_tracker.get())
                )
            );

            return true;
        }
    }
    else if (result_code == regulator::executor::kViolateMaxTotal)
    {
        std::cout << "Maximum Total reached: " << (
            new CorpusEntry<Char>(
                    child,
                    strlen,
                    new CoverageTracker(*result.coverage_tracker.get())
                )
            )->ToString();
        return false;
    }

    // No significance found in this child -- toss its memory
    delete[] child;
    return true;
}


/**
 * Pass over the given Corpus exactly once
 */
template<typename Char>
inline bool work_on_campaign(FuzzCampaign<Char> *campaign)
{
    regulator::executor::V8RegExpResult result(campaign->strlen);
    std::vector<Char *> children_to_eval;
    auto yield_deadline = std::chrono::steady_clock::now() + std::chrono::milliseconds(100);
    auto start_time = std::chrono::steady_clock::now();
    auto last_progress_time_this_try = start_time;

    while (std::chrono::steady_clock::now() < yield_deadline)
    {
        // If we've already fuzzed everything in the queue, flush and
        // re-build the queue
        if (!campaign->work_queue.HasNext())
        {
            size_t prev_corpus_size = campaign->corpus.Size();
#ifdef REG_PROFILE
            std::chrono::steady_clock::time_point econo_start = std::chrono::steady_clock::now();
#endif
            // record new children into corpus
            campaign->corpus.FlushGeneration();
#ifdef REG_PROFILE
            campaign->econo_dur += (std::chrono::steady_clock::now() - econo_start);
#endif
            if (prev_corpus_size < campaign->corpus.Size())
            {
                // Reset all work-clocks because we added to the corpus and made progress
                last_progress_time_this_try = std::chrono::steady_clock::now();
                campaign->exec_since_last_progress = std::chrono::seconds(0);
            }

            campaign->num_generations++;

            campaign->work_queue.Fill(campaign->corpus);
        }

        CorpusEntry<Char> *parent = campaign->work_queue.Pop();

        // Create children
#ifdef REG_PROFILE
        std::chrono::steady_clock::time_point gen_start = std::chrono::steady_clock::now();
#endif
        children_to_eval.clear();
        campaign->corpus.GenerateChildren(
            parent,
            N_CHILDREN_PER_PARENT,
            children_to_eval
        );
#ifdef REG_PROFILE
        campaign->gen_child_dur += (std::chrono::steady_clock::now() - gen_start);
#endif

        // Evaluate each child
        for (size_t j = 0; j < children_to_eval.size(); j++)
        {
            Char *child = children_to_eval[j];

            bool keep_going = evaluate_child<Char>(
                child,
                campaign->strlen,
                campaign->regexp,
                result,
                campaign,
                parent
            );
            if (!keep_going)
            {
                return false;
            }
        }
    }

    // advance the work-time sums
    std::chrono::steady_clock::duration work_done_since_progress = std::chrono::steady_clock::now() - last_progress_time_this_try;
    campaign->exec_since_last_progress += work_done_since_progress;

    std::chrono::steady_clock::duration work_done = std::chrono::steady_clock::now() - start_time;
    campaign->exec_overall += work_done;
    return true;
}


/**
 * Entry point for a work thread
 */
void do_work(fuzz_global_context *context)
{
    if (f::FLAG_debug)
    {
        std::cout << "DEBUG started thread "
            << std::hex << std::this_thread::get_id() << std::dec << std::endl;
    }

    regulator::executor::Initialize();

    while (context->deadline > std::chrono::steady_clock::now())
    {
        // get a campaign to work on
        struct fuzz_campaign_ll *my_work;

        {
            std::unique_lock<std::mutex> lock(context->global_mutex);

            while (context->work_ll == nullptr && context->n_active_campaigns > 0)
            {
                std::cout << "DEBUG thread "
                    << std::hex << std::this_thread::get_id() << std::dec
                    << " waiting"
                    << std::endl;
                context->work_ll_waiter.wait(lock);
            }

            if (context->n_active_campaigns == 0)
            {
                // there's no more work to do, quit
                return;
            }


            // take an item off the head
            my_work = context->work_ll;

            if (context->work_ll->next == context->work_ll)
            {
                // if this is the last thing in the work-list then set null
                context->work_ll = nullptr;
            }
            else
            {
                // otherwise just re-rig the linked-list to delete head
                context->work_ll = context->work_ll->next;
                context->work_ll->prev = my_work->prev;
                my_work->prev->next = my_work->next;
            }
        }

        // we have our campaign to work on, perform one unit of work
        bool should_quit_campaign;
        if (my_work->is_one_byte)
        {
            auto campaign = reinterpret_cast<regulator::fuzz::FuzzCampaign<uint8_t> *>(my_work->campaign);
            bool keep_going = work_on_campaign<uint8_t>(campaign);
            work_interrupt(campaign);

            should_quit_campaign = !keep_going || campaign->exec_since_last_progress > context->individual_timeout;
        }
        else
        {
            auto campaign = reinterpret_cast<regulator::fuzz::FuzzCampaign<uint16_t> *>(my_work->campaign);
            bool keep_going = work_on_campaign<uint16_t>(campaign);
            work_interrupt(campaign);

            should_quit_campaign = !keep_going || campaign->exec_since_last_progress > context->individual_timeout;
        }

        // work completed, put my_work back on the work_ll ONLY IF WE SHOULD NOT QUIT
        if (!should_quit_campaign) {
            std::unique_lock<std::mutex> lock(context->global_mutex);

            if (context->work_ll == nullptr)
            {
                context->work_ll = my_work;
                my_work->next = my_work;
                my_work->prev = my_work;
            }
            else
            {
                // put my_work in head->prev
                my_work->prev = context->work_ll->prev;
                my_work->next = context->work_ll;
                context->work_ll->prev->next = my_work;
                context->work_ll->prev = my_work;
            }

            context->work_ll_waiter.notify_one();
        }
        else
        {
            // [branch] should_quit_campaign == true

            std::unique_lock<std::mutex> lock(context->global_mutex);
            context->n_active_campaigns--;

            if (context->n_active_campaigns == 0)
            {
                // if there's no more work to do, tell everyone
                context->work_ll_waiter.notify_all();
            }

            if (my_work->is_one_byte)
            {
                delete reinterpret_cast<regulator::fuzz::FuzzCampaign<uint8_t> *>(my_work->campaign);
            }
            else
            {
                delete reinterpret_cast<regulator::fuzz::FuzzCampaign<uint16_t> *>(my_work->campaign);
            }
        }
    }

    if (f::FLAG_debug)
    {
        std::cout << "DEBUG Time expired in thread" << std::endl;
    }
}


uint64_t Fuzz(
    v8::Isolate *isolate,
    regulator::executor::V8RegExp *regexp,
    std::vector<size_t> &strlens,
    std::vector<std::string> &seeds,
    int32_t timeout_secs,
    int32_t individual_timeout_secs,
    int32_t max_total,
    bool fuzz_one_byte,
    bool fuzz_two_byte,
    uint16_t n_threads)
{
    fuzz_global_context context;

    context.begin = std::chrono::steady_clock::now();
    context.work_ll = nullptr;
    context.max_total = max_total;

    if (timeout_secs > 0)
    {
        context.deadline = context.begin + std::chrono::seconds(timeout_secs);
    }
    else
    {
        // no timeout so just set it to 10 yr
        context.deadline = context.begin + std::chrono::seconds(60ul * 60ul * 24ul * 365ul * 10ul);
    }

    if (individual_timeout_secs > 0)
    {
        context.individual_timeout = std::chrono::seconds(individual_timeout_secs);
    }
    else
    {
        // no individual timeout so just set it to 10yr
        context.individual_timeout = std::chrono::seconds(60ul * 60ul * 24ul * 365ul * 10ul);
    }

    for (const size_t strlen : strlens)
    {
        if (fuzz_one_byte)
        {
            if (f::FLAG_debug)
            {
                std::cout << "DEBUG adding 1-byte campaign for strlen " << std::dec << strlen << std::endl;
            }

            if (!make_campaign<uint8_t>(context.work_ll, regexp, strlen, seeds, max_total))
            {
                return 0;
            }
        }

        if (fuzz_two_byte)
        {
            if (f::FLAG_debug)
            {
                std::cout << "DEBUG adding 2-byte campaign for strlen " << std::dec << strlen << std::endl;
            }

            if (!make_campaign<uint16_t>(context.work_ll, regexp, strlen, seeds, max_total))
            {
                return 0;
            }
        }
    }

    // count how many campaigns we have
    context.n_active_campaigns = 1;
    struct fuzz_campaign_ll *curr = context.work_ll;
    for (; curr->next != context.work_ll; curr = curr->next, context.n_active_campaigns++);

    if (f::FLAG_debug)
    {
        std::cout << "DEBUG We have " << std::dec << context.n_active_campaigns << " fuzz campaigns" << std::endl;
        std::cout << "DEBUG Baseline established. Proceeding to main work loop." << std::endl;
    }

    // More threads than campaigns is meaningless
    size_t threads_to_make = std::min(context.n_active_campaigns, static_cast<size_t>(n_threads));

    std::vector<std::thread *> work_threads;
    for (size_t i=0; i < threads_to_make; i++)
    {
        std::thread *t = new std::thread(do_work, &context);
        work_threads.push_back(t);
    }

    for (size_t i=0; i < work_threads.size(); i++)
    {
        work_threads[i]->join();
    }

    return 1;
}

}

}
