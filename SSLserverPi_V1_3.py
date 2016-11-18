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

# ! /usr/bin/env python
import socket
import sys
import os

# import thread

import random
import subprocess
from subprocess import PIPE, Popen
from Queue import Queue, Empty

import threading
from threading import Thread

import time
import datetime
# import copy
from ConfigParser import SafeConfigParser

try:
    import ssl
except ImportError:
    print 'Error importing SSL !!!'
    sys.exit()

##########################
# Config variables
bUseConfig = True
strConfig = 'SSLPi.cfg'
iPort = 10023
strHost = ''
strPath = ''
strCert = 'server.pem'
strKey = 'server.key'
strEndStat = 'EndCom'
bDebug = True
bDetailError = True
cmdList = []  # storage of all commands
cmdParam = []  # list of just the commands that can come with parameter
maxThreads = 10


#####################

###############################
# Class for Running the Command asynchron
# this will work only reading what the Server is sending
# there is only limeted why to send Data from client tothe server
class myThread(threading.Thread, ):
    BUFSIZE = 1024

    def __init__(self, connstream, cmd):
        threading.Thread.__init__(self)
        self.connstream = connstream
        # self.stdout = None
        # self.stderr = None
        self.cmd = cmd
        self.isrunning = True
        self.PID = None

    def run(self):
        print "Starting asynchrone Thread with Command " + self.cmd

        p = Popen([self.cmd], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
        if bDebug:
            print getTime() + ": PID of Thread = " + str(p.pid)

        # wrap p.stdout with a NonBlockingStreamReader object:
        nbsr = NonBlockingStreamReader(p.stdout)

        # get the output
        strTemp = ''
        while self.isrunning:
            output = nbsr.readline(0.1)
            # 0.1 secs to let the shell output the result
            if not output:
                if strTemp != '':
                    # print strTemp
                    try:
                        self.connstream.write(strTemp)
                    except:
                        if bDebug:
                            print getTime() + ": Connection was destroyed by Client!"
                            print getTime() + ": PID = " + str(os.getpid())
                            print getTime() + ": Group PID = " + str(os.getpgid(os.getpid()))
                        # p.kill() stops subprocess
                        p.kill()
                        self.isrunning = False
                        break
                    strTemp = ''
                continue
            else:
                strTemp = strTemp + output
        nbsr.stop()
        return
        # Get lock to synchronize threads
        # threadLock.acquire()

    def stop(self):
        self.isrunning = False
        print getTime() + ": Stopping " + self.name + ' sent !'


####End Class

######################
# Helper Class for non blocking
# reading from a subprocess output stream
class NonBlockingStreamReader:
    def __init__(self, stream):
        '''
        stream: the stream to read from.
                Usually a process' stdout or stderr.
        '''
        # self._t = None
        self._s = stream
        self._q = Queue()
        self._isrunning = True

        def _populateQueue(stream, queue):
            '''
            Collect lines from 'stream' and put them in 'quque'.
            '''
            while self._isrunning:
                # readline doesn't work
                # line = stream.readline()
                line = stream.read(1)
                if line:
                    queue.put(line, False)
                    # print 'Add Line to Queue...' + line
                else:
                    print getTime() + ': UnexpectedEndOfStream !!!'
                    raise UnexpectedEndOfStream
            if bDebug:
                print getTime() + ": populate Queue Ended !"
            return

        self._t = Thread(target=_populateQueue,
                         args=(self._s, self._q))
        self._t.daemon = True
        self._t.start()  # start collecting lines from the stream

    def readline(self, timeout=None):
        # print 'in readline..'
        try:
            return self._q.get(block=timeout is not None, timeout=timeout)
        except Empty:
            return None

    def stop(self):
        self._isrunning = False
        if bDebug:
            print getTime() + ": Stopping NonBlockingStreamReader !"


class UnexpectedEndOfStream(Exception): pass


###End Helper Class



#######################################
# Helper function
# Function to get present Time as String
def getTime():
    ts = time.time()
    strTime = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return strTime


###### End Function

#########################################
# Function reading and parsing Config File
def ReadInConfig():
    # store in global Variables
    # therefore call explicit the global Keyword
    global bDebug
    global iPort
    global strHost
    global strPath
    global strCert
    global strKey
    global strEndStat
    global cmdList
    global cmdParam
    global bDetailError
    # open parser file
    config = SafeConfigParser()

    try:
        config.read(strPath + strConfig)
    except:
        if bDebug:
            print getTime() + ": Error open config file !"
        return False

    ################
    # parse SETUP Variales
    try:
        if (config.get("SETUP", "bDebug") == 'True'):
            bDebug = True
        else:
            bDebug = False
        if (config.get("SETUP", "bDetailError") == 'True'):
            bDetailError = True
        else:
            bDetailError = False
        iPort = int(config.get("SETUP", "iPort"))
        strHost = config.get("SETUP", "strHost")
        strPath = config.get("SETUP", "strPath")
        # if strPath not set we assume
        # Cert Files are in the working Dir
        if strPath == '':
            strPath = os.getcwd() + '/'
        strCert = config.get("SETUP", "strCert")
        strKey = config.get("SETUP", "strKey")
        strEndStat = config.get("SETUP", "strEndStat")
        if bDebug:
            print getTime() + ": strConfig = " + strConfig
            print getTime() + ": iPort = " + str(iPort)
            print getTime() + ": strHost = " + strHost
            print getTime() + ": strPath = " + strPath
            print getTime() + ": strCert= " + strCert
            print getTime() + ": strKey= " + strKey
            print getTime() + ": strEndStat= " + strEndStat
            print getTime() + ": bDebug = " + str(bDebug)
            print getTime() + ": bDetailError = " + str(bDetailError)
    except:
        if bDebug:
            print getTime() + ": Error reading SETUP Variable from Config File !"
        return False

    ###################################
    # Read in the commands
    lSections = config.sections()
    if bDebug:
        print 'Sections = '
        print  lSections
    # Loop through Sections
    for section in lSections:
        if (section == 'APP_CALLS'):
            # store Section APP_CALLS in lCommads List
            lComands = config.options(section)
            # read every line of the lCommads List
            for line in lComands:
                resLine = config.get(section, line)
                # split the line with sperator ;
                LineParts = resLine.split(";")
                # store all commands in List
                cmdList.append(LineParts)
                if bDebug:
                    print 'Seperated Commandline ='
                    print LineParts
                # if there is CommandIn which comes with parameter
                # store it in the cmdParam List
                if (LineParts[4] == '4') or (LineParts[4] == '5') or (LineParts[4] == '6'):
                    print 'Found Parameter command with ' + LineParts[0]
                    # but first proof if it isnot already in there
                    if LineParts[0] not in cmdParam:
                        cmdParam.append(LineParts[0])
    return True


###### End Function

#########################################
# Function Processing the commands
#   Test Command					-- Value 0
#   Change Dir 						-- Value 1
#   Command without a return (like rm ) 		-- Value 2
#   Command with return (like ls or pwd)		-- Value 3
#
#   Command In comes with parameters, with return	-- Value 4
#   Command In comes with parameters, without return	-- Value 5
#   Command In for Change Dir				-- Value 6
########################################################################
#   Run Command asynchron (as a Service)    -- Value 7
#
# Function returns a Truple, iReturn as Integer with Internal(-3), Sucess (1), undefined (-2) or Error (0) and
# the String which can be either an Error description or the System feedback
#
def processCommand(connstream, cmdList, strParam=''):
    iReturn = -3
    strReturn = ''
    for cmdLine in cmdList:
        # print '++++++++++++++++++++'
        # print cmdLine
        ###########
        # TestCommand
        if cmdLine[4] == '0':
            if bDebug:
                print getTime() + ': ' + cmdLine[0] + ' Test Command'
            iReturn = 1
            strReturn = strReturn + "Test message fom SSL server\r\n"
        #########
        # chDir
        elif cmdLine[4] == '1':
            if bDebug:
                print getTime() + ': ' + cmdLine[0] + ' Change Dir'
            try:
                # change Dir returns None in any case
                # if it fails there will be an exception
                os.chdir(cmdLine[6])
                iReturn = 1
            except:
                if bDebug:
                    print getTime() + ': ' + cmdLine[0] + ' Change Dir did not work'
                iReturn = 0
                strReturn = strReturn + cmdLine[0] + ' Change Dir did not work\r\n'
        ################
        # Command without a return
        elif cmdLine[4] == '2':
            if bDebug:
                print getTime() + ': ' + cmdLine[0] + ' Command without a return'
                # print 'CommandIn ' +cmdLine[0]
                # print 'Command ' +cmdLine[3]
                # print 'Parameter ' +cmdLine[6]
                # print 'Return ' +cmdLine[5]
            try:
                strTemReturn = subprocess.call([cmdLine[3], cmdLine[6]])
                # proof for success
                if strTemReturn == int(cmdLine[5]):
                    iReturn = 1
                else:
                    if bDebug:
                        print getTime() + ': ' + cmdLine[0] + ' ' + cmdLine[3] + ' did not work\r\n'
                    iReturn = 0
                    strReturn = strReturn + cmdLine[0] + ' ' + cmdLine[3] + ' did not work\r\n'
            except:
                if bDebug:
                    print getTime() + ': ' + cmdLine[0] + ' ' + cmdLine[3] + ' did not work\r\n'
                iReturn = 0
                strReturn = strReturn + cmdLine[0] + ' ' + cmdLine[3] + ' did not work\r\n'
        #############
        # Command with return
        elif cmdLine[4] == '3':
            if bDebug:
                print getTime() + ': ' + cmdLine[0] + ' Command with return'
                # print cmdLine[0]
                # print cmdLine[6]
            try:
                # proof if there has to be an argument to be included
                if (len(cmdLine) < 7) or (cmdLine[6] == ''):
                    strTempReturn = subprocess.check_output([cmdLine[3]])
                else:
                    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    # The application could be extended reading more the
                    # then one argument.
                    # Therefore I would change passing a List of arguments instead of
                    # the individual arguments.
                    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    strTempReturn = subprocess.check_output([cmdLine[3], cmdLine[6]])
                iReturn = 1
                strReturn = strReturn + strTempReturn + '\r\n'
            except:
                if bDebug:
                    print getTime() + ': ' + cmdLine[0] + ' ' + cmdLine[3] + ' Command with return did not work'
                iReturn = 0
                strReturn = strReturn + cmdLine[0] + ' ' + cmdLine[3] + ' Command with return did not work\r\n'
        #########
        # CommandIn comes with parameters, with return
        elif cmdLine[4] == '4':
            if bDebug:
                print getTime() + ': ' + cmdLine[0] + ' Command In comes with parameters, with return'

            try:

                # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                # The application could be extended reading more the
                # then one argument.
                # Therefore I would change passing a List of arguments instead of
                # the individual argument strParam.
                # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                strTempReturn = subprocess.check_output([cmdLine[3], strParam.strip()])
                iReturn = 1
                strReturn = strReturn + strTempReturn + '\r\n'
            except:
                if bDebug:
                    print getTime() + ': ' + cmdLine[0] + ' ' + cmdLine[3] + ' Command In with return did not work'
                iReturn = 0
                trReturn = strReturn + cmdLine[0] + ' ' + cmdLine[3] + ' Command In with return did not work\r\n'

        ########
        # CommandIn comes with parameters, without return
        elif cmdLine[4] == '5':
            if bDebug:
                print getTime() + ': ' + cmdLine[0] + ' Command In comes with parameters, without return'
            try:
                strTemReturn = subprocess.call([cmdLine[3], strParam.strip()])
                # print 'Return of CommandIn ='
                # print 'strTemReturn = ' + str(strTemReturn)
                # print 'cmdLine[5] =' + cmdLine[5]
                # proof for success
                if strTemReturn == int(cmdLine[5]):
                    iReturn = 1
                else:
                    if bDebug:
                        print getTime() + ': ' + cmdLine[0] + ' ' + cmdLine[3] + ' did not work\r\n'
                    iReturn = 0
                    strReturn = strReturn + cmdLine[0] + ' ' + cmdLine[3] + ' did not work\r\n'
            except:
                if bDebug:
                    print getTime() + ': ' + cmdLine[0] + ' ' + cmdLine[3] + ' did not work\r\n'
                iReturn = 0
                strReturn = strReturn + cmdLine[0] + ' ' + cmdLine[3] + ' did not work\r\n'
                ########
        # CommandIn for Change Directory chdir
        elif cmdLine[4] == '6':
            if bDebug:
                print getTime() + ': ' + cmdLine[0] + ' Command In for Change Dir'
            try:
                # change Dir returns None in any case
                # if it fails there will be an exception
                os.chdir(strParam.strip())
                iReturn = 1
            except:
                if bDebug:
                    print getTime() + ': ' + cmdLine[0] + ' Command In for Change Dir did not work'
                iReturn = 0
                strReturn = strReturn + cmdLine[0] + ' Command In for Change Dir did not work\r\n'
                ##################################
        ########
        # Run Command asynchron (as a Service)
        elif cmdLine[4] == '7':
            if bDebug:
                print getTime() + ': ' + cmdLine[0] + ' Run Command asynchron'
            ########
            # Create new threads
            thread1 = myThread(connstream, cmdLine[3])
            print getTime() + ': threat should be created'
            # Start new Threads
            thread1.start()
            # thread1.join()
            print getTime() + ': Main thread again ...'
            # print thread1.stdout


        ##############################

        #############
        # Command Type not defined
        else:
            if bDebug:
                print getTime() + ': ' + cmdLine[0] + ' Command Type not defined'
            iReturn = -2
        # !!!!!!!!
        # Stop Loop and exit function
        # if it has not been successful
        if iReturn != 1:
            break

    return (iReturn, strReturn)


###### End Function

#########################################
# Function for implementing own code
# return codes
#   -2   Command not Found
#   -1   Client ends communication
#    0   Error occoured
#    1   Success
#    2   unknown
#
def Proceed_func(fromaddr, data, connstream):
    # will hold the relevant commands
    passCommand = []
    # holds parameter if there will be one
    strSecond = ''
    strFirst = ''
    if bDebug:
        print getTime() + " :from IP :" + str(fromaddr), data
    # proof if Client end communication
    if (data == strEndStat):
        print getTime() + ': Client quits'
        return -1
    # is the received message one with Parameter ?
    for strParam in cmdParam:
        if (data.startswith(strParam)):
            # if yes extract Parameter
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # The application could be extended reading more the
            # then one argument.
            # Therefore I would change passing a List of arguments instead of
            # the variable strSecond.
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            strSecond = data[len(strParam):]
            strFirst = strParam

            if bDebug:
                print getTime() + ': ' + data + ' is in cmdParam'
                print getTime() + ': Parameter = ' + strSecond
                print getTime() + ': Command = ' + strFirst
            # if there are no Parameter leave the
            # function withh erorr message
            if len(strSecond.strip()) < 1:
                if bDebug:
                    print getTime() + ': ' + data + ' is in cmdParam with missing Parameter : ERROR'
                connstream.write('ERROR\r\n' + data + ' is in cmdParam with missing Parameter' + '\r\n')
                return 0
            # now run through command List to
            # do the sequence
            for strComandLine in cmdList:
                if (strFirst == strComandLine[0]):
                    # print strComandLine
                    passCommand.append(strComandLine)

    # is the received Message one without Parameter ?
    # print '#####################'
    for strComandLine in cmdList:
        if (data == strComandLine[0]):
            # print strComandLine
            passCommand.append(strComandLine)

    # If message is relevant, process the commands
    if not passCommand:
        return -2
    else:
        iCode, strBack = processCommand(connstream, passCommand, strSecond)
        # print 'return Code = ' + str(iCode)
        # print 'return String = ' + strBack
        # SUCCESS
        if (iCode == 1):
            if strBack != '':
                connstream.write('OK\r\n' + strBack)
            else:
                connstream.write('OK\r\n')
            return 1
        # ERROR
        elif (iCode == 0):
            if bDetailError == True:
                connstream.write('ERROR\r\n' + strBack)
            else:
                connstream.write('ERROR\r\n')
            return 0

    return 2


###### End function



###############################
# Socket Thread
# TODO:
#     1)by terminating the Thread there also has to be terminated the TCP Socket !!
#
# Creation of Threading Lock
threadLock = threading.Lock()


class mySSLThread(threading.Thread, ):
    def __init__(self, threadID, newsocket, ip, port, context):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.Mysocket = newsocket
        self.ip = ip
        self.port = port
        self.isrunning = True
        self.context = context

    def run(self):
        if bDebug:
            print getTime() + ": Starting Thread No " + str(self.threadID)

        try:
            # Timout to give time to setup
            time.sleep(2)
            connstream = None
            iLoop = 1
            if bDebug:
                print getTime() + ': certfile = ' + strPath + strCert
                print  getTime() + ': keyfile = ' + strPath + strKey
                print  getTime() + ': Working Dir = ' + os.getcwd()

            connstream = self.context.wrap_socket(self.Mysocket, server_side=True)
            ##Code form Version Python 2.7.3
            # establish a SSL Socket with client
            # connstream = ssl.wrap_socket(self.Mysocket,
            #                              server_side=True,
            #                              certfile=strPath + strCert,
            #                              keyfile=strPath + strKey)

            if bDebug:
                print getTime() + ': Thread: Accepted SSL connection to address ' + self.ip + ":" + str(
                    self.port) + "\n"
        except ssl.SSLError, msg:
            if bDebug:
                print getTime() + ': ERROR Thread: Error. SSLError in Thread : ', msg[1]
                if connstream != None:
                    print getTime() + ': ERROR SSLsocket could be created !'
                else:
                    print getTime() + ': ERROR SSLsocket is NULL !'
            iLoop = 0

        # Loop for receiving the messages from the client
        iReturn = 0
        while iLoop:

            data = connstream.recv(1280)

            if not data:
                continue
            else:
                # Block Threads
                threadLock.acquire()
                iReturn = Proceed_func((self.ip, self.port), data, connstream)
                # Release Threads
                threadLock.release()
                if bDebug:
                    print getTime() + ': iReturn = ' + str(iReturn)
                ###############
                # handling feedback from the message
                # get of loop, if client quits
                if (iReturn == -1):
                    connstream.write('Goobye\r')
                    break
                # Message could not be found
                if (iReturn == -2):
                    connstream.write('Message is not a Command\r')
                # Sucess
                elif (iReturn == 1):
                    pass
                # ERROR
                elif (iReturn == 0):
                    pass
                else:
                    connstream.write('unknown\r')

        if connstream != None:
            # houskeeping, clean up SSL socket
            connstream.shutdown(socket.SHUT_RDWR)
            connstream.close()

        self.stop()

    def stop(self):
        self.Mysocket.close()
        if bDebug:
            print getTime() + ':Thread: Goodbye !'
        self.isrunning = False
        if bDebug:
            print getTime() + ": Stopping Thread No " + str(self.threadID)
            # def __del__(self):
            # print "Stopping " + self.name


###### End Thread

###############################################
# main() Function
def main():
    err = 0
    msg = None
    ThreadNum = 1  # threadCounter
    Threads = []  # ThredsList

    #######
    # Read in the Config if set
    if bUseConfig:
        if (ReadInConfig() == False):
            if bDebug:
                print getTime() + ": Error reading Config; Server quits"
            err = 1
    ####################
    # proof if certificates are availible
    if os.path.exists(strPath + strCert):
        if bDebug:
            print getTime() + ': certificate file could be loaded'
    else:
        if bDebug:
            print getTime() + ': certificate file does not exist'
        err = 1

    ##New Code with Version Python 2.7.9
    # it is recommended to use PROTOCOL_SSLv23 as the protocol version
    # and then disable SSLv2 and SSLv3 explicitly using the SSLContext.options attribute
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.options |= ssl.OP_NO_SSLv2
    context.options |= ssl.OP_NO_SSLv3
    context.load_cert_chain(certfile=strPath + strCert, keyfile=strPath + strKey)


    # establish a TCP socket
    # bindsocket = socket.socket()
    bindsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bindsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        bindsocket.bind((strHost, iPort))
    except socket.error, msg:
        if bDebug:
            print getTime() + ": Bind failed in server: " + str(msg[0]) + " Message " + msg[1]
        err = 1

    # loop , waiting for a TCP Connection and making a client thread if there is a connection
    while (err == 0):

        try:
            try:
                bindsocket.listen(4)
            except socket.error, msg:
                if bDebug:
                    print getTime() + ": Listen failed: " + str(msg[0]) + " Message " + msg[1]
                err = 1
            if bDebug:
                print getTime() + ":Server is listening for connections\n"
            (newsocket, (ip, port)) = bindsocket.accept()
            if bDebug:
                print getTime() + ":Accepted client connection to address " + ip + ":" + str(port) + "\n"

            # start a new thread with TCP connection
            # thread.start_new_thread(deal_with_client,(newsocket, fromaddr))
            ########
            # Create new threads
            if maxThreads >= threading.activeCount():
                thread1 = mySSLThread(ThreadNum, newsocket, ip, port, context)
                Threads.append(thread1)

                if bDebug:
                    print getTime() + ":Threat No. " + str(ThreadNum) + " should be created \n"
                    print getTime() + ': Number of Threads = ' + str(threading.activeCount())
                # Start new Threads
                thread1.start()
                ThreadNum = ThreadNum + 1
            else:
                if bDebug:
                    print getTime() + ': Number of Threads exceeded ! Sorry!'
        except ssl.SSLError:
            if bDebug:
                print getTime() + ': Error: ssl.SSLError!'
            err = 1
        except:
            if bDebug:
                print getTime() + ": Unexpected error in While:", sys.exc_info()[0]
            err = 1
    # housekeeping, close TCP socket
    bindsocket.close()


###### End main()function

#######################
main()
#######################