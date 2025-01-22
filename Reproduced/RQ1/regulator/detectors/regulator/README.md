# Regulator ReDoS detector


This is the prototype, bulk-processing version used for publication
in USENIX '22.

## Directories

Directory `fuzzer/` contains the C++ code and artifacts to build the core fuzzer; see `fuzzer/README.md` for more details and build instructions. A pre-built version is included.

Directory `extractor/` contains a small C++ wrapper around the irregexp compiler, which we use to pre-compile irregexp bytecode for the perffuzz evaluation.

## Running

This prototype is broken into three bulk-processing stages. Intermediate results are stored in postgresql. So, before running, ensure postgresql is up: `service postgresql start`. If not using the docker container, ensure that the database 'postgresdb' exists, that the user 'regulator' (password: 'password') has access, and you likely want to run `db.sql` to add all the tables and regexps.


To load regexp(s) for fuzzing, call `python3 add_to_queue.py --id THE_ID`. See `../../data/regexps.csv` for IDs. You may want to check `../../data/regulator_results.csv` for some interesting regexps to re-run. Other options are `--all`, which enqueues all regexps, and `--some-vulns NVULNS`, which enqueues NVULNS known-vulnerable regexps from the paper's experiments, randomly sampled.

The fuzzing stage is next. Run `python3 fuzz_from_queue.py` to begin; by default this uses n-2 CPU threads, one per regexp, bound by `taskset` - change the exact cores used by passing `--cores=1,2,3`.

The pumping stage is next. This will attempt to classify witnesses as super-linear. Run `python3 pump_all.py`. This accepts `--cores` as above.

The dynamic validator is next. This will first determine if 10 seconds of slow-down is possible within a 1m character budget. Then, it will binary-search for the exact length where this regexp exceeds 10 seconds of slow-down. Run `python3 binsearch_pump.py`.

Dump the results with `python3 dump_results.py > regulator_results.csv`. Copy this to `/data/regulator_results.csv` to run analysis against new results. A description of the columns is detailed in the `/data/regulator_results.csv` file that comes in this artifcat.

## Other files

`time_exec.js` is a utility called by `binsearch_pump.py` for real, wall-clock timings of the irregexp engine matching against a given witness string.

`coverage_fuzzer` is the regulator fuzzer built to emit coverage information periodically; we use this to plot coverage information over time
