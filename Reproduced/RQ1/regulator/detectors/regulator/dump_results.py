import psycopg2
import ast
import base64

db = psycopg2.connect(
    dbname='postgresdb',
    user='regulator',
    password='password',
    host='localhost',
)

curr = db.cursor()

def decode_witness_one_byte(s: str) -> bytes:
    s = s.replace("'", "\\'")
    s = ast.literal_eval("b'" + s + "'")
    return s
def decode_witness_two_byte(s: str) -> bytes:
    b = b''
    i = 0
    while i < len(s):
        c = s[i]
        if c == '\\' and s[i+1] == 'u':
            b1 = int(s[i+2:i+4], 16)
            b2 = int(s[i+4:i+6], 16)
            # load as little-endian
            b += bytes([b2, b1])
            i += 6
        elif c == '\\' and s[i+1] == '\\':
            b += bytes([ord('\\'), 0])
            i += 2
        elif c == '\\' and s[i+1] == 'r':
            b += bytes([ord('\r'), 0])
            i += 2
        elif c == '\\' and s[i+1] == 't':
            b += bytes([ord('\t'), 0])
            i += 2
        elif c == '\\' and s[i+1] == 'n':
            b += bytes([ord('\t'), 0])
            i += 2
        else:
            assert  ' ' <= c <= '~'
            b += bytes([ord(c), 0])
            i += 1
    return b

# all of the results from fuzzing
curr.execute(
    """
    SELECT regexp_id, rfr.id, rfr.witness, char_width, fail_reason
    FROM regexps_fuzz_results rfr
    JOIN regexps r ON rfr.regexp_id = r.id
    WHERE rfr.length = 200 AND
        fuzzer_version = 6
    """
)

def print_row(stuff):
    print(','.join(str(x) for x in stuff))

curr2 = db.cursor()
for regexp_id, rfr_id, witness, char_width, fail_reason in curr:
    if fail_reason == 'nonzero return(15)':
        # syntax error as well
        print_row([regexp_id, 'SYNTAX ERROR'])
        continue

    if witness is None:
        if fail_reason is None:
            print('ignoring broken fuzz result', rfr_id)
            continue
        if not 'timeout' in fail_reason:
            import pdb; pdb.set_trace()
        witness = 'a' * 200
    # encode the witness
    # TODO do this properly
    if char_width == 2:
        witness = decode_witness_two_byte(witness)
        b64witness = 'utf16le:' + base64.b64encode(witness).decode('ascii')
    else:
        assert char_width == 1
        witness = decode_witness_one_byte(witness)
        b64witness = 'latin1:' + base64.b64encode(witness).decode('ascii')

    if fail_reason is not None and 'timeout' in fail_reason:
        print_row([regexp_id, 'EXPONENTIAL(hung_fuzzer)', b64witness, True])
        continue

    curr2.execute(
        """
        SELECT id, klass
        FROM regexps_guess_pump_from_fuzz3
        WHERE classifier_version = 2
            AND fuzz_result_id = %s
        """,
        (rfr_id,)
    )
    pump_ids = curr2.fetchall()

    # if this fuzz result was not pumped, class it as UNKNOWN and move on
    if len(pump_ids) == 0:
        print_row([regexp_id, 'UNKNOWN', b64witness])
        continue

    assert len(pump_ids) > 0

    worst_pump_id, worst_pump_klass = pump_ids[0]
    for pump_id, klass in pump_ids[1:]:
        if klass == 'UNKNOWN':
            continue
        elif klass.startswith('EXPONENTIAL'):
            worst_pump_id = pump_id
            worst_pump_klass = klass
        elif klass == 'POLYNOMIAL':
            if worst_pump_klass == 'UNKNOWN':
                worst_pump_id = pump_id
                worst_pump_klass = klass
        else:
            raise NotImplementedError('unexpected')

    # if this is unknown class, just write that
    if worst_pump_klass == 'UNKNOWN':
        print_row([regexp_id, 'UNKNOWN', b64witness])
        continue

    # if this is baseline_fail, then it is known 10s slow-down; just say it validated
    if worst_pump_klass == 'EXPONENTIAL(baseline_fail)':
        print_row([regexp_id, worst_pump_klass, b64witness, True])
        continue

    # get the prefix, pump, suffix, length to  10s
    assert worst_pump_id is not None
    curr2.execute(
        """
        SELECT pump_pos, pump_len, bool_or(not gpl.exceeded_max_pumps), min(gpl.length_for_ten_s)
        FROM regexps_guess_pump_from_fuzz3 rgp
        JOIN regexps_guess_pump_length_results3 gpl ON gpl.guess_pump_id = rgp.id
        WHERE rgp.id = %s
        GROUP BY pump_pos, pump_len
        """,
        (worst_pump_id,)
    )
    pump_pos, pump_len, validated, len_for_10s = curr2.fetchone()

    prefix = witness[:pump_pos * char_width]
    pump = witness[pump_pos * char_width :(pump_pos + pump_len) * char_width]
    suffix = witness[(pump_pos + pump_len) * char_width:]

    b64prefix = base64.b64encode(prefix).decode('ascii')
    b64pump = base64.b64encode(pump).decode('ascii')
    b64suffix = base64.b64encode(suffix).decode('ascii')

    print_row([regexp_id, worst_pump_klass, b64witness, validated, b64prefix, b64pump, b64suffix, len_for_10s])
