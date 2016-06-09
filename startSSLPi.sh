#!/bin/sh
HOME=

NumParam=$#
echo $NumParam

if [ $NumParam = "0" ]; then
	cd $HOME
        Test=$HOME"SSLserverPi_V1.py"
        echo "NO Parameter"
else
	#proof if path ende with /
	echo $1 | grep '\>/' >> /dev/null
	if [ $? -eq 0 ];then
		echo "Missing / at the end of Path"
		Param=$1"/"
	else
		Param=$1
	fi 
        cd $Param
        Test=$Param"SSLserverPi_V1.py"
        echo "ONE Parameter"
fi


echo "Test = " $Test
pwd

sudo ps aux | grep python | grep $Test >> /dev/null
! [ "$?" = "0" ] && sudo python $Test  >> SSLPi.log
