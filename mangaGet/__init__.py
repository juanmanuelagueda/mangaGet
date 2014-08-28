#!/usr/bin/python

"""
Author: DarkDragn
Date:   28Aug14 
"""


import os
import re
import sys
import time

import shutil
import urllib2
import zipfile

import optparse
import importlib
import threading

from os import path

ChapterHold = []
CompleteStatus = None
FullLine = 1
Mods = []

PervEden = 'http://www.perveden.com/en-manga'

def getPic(mod, series, chapter, page, picUrls,lastPage=1):
    
    # List of variables for this method
    pageName='%02d.jpg' % int(page)
    holdTime=time.localtime()
    retries=0
    curSize=0
    
    # Check to see if we have this page...
    if os.path.exists(os.path.realpath('./%s/%s/%s' %
                      (series, chapter, pageName))):
      return False
    
    if picUrls.__len__() == 0:
      picUrl = mod.getPicUrl(series, chapter, page, ChapterHold)
    else:
      picUrl = picUrls[page-1]

    # Check to see if the series/chapter folders exist. If not, make them
    if not os.path.exists(series):
      os.mkdir(series)
    if not os.path.exists('%s/%s' % (series, chapter)):
      os.mkdir(path.realpath('%s/%s' % (series, chapter)))
    
    up=getUrl(picUrl)
    meta=up.info()
    totalSize= meta.getheader('content-length')
    
    # Make a status entry for the log
    logFile=open(path.realpath('%s/%s/logFile' % (series, chapter)), 'a')
    logFile.write("File Number %02d/%02d  Current Time: %02d:%02d:%02d  " %
                  (int(page), int(lastPage), holdTime.tm_hour, 
                   holdTime.tm_min, holdTime.tm_sec))
    logFile.flush()
    
    # Run the file download, and verify file size
    while not curSize == int(totalSize):
      # Check to see if this is the first try
      if retries > 0:
        if retries > 4:
          logFile.write('Failed\n')
          logFile.close()
          return False
        
        # Delete the URL object, and headers
        up.close()
        del up, meta
        os.remove(path.realpath('%s/%s/%s' % (series, chapter, pageName)))
        print 'Something\'s wrong with the filesize. Retrying...'
        
        # Re-open the URL, re-grab the headers, and let the user know 
        #what happened
        up=getUrl(picUrl)
        meta=up.info()
        totalSize=meta.getheader('content-length')
      
      # Try, Except for any 404 errors or such
      try:
        with open(path.realpath('%s/%s/%s' % (series, chapter, pageName)), 'wb') as f:
          f.write(up.read())
          f.close()
        
        # Get final size, and increment retries counter
        curSize=os.path.getsize(path.realpath('%s/%s/%s' %
                                (series, chapter, pageName)))
        retries+=1
        
      except Exception:
        print 'Error while reading the pic from the URL. Retrying...'
        retries+=1
    
    # Close out the log... Did it work?
    logFile.write('Success!\n')
    logFile.close()


def getChap(series, chapter, mod):
    global FullLine
    global CompleteStatus
    
    # Piece together the name for the chapter
    if '.' in chapter:
      name=chapter.split('.')
      chapName='%03d.%s' % (int(name[0]), name[1])
    else:
      chapName='%03d' % (int(chapter))
    zipName='%s.cbz' % chapName
    
    # Give the user some kind of status...
    if os.path.exists(os.path.realpath('./%s/%s' % (series, zipName))):
      statusPrint('Chapter %s found!!!... ' % chapName)
      return False
    else:
      statusPrint('Starting on chapter %s... ' % chapName)
      if CompleteStatus == None:
        statusStarter='For today, as have the following to read!'
        CompleteStatus='%s\nDownloaded %s Chapter %s' % (statusStarter, 
                                                         series, chapter)
      else:
        CompleteStatus='%s\nDownloaded %s Chapter %s' % (CompleteStatus, 
                                                         series, chapter)
 
    
    # Check for which site we're using. Parse pages for site-specifiy ref.
    pageNums, finalPics = mod.getPages(series, chapter)

    # Loop for every Picture
    for i in range(1, pageNums+1):
        getPic(mod, series, chapter, i, finalPics, pageNums)
    
    # Zip our chapter up, and remove the temp folder.
    zipIt('./%s/%s' % (series, chapter), '%s/%s' % (series, zipName),
          chapter)
    shutil.rmtree(path.realpath('%s/%s' % (series, chapter)))
    

def getSeries(series, mod):
    global CompleteStatus
    global ChapterHold
    chaptrs = []
    holdTime=time.localtime()
    
    # Let the user know what's going on, then flush stdout.
    sys.stdout.write('Looking up the index page for %s...\n' % series)
    sys.stdout.flush()
    index = urllib2.urlopen('%s/%s' % (mod.site, series))
    
    timeRun='%02d%02d%02d' % (holdTime.tm_year, holdTime.tm_mon, 
                              holdTime.tm_mday)
    updateName='update.%s' % timeRun
    if os.path.exists(os.path.realpath(updateName)):
      CompleteStatus=' '
    
    # Enumerate the list of chapters for the series.
    while True:
      buffer = index.readline(8192)
      if not buffer:
        break
      
      # Perform a site-specific check, and parse.
      chap, chapHold = mod.parseChapters(buffer, series)
      
      if chap != '':
        chaptrs.append(chap)
      if chapHold != None:
        ChapterHold.append(chapHold)
    
    sys.stdout.write('Chapter index found... %d chapters to get.\n' %
                     len(chaptrs))
    sys.stdout.flush()
    
    # Compensate for len beginning at index value of 0. Start at the end of
    # list, and chop off the endline special character.
    for i in range(1, len(chaptrs)+1):
      chapter = str(chaptrs[len(chaptrs)-(i)]).rstrip('\n')
      while threading.activeCount() > 4:
        time.sleep(.25)
      thread = threading.Thread(target=getChap, args=(series, chapter, mod))
      thread.start()
      time.sleep(.05)
      
    # Wait for the last thread to finish
    thread.join()
    sys.stdout.write('Finished!!!... \nTook long enough, eh?\n')
    sys.stdout.flush()
    
    if not CompleteStatus == None:
      if not CompleteStatus == ' ':
        with open(updateName, 'ab') as f:
          f.write('%s\n' % CompleteStatus)
          f.flush()
          f.close()


def zipIt(path, name, top):
    # Walk an entire directory, recursively creating a zip.
    zip=zipfile.ZipFile(name, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(path):
      for file in files:
        zip.write(os.path.join(root, file), '%s/%s' % (top, file))
    zip.close()


def getUrl(url, retries=0):
    # Attempt getting the URL object, retry up to four times.
    while retries < 4:
      try:
        hold=urllib2.urlopen(url)
        return hold
      except Exception:
        print 'Error opening the URL. Retrying...'
        retries+=1
        print retries


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


def importer():
    modList = ['mangaGet.sites.%s' % re.sub(r'\.py', '', f) for f in os.listdir('%s/%s' % 
                (os.path.dirname(__file__), "sites")) if f.endswith('.py') and f != '__init__.py']
    for i in modList:
      Mods.append(importlib.import_module(i)) 


def sigIntHandler(signal, frame):
    # Catch all the CTRL+C
    print '  SigInt Caught, Terminating...'
    sys.exit(0)

   
importer()

