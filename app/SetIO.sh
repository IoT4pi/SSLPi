#!/bin/sh

python File_Write.py $1
res=$?
if [ $res = "0" ]; then
	exit 0
else
	echo "Error" 1>&2
	exit 1
fi

