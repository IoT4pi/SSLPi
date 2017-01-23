#!/bin/sh
echo start Timer
python -u TimeTest.py
#sudo top | grep python >&1
#echo new scrpit
 
res=$?
if [ $res = "0" ]; then
        exit 0
else
        echo "Error" 1>&2
        exit 1
fi


