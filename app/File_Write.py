#! /usr/bin/env python
#
#Example to ad to a File
#
import os
import sys
#import subprocess

strParamTxt= sys.argv[1]
iReturn = 0



FilePath='Test.txt'

try:

    if os.path.exists(FilePath):
        file= open(FilePath,"a")
    else:
        file= open(FilePath,"w")


    a='hallo ', 'ein ', 'test'

    file.writelines("\nHallo this is my first Line\n")
    file.writelines("Now the second Line\n")
    file.writelines(a)
    file.writelines('\nParameter =' + strParamTxt)
    file.close()
    print 'Python Return = 0'
    iReturn = 0
except:
    print 'Python Return = 1'
    iReturn = 1
sys.exit(iReturn)
