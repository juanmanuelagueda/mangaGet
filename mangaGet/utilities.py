import os
import sys
import threading
import time
import urllib2

FullLine = 1

def getUrl(url, series = '', retries=0, extras = None):
    # Attempt getting the URL object, retry up to four times.
    while retries < 4:
        try:
            opener = urllib2.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            hold=opener.open(url, timeout=20.0)
            return hold
        except Exception:
            retries+=1
            errMsg = 'Error opening the URL. Retrying(%d)...\n' % retries
            if extras != None:
                errExtra = ['Chapter: %s' % extra[0]]
                if extras[1] != None:
                    errExtra.append('Page: %s' % extras[1])
                errMsg = '; '.join(errExtra[:]) + errMsg
            errorWrite(errMsg, series)


def statusPrint(message):
    global FullLine
    if FullLine > 3:
      FullLine = 1
      sys.stdout.write('%s\n' % message)
      sys.stdout.flush()
    else:
      FullLine += 1
      sys.stdout.write(message)
      sys.stdout.flush()


def threadIt(meth, chaptrs, args):
    # Compensate for len beginning at index value of 0. Start at the end of
    # list, and chop off the endline special character.
    threads = []
    
    for i in range(1, len(chaptrs)+1):
      chapter = str(chaptrs[len(chaptrs)-(i)]).rstrip('\n')
      while threading.activeCount() > 4:
        time.sleep(.25)
      threads.append(threading.Thread(target=meth, args=(args[0], chapter, args[1])))
      threads[-1].daemon = True
      threads[-1].start()
      time.sleep(.05)
      
    # Wait for the last thread to finish
    for i in threads:
      if i.isAlive:
        i.join()
    sys.stdout.write('Finished!!!... \nTook long enough, eh?\n')
    sys.stdout.flush()


def safeRead(urlHold, series, chap = None):
    retries = 0
    while retries < 4:
      try:
        buff = urlHold.readline()
        return buff
      except Exception:
        retries += 1
        msg = 'Error reading from the url stream. (%s) Retrying(%d)...' % (str(chap), retries)
        errorWrite(msg, series)


def errorWrite(msg, series):
    with open(os.path.realpath('%s/logFile.err' % series), 'a') as logFileErr:
      logFileErr.write(msg)
      logFileErr.flush()
      logFileErr.close()

def sigIntHandler(signal, frame):
    # Catch all the CTRL+C
    sys.stdout.write( '  SigInt Caught, Terminating...\n')
    sys.exit(0)


