#!/usr/bin/python

"""
Author: DarkDragn
Date:   23May14 
"""


import os
import re
import sys
import time

import shutil
import signal
import urllib2
import zipfile

import optparse
import threading

from os import path

ChapterHold = None
CompleteStatus = None
FullLine = 1


MangaEden = 'http://www.mangaeden.com/en-manga'
MangaPark = 'http://www.mangapark.com/manga'
PervEden = 'http://www.perveden.com/en-manga'

def getPic(site, series, chapter, page, lastPage=1, picUrl=None):
    
    # List of variables for this method
    pageName='%02d.jpg' % int(page)
    holdTime=time.localtime()
    retries=0
    curSize=0
    
    # Check to see if we have this page...
    if os.path.exists(os.path.realpath('./%s/%s/%s' %
                      (series, chapter, pageName))):
      return False
    
    if not picUrl:
      url='%s/%s/%s/%s' % (site,series,chapter,page)
      buf=getUrl(url)
      holdPic=''
      
      # Read the HTML, grabbing the line we need.
      while True:
        buffer=buf.readline(1024)
        if not buffer:
          break
        if 'mainImg' in buffer:
          holdPic=buffer
      
      # Parse the picture's URL from the page's HTML
      firstCut=re.sub('.*Img" src="', '', holdPic)
      picUrl='http:%s' % re.sub('" alt=.*', '', firstCut)
    
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


def getChap(series, chapter, site):
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
    if site == MangaEden or site == PervEden:
      holdPage=urllib2.urlopen('%s/%s/%s/1' % (site, series, chapter))
      
      # Read the html line by line, looking the the one we need.
      while True:
        buffer=holdPage.readline(8192)
        if not buffer:
          break
        if '<a class="selected"' in buffer:
          pageHold=buffer
      
      # Parse each page name from the line.
      pageNums=[]
      pageNums.append('1')
      for i in re.split('href="', pageHold):
        if 'en-manga' in i:
          if not 'Next' in i:
            firstCut=  re.sub('/en-manga/%s/%s/' %
                          (series, chapter), '', i)
            pageNums.append(re.sub('/">.*', '', firstCut))
      
      # Loop for every Picture.
      for i in pageNums:
        getPic(site, series, chapter, i, pageNums[-1])
    # The catch for mangaPark.
    elif site == MangaPark:
      holdPics=[]
      finalPics=[]
      chapterUrl=''
      
      # Check to see if ChapterHold alredy has what we need.
      if not ChapterHold:
        holdChap=urllib2.urlopen('%s/%s' % (site, series))
        
        while True:
          buffer=holdChap.readline(8192)
          if not buffer: 
            break
          if '/%s/s1/' % series in buffer:
            for splitIt in buffer.split('</a>'):
              if '/c%s/' % chapter in splitIt:
                if 'class' in splitIt:
                  firstCut=re.sub('.*manga', '', splitIt)
                  chapterUrl=re.sub('/1.*', '', firstCut)
      # If ChapterHold has what we need, just use it!
      else:
        for lines in ChapterHold:
          if '/%s/s1/' % series in lines:
            for splitIt in lines.split('</a>'):
              if '/c%s/' % chapter in splitIt:
                if 'class' in splitIt:
                  firstCut=re.sub('.*manga', '', splitIt)
                  chapterUrl=re.sub('/1.*', '', firstCut)
      
      # Once we have the chapter's URL, lets open it.
      holdPage=urllib2.urlopen('%s%s' % (site, chapterUrl))
      
      # Loop through the chapter's URL line by like, parsing the pics out.
      while True:
        buffer=holdPage.readline(8192)
        if not buffer:
          break
        if 'a target="_blank' in buffer:
          firstCut=re.sub('.*href..', '', buffer)
          finalPics.append(re.sub('" .*', '', firstCut))
      for i in range(0, len(finalPics)):
        getPic(site, series, chapter, i+1, len(finalPics), finalPics[i])
      
    # Zip our chapter up, and remove the temp folder.
    zipIt('./%s/%s' % (series, chapter), '%s/%s' % (series, zipName),
          chapter)
    shutil.rmtree(path.realpath('%s/%s' % (series, chapter)))
    

def getSeries(series, site):
    global CompleteStatus
    chaptrs = []
    holdTime=time.localtime()
    
    # Let the user know what's going on, then flush stdout.
    sys.stdout.write('Looking up the index page for %s...\n' % series)
    sys.stdout.flush()
    index = urllib2.urlopen('%s/%s' % (site, series))
    
    timeRun='%02d%02d%02d' % (holdTime.tm_year, holdTime.tm_mon, 
                              holdTime.tm_mday)
    updateName='update.%s' % timeRun
    if os.path.exists(os.path.realpath(updateName)):
      CompleteStatus=' '
    
    # Enumerate the list of chapters for the series.
    while True:
      buffer = index.readline(8192)
      ChapterHold=[]
      if not buffer:
        break
      
      # Perform a site-specific check, and parse.
      if site == MangaEden or site == PervEden:
        if 'chapterLink' in buffer:
          buffer = re.sub('/1/".*', '', buffer)
          buffer = re.sub('.*/', '', buffer)
          chaptrs.append(buffer)
      elif site == MangaPark:
        if '/manga/%s' % series in buffer:
          if '/s1' in buffer:
            if 'class' in buffer:
              ChapterHold.append(buffer)
              firstCut=re.sub('.*/c', '', buffer)
              chaptrs.append(re.sub('/1.*', '', firstCut))
    
    sys.stdout.write('Chapter index found... %d chapters to get.\n' %
                     len(chaptrs))
    sys.stdout.flush()
    
    # Compensate for len beginning at index value of 0. Start at the end of
    # list, and chop off the endline special character.
    for i in range(1, len(chaptrs)+1):
      chapter = str(chaptrs[len(chaptrs)-(i)]).rstrip('\n')
      while threading.activeCount() > 4:
        time.sleep(.25)
      thread = threading.Thread(target=getChap, args=(series, chapter, site))
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

def sigIntHandler(signal, frame):
    # Catch all the CTRL+C
    print '  SigInt Caught, Terminating...'
    sys.exit(0)


if __name__ == '__main__':
  
  parser=optparse.OptionParser('MangaGet Second Edition')
  
  parser.add_option('-s', action='store', dest='seriesName',
                    help='Specify a series name. Match the site.')
  parser.add_option('-c', action='store', dest='chap', 
                    help='Specify a chapter number.%s' % 
                    'For this, -s is a requirement.')
  parser.add_option('--site', action='store', dest='siteName', 
                    help='Specify a site name.%s %s %s' %
                    ('Valid options are:', 'mangaEden, me',
                     'mangaPark, mp.'))
  
  (results, args) = parser.parse_args()
  signal.signal(signal.SIGINT, sigIntHandler)
  
  if not results.siteName == None:
    if results.siteName == 'mangaPark' or results.siteName == 'mp':
      site=MangaPark
    elif results.siteName == 'mangaEden' or results.siteName == 'me':
      site=MangaEden
    elif results.siteName == 'pervEden' or results.siteName == 'pe':
      site=PervEden
    else:
      print 'Your options are mangaPark, mp, mangaEden or me!!!'
      sys.exit(0)
  else:
    site=MangaEden
  if not results.chap == None:
    if not results.seriesName == None:
      getChap(results.seriesName, results.chap, site)
    else:
      print 'Please provide a -s (series) with -c'
  elif not results.seriesName == None:
    getSeries(results.seriesName, site)
  else:
    parser.print_help()
