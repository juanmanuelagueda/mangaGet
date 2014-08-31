import threading
import time
import urllib2
import sys

FullLine = 1

def getUrl(url, retries=0):
    # Attempt getting the URL object, retry up to four times.
    while retries < 4:
      try:
        hold=urllib2.urlopen(url, timeout=20.0)
        return hold
      except Exception:
        retries+=1
        print url
        print 'Error opening the URL. Retrying(%d)...' % retries


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
 

def sigIntHandler(signal, frame):
    # Catch all the CTRL+C
    print '  SigInt Caught, Terminating...'
    sys.exit(0)


