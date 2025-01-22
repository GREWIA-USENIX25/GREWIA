import os
import psycopg2
import argparse
import random

parser = argparse.ArgumentParser()
parser.add_argument('--id', type=int, help='a single regexp id to add')
parser.add_argument('--all', action='store_true', help='add all regexps (WARNING: this is a lot)')
parser.add_argument('--some-vulns', type=int, metavar='NVULNS', help='randomly add this many vulnerable regexps to the queue')

args = parser.parse_args()


if args.id is not None:
    print('adding ID:', args.id)
    to_add = [args.id]
elif args.all:
    print('adding ALL regexps')
    to_add = set()

    # only base regexps get the modified version queued, so we need to know which are it
    base_regexps = set()
    with open(f'../../data/regexps.csv') as fin:
        for line in fin:
            if not line.strip() or line.startswith('#') or line.startswith('ID,'):
                continue
            splat = line.split(',')
            id_ = int(splat[0])
            to_add.add(id_)
            dataset = splat[1]
            #
            # NOTE: here you could decode the base64 regexp pattern (splat[2]) and see if it
            # contains the characters {, +, $, ^, or * -- if not, then it has no quantifiers
            # or assertions, which means it is trivially O(n) in Irregexp. For efficiency those
            # can be skipped.
            #

            for ds in ['corpus', 'regexlib', 'snort']:
                if ds in dataset:
                    base_regexps.add(id_)
    
    assert len(base_regexps) > 5000 # sanity

    # now that we know what is in base, add modified regexps as appropriate
    with open(f'../../data/modified_regexps.csv') as fin:
        for line in fin:
            if not line.strip() or line.startswith('#') or line.startswith('ID,'):
                continue
            id_ = int(line.split(',')[0])
            if id_ in base_regexps:
                to_add.add(id_)
    print(f'adding {len(to_add)} regexps to queue')
elif args.some_vulns:
    assert args.some_vulns > 0, 'must add positive count of vulnerable regexps'

    candidates = set()
    with open(f'../../data/regulator_results.csv') as fin:
        for line in fin:
            if not line.strip() or line.startswith('#') or line.startswith('regexp id,'):
                continue
            splat = line.strip().split(',')
            if len(splat) < 4:
                # no positive result anyway
                continue
            id_ = int(splat[0])
            validated = {'True': True, 'False': False}[splat[3]]

            if validated:
                candidates.add(id_)
    print(f'{len(candidates):,} candidate regexps; randomly sampling {args.some_vulns}')
    to_add = random.sample(candidates, args.some_vulns)
    assert len(to_add) == args.some_vulns
else:
    print('Must select one option (see --help)')
    exit(1)



db = psycopg2.connect(
    dbname='postgresdb',
    user='regulator',
    password='password',
    host='localhost',
)

db.autocommit = False

print('[*] connected to postgresql')

curr1 = db.cursor()

curr1.execute("""CREATE TABLE IF NOT EXISTS fuzz_work_queue (
	id SERIAL NOT NULL,
	ts_taken timestamp without time zone,
	regexp_id INTEGER NOT NULL,
	length INTEGER NOT NULL,
	char_width INTEGER NOT NULL,
	seed INTEGER NOT NULL,
	fuzz_time_sec INTEGER NOT NULL,
	ts_completed timestamp without time zone
)
""")

curr1.execute("""CREATE TABLE IF NOT EXISTS public.regexps_fuzz_results (
    id SERIAL NOT NULL,
    regexp_id integer NOT NULL,
    length integer NOT NULL,
    fuzz_time_sec integer NOT NULL,
    score integer,
    witness text,
    fail_reason text,
    char_width integer,
    seed integer,
    max_total_exceeded boolean,
    max_observations integer,
    created_at timestamp without time zone DEFAULT now(),
    fuzzer_version integer,
    fuzz_queue_id integer 
);
""")


curr1.execute("""CREATE TABLE IF NOT EXISTS public.regexps_guess_pump_from_fuzz3 (
    id serial NOT NULL,
    fuzz_result_id integer NOT NULL,
    inscount_version integer NOT NULL,
    pump_pos integer,
    pump_len integer,
    klass text NOT NULL,
    poly_deg integer,
    fail_reason text,
    pump_string bytea,
    time_pumping_secs double precision,
    classifier_version integer 
);
""")

curr1.execute("""CREATE TABLE IF NOT EXISTS regexps_guess_pump_length_results3 (
    id SERIAL NOT NULL,
    guess_pump_id integer NOT NULL,
    length_for_ten_s integer,
    fail_reason text,
    exceeded_max_pumps boolean,
    num_pumps integer 
)""")

for i, id_ in enumerate(to_add):
    if len(to_add) > 100:
        if i % 100 == 0:
            print(f'{i}/{len(to_add)}')

    curr1.execute("SELECT 1 FROM regexps WHERE id = %s", (id_,))
    if curr1.rowcount != 1:
        print('Could not find ID', id_)
        exit(1)

    FUZZ_SECONDS = 60 * 5 - 5
    curr1.execute("""
        INSERT INTO fuzz_work_queue (regexp_id, length, char_width, seed, fuzz_time_sec)
        VALUES (%s,%s,%s,%s,%s)
    """, (id_, 200, 1, 10, FUZZ_SECONDS))

db.commit()

print('[*] done')
