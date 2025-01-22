cd /Evaluation
echo "--------------------Working on corpus_snort_regexlib_regex101_unique--------------------"
./Generate_test.sh Benchmarks/corpus_snort_regexlib_regex101_unique.txt
./Verify_test.sh Benchmarks/corpus_snort_regexlib_regex101_unique.txt
./DrawTablesAndGraphs_test.sh Benchmarks/corpus_snort_regexlib_regex101_unique.txt
echo "--------------------corpus_snort_regexlib_regex101_unique done--------------------"