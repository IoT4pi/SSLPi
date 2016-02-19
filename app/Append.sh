#!/bin/sh

Param=$*

echo $Param >> TestFile
res=$?
#echo "$res"
if [ $res = "0" ]; then
	exit 0
else
	echo "Error" 1>&2
	exit 1
fi

