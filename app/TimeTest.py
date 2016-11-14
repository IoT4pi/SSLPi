import sys
import os
import time
import random

output = sys.stdout #store original stdout object for later
while 1:
    Zahl1= random.randrange(0, 50, 1)
    Zahl2= random.randrange(0, 50, 1)
    strText= str(Zahl1)+ ";"+ str(Zahl2)+'\r'
    #print "Data :" +strText
    output.write("Data :" +strText)
    output.flush()
    #Timout
    time.sleep(10) #4 sec schlafen

#end while
