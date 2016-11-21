###############################################
#install script 
#--------------------------------------------
# Please do not change the code  
# except you know what you are doing.
# Configuration of installation is  
# interactive !
#
# Change the configuration if needed in the 
# SSLPy.cfg configuration file  
#####################################################
#  Copyright (C) 2016 
#  IoT4pi <office@iot4pi.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the Apache License Version 2.0 (APLv2)
#  as published by http://www.apache.org/licenses/LICENSE-2.0 .
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  This product includes software developed by the OpenSSL Project
#  for use in the OpenSSL Toolkit. (http://www.openssl.org/)
#
#####################################################
#!/bin/sh

clear
#########################
#default variables
DefaultInstallPath="/home/pi/SSLPi/"
DefaultCertPath=$DefaultInstallPath"Cert/"
DefaultAppPath=$DefaultInstallPath"app/"
currentDir=`pwd`
ServerScript="SSLserverPi_V1_3.py"




#echo "CurrentDir= "$currentDir
#######################
#functions 
#checks  and create dir if needed
checkDir () {
		echo "In function"	
        	#echo $1
		whichDir=$1
		echo $whichDir
		cd $whichDir  2> /dev/null
		#echo $?
		if ! [ $? -eq 0 ];then	
			echo "Directory doesn't exist ! It will be created!"		
			mkdir $whichDir 2> /dev/null
			if [ $? -eq 0 ];then
				echo "Directory created !"
			else
				echo "Directory could not be generated !"
				return 1
			fi
		fi
		return 0
	}  
#end functions

#############
echo "Testing required Software ..."
#test if needed software is installed
#first OpenSSL 
dpkg -l | grep -i openssl >> /dev/null
if [ $? -eq 0 ];then
	echo "openssl is installed !"
else	
	echo "openssl is not installed ! \n Please do install, then run this script again !"
	exit
fi
#######
#second python 2.7
dpkg -l | grep -i python2.7 >> /dev/null
if [ $? -eq 0 ];then
	echo "python2.7 is installed !"
else	
	echo "python2.7 is not installed ! \n Please do install, then run this script again !"
	exit
fi
########
#some specifications we need
########
#installation Path / Dir of Server
echo -n "Type path to install the SSL Server (default "$DefaultInstallPath") [ENTER]:"
read readInstallPath
#proof if readInstallPath is set
if [ -z "$readInstallPath" ]; then
	InstallPath=$DefaultInstallPath
else 
	#proof if path ende with /	
	echo $readInstallPath | grep "/$" >> /dev/null
	if [ $? -eq 1 ];then
		echo "Missing / at the end of Path"
		readInstallPath=$readInstallPath"/"
	fi

	InstallPath=$readInstallPath
fi
#call function checkDir
checkDir $InstallPath
if ! [ $? -eq 0 ];then
	echo "Exit install script"	
	exit
fi
echo "InstallPath ="$InstallPath
#############
#installation Path / Dir of Certificates
echo -n "Type path to install the Certificates (default "$DefaultCertPath") [ENTER]:"
read readCertPath
#proof if readCertPath is set
if [ -z "$readCertPath" ]; then
	CertPath=$DefaultCertPath
else
	#proof if path ende with /
	echo $readCertPath | grep "/$" >> /dev/null
	if [ $? -eq 1 ];then
		echo "Missing / at the end of Path"
		readCertPath=$readCertPath"/"
	fi 
	CertPath=$readCertPath
	
fi
#call function checkDir
checkDir $CertPath
if ! [ $? -eq 0 ];then
	echo "Exit install script"	
	exit
fi
echo "CertPath ="$CertPath


####################################################################
#Create the OpenSSL Certificates 
echo "Starting Certificate creation..."
#generate Certificates
openssl genrsa -des3 -out $CertPath"server.orig.key" 2048 
openssl rsa -in $CertPath"server.orig.key" -out $CertPath"server.key"
openssl req -new -key $CertPath"server.key" -out $CertPath"server.cer"
openssl x509 -req -days 365 -in $CertPath"server.cer" -signkey $CertPath"server.key" -out $CertPath"server.pem"
#########################################
#at this point all certificates should be stored in the Cert Path
#we now have to copy all needed files from the current file to the install Path
#needed files are: 
#		SSLPi.cfg		ConfigFile
#		startSSLPi.sh		Startup Script 
#		SSLserverPi_Vx.py	Python SSL Server
#               Directory app		Test Applications
####
#first test if install path the current path
#echo "CurrentDir= "$currentDir
#echo "install Path= "$InstallPath
testCurrDir=$currentDir"/"
#echo $testCurrDir
if [ "$testCurrDir"!="$InstallPath" ];then 
	echo "Start to copy to "$InstallPath
	cp $currentDir/SSLPi.cfg $InstallPath
	if ! [ $? -eq 0 ];then
		echo "Copy SSLPi.cfg faild"		
		echo "Exit install script"	
		exit
	fi

	cp $currentDir/startSSLPi.sh $InstallPath
	if ! [ $? -eq 0 ];then
		echo "Copy startSSLPi.sh faild"		
		echo "Exit install script"	
		exit
	fi

	cp $currentDir/$ServerScript $InstallPath
	if ! [ $? -eq 0 ];then
		echo "Copy "$ServerScript" faild"		
		echo "Exit install script"	
		exit
	fi

	cp -rf $currentDir/app $InstallPath
	if ! [ $? -eq 0 ];then
		echo "Copy Dir app faild"		
		echo "Exit install script"	
		exit
	fi
fi

echo "Making Scripts runnable "
#make startSSLPi.sh runnable
chmod +x $InstallPath/*.sh
if ! [ $? -eq 0 ];then
	echo "Making startSSLPi.sh runnable faild"		
	echo "Exit install script"	
	exit
fi
#make Scripts in dir app runnable
chmod +x $InstallPath/app/*.sh
if ! [ $? -eq 0 ];then
	echo "Making apps runnable faild"		
	echo "Exit install script"	
    exit
fi
#######################
#write install Path into startSSLPi.sh
grepResult=$(grep "^HOME=*" $InstallPath/startSSLPi.sh)
#echo $grepResult
sed -i s!$grepResult!HOME=$InstallPath! $InstallPath/startSSLPi.sh
if [ $? -eq 0 ];then
	echo "Install Path written to startSSLPi.sh" 
else
	echo "Install Path could not be written to startSSLPi.sh"
	echo "Exit install script"	
	exit 
fi

#######################
#write Cert Path SSLPi.cfg
grepResult=$(grep "^strPath:*" $InstallPath/SSLPi.cfg)
#echo $grepResult
sed -i s!$grepResult!strPath:$CertPath! $InstallPath/SSLPi.cfg
if [ $? -eq 0 ];then
	echo "Certificate Path written to SSLPi.cfg" 
else
	echo "Certificate Path could not be written to SSLPi.cfg"
	echo "Exit install script"	
	exit 
fi
#Change the app Dir in SSLPi.cfg
grepResult=$(grep ";"$DefaultAppPath $InstallPath/SSLPi.cfg)
#echo $grepResul 
if [ $? -eq 0 ];then
    echo "Change app dir in SSLPi.cfg"
    sed -i 's!;'"$DefaultAppPath"'!;'"$InstallPath"'app/!g' $InstallPath/SSLPi.cfg
    if [ $? -eq 0 ];then
	    echo "app Path written to SSLPi.cfg" 
    else
	    echo "app Path could not be written to SSLPi.cfg"
	    echo "Exit install script"	
	    exit 
    fi
fi




##############################
#now set up crontab, so that the server is running at 
#system start without user input
#using the easy way with cron/crotab

echo "Setting up cron...."
crontab -l > mycron
grepResult=$(crontab -l | grep "^@reboot" | grep $InstallPath"startSSLPi.sh")
echo $grepResult
if [ -z "$grepResult" ];then
	echo "No entry existing"
	echo "@reboot sudo "$InstallPath"startSSLPi.sh >> "$InstallPath"log 2>&1" >> mycron 
	crontab mycron
	echo "New cronjob added "
else
	echo "cornjon already exists"
	cronResult=$(cat mycron)
	echo $cronResult
fi
rm mycron
echo "You finally finished with success."
echo "Congratulations !"
echo "Now please change the SSLPi.cfg to your needs"
echo "After rebooting the systems it should be running"
echo "Best wishes, your IoT4pi team" 

