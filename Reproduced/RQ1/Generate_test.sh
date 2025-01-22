if [ $# -gt 0 ]; then
    filename=$1
    echo "You selected $filename"
else
    echo "Please select the test data file:"
    i=0
    for file in `ls Benchmarks/*.txt`
    do
        i=$(($i+1))
        echo $i $file
    done
    read num
    i=0
    for file in `ls Benchmarks/*.txt`
    do
        i=$(($i+1))
        if [ $i = $num ]; then
            filename=$file
            echo "You selected $filename"
        fi
    done
fi

cd /Evaluation

echo "make regexes for each tool"
rm -rf /Evaluation/Results/
mkdir Results
rm -rf /Evaluation/regexes
python3 make_regexs.py $filename

echo "run each tool on the test data"

echo "--------------------GREWIA_INC start--------------------"
rm -rf /Evaluation/Results/GREWIA_INC
mkdir  /Evaluation/Results/GREWIA_INC
cd /Evaluation/GREWIA_INC
python3 Test.py
echo "--------------------GREWIA_INC end--------------------"

echo "--------------------GREWIA_DEC start--------------------"
rm -rf /Evaluation/Results/GREWIA_DEC
mkdir  /Evaluation/Results/GREWIA_DEC
cd /Evaluation/GREWIA_DEC
python3 Test.py
echo "--------------------GREWIA_DEC end--------------------"

echo "--------------------regulator start--------------------"
rm -rf /Evaluation/Results/regulator
cd /Evaluation/regulator/detectors/regulator
rm -rf /Evaluation/regulator/detectors/regulator/AttackString
mkdir /Evaluation/regulator/detectors/regulator/AttackString
python3 Test.py
mv /Evaluation/regulator/detectors/regulator/AttackString /Evaluation/Results/regulator
echo "--------------------regulator end--------------------"

# echo "--------------------rescue start--------------------"
# rm -rf /Evaluation/Results/rescue
# cd /Evaluation/rescue/test
# rm -rf /Evaluation/rescue/ReScue_attackstring
# mkdir /Evaluation/rescue/ReScue_attackstring
# cp /Evaluation/$filename /Evaluation/rescue/test/data/test.txt
# python3 batchtester.py -a -reg test.txt
# mv /Evaluation/rescue/ReScue_attackstring /Evaluation/Results/rescue
# echo "--------------------rescue end--------------------"

echo "--------------------rescue2 start--------------------"
rm -rf /Evaluation/Results/rescue
mkdir /Evaluation/Results/rescue
cd /Evaluation/rescue2/ReScue_jar
python3 Test.py
echo "--------------------rescue2 end--------------------"

echo "--------------------regexploit start--------------------"
rm -rf /Evaluation/Results/regexploit
rm -rf /Evaluation/regexploit/Regexploit_AttackString
mkdir /Evaluation/regexploit/Regexploit_AttackString
cd /Evaluation/regexploit
python3 Test.py
mv ./Regexploit_AttackString /Evaluation/Results/regexploit
echo "--------------------regexploit end--------------------"

echo "--------------------regexstatic start--------------------"
rm -rf /Evaluation/Results/regexstatic
cd /Evaluation/regexstatic
rm -rf ./AttackString
mkdir ./AttackString
python3 Test.py
mv ./AttackString /Evaluation/Results/regexstatic
echo "--------------------regexstatic end--------------------"

echo "--------------------redoshunter start--------------------"
rm -rf /Evaluation/Results/redoshunter
cd /Evaluation/redoshunter
python3 Test.py
mv ./AttackString /Evaluation/Results/redoshunter
echo "--------------------redoshunter end--------------------"

echo "--------------------rengar start--------------------"
rm -rf /Evaluation/Results/rengar
cd /Evaluation/Rengar
python3 Test.py
mv ./AttackString /Evaluation/Results/Rengar
echo "--------------------rengar end--------------------"
