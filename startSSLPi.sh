#!/bin/sh
HOME=/home/pi/SSLPi/
Script="SSLserverPi_V1_2.py"
NumParam=$#
echo $NumParam

if [ $NumParam = "0" ]; then
        cd $HOME
        Test=$HOME$Script
        echo "NO Parameter"
else
        #proof if path ende with /
        echo $1 | grep '/$' >> /dev/null
        if [ $? -eq 1 ];then
                echo "Missing / at the end of Path"
                Param=$1"/"
        else
                Param=$1
        fi 
        cd $Param
        Test=$Param$Script
        echo "ONE Parameter"
fi


echo "Test = " $Test
#pwd


sudo ps aux | grep python | grep $Test #>> /dev/null
! [ "$?" = "0" ] && sudo python $Test  >> SSLPi.log


