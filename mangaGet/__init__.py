import os
import re
import sys
import time

import shutil
import zipfile
import importlib
import threading

import sites

ChapterHold = []
CompleteStatus = None
Mods = []


def getPic(mod, series, chapter, page, picUrls,lastPage=1):
    
    # List of variables for this method
    pageName = '%02d.jpg' % int(page)
    holdTime = time.localtime()
    retries = 0
    curSize = 0
    
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
      os.mkdir(os.path.realpath('%s/%s' % (series, chapter)))
    
    up = utilities.getUrl(picUrl, series)
    meta = up.info()
    totalSize = meta.getheader('content-length')
    
    # Make a status entry for the log
    logFile = open(os.path.realpath('%s/%s/logFile' % (series, chapter)), 'a')
    logFile.write("File Number %02d/%02d  Current Time: %02d:%02d:%02d  " %
                  (int(page), int(lastPage), holdTime.tm_hour, 
                   holdTime.tm_min, holdTime.tm_sec))
    logFile.flush()
    
    # logFileErr=open(os.path.realpath('%s/logFile.err' % series), 'a')
    
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
        try:
          os.remove(os.path.realpath('%s/%s/%s' % (series, chapter, pageName)))
        except Exception:
          pass
        
        # Re-open the URL, re-grab the headers, and let the user know 
        # what happened
        err = 'Something\'s wrong with the filesize. Retrying...'
        errMsg = ('Chapter: %s Page: %s (%s) Current Time: %02d:%02d:%02d  \n' %
                  (chapter, page, err, holdTime.tm_hour, holdTime.tm_min, 
                   holdTime.tm_sec))
        utilities.errorWrite(errMsg, series)
        
        up = utilities.getUrl(picUrl, series)
        meta = up.info()
        totalSize = meta.getheader('content-length')
      
      # Try, Except for any 404 errors or such
      try:
        buffer = up.read()
        with open(os.path.realpath('%s/%s/%s' % (series, chapter, pageName)), 'wb') as f:
          f.write(buffer)
          f.close()
        
        # Get final size, and increment retries counter
        curSize = os.path.getsize(os.path.realpath('%s/%s/%s' %
                                (series, chapter, pageName)))
        retries += 1
        
      except Exception:
        err = 'Error while reading the pic from the URL. Retrying...'
        errMsg = ('Chapter: %s Page: %s (%s) Current Time: %02d:%02d:%02d  \n' %
                  (chapter, page, err, holdTime.tm_hour, 
                   holdTime.tm_min, holdTime.tm_sec))
        utilities.errorWrite(errMsg, series)
        retries += 1
    
    # Close out the log... Did it work?
    logFile.write('Success!\n')
    logFile.close()


def getChap(series, chapter, mod):
    global CompleteStatus
    
    # Piece together the name for the chapter
    if '.' in chapter:
      name = chapter.split('.')
      chapName = '%03d.%s' % (int(name[0]), name[1])
    else:
      chapName = '%03d' % (int(chapter))
    zipName = '%s.cbz' % chapName
    
    # Give the user some kind of status...
    if os.path.exists(os.path.realpath('./%s/%s' % (series, zipName))):
      utilities.statusPrint('Chapter %s found!!!... ' % chapName)
      return False
    else:
      utilities.statusPrint('Starting on chapter %s... ' % chapName)
      if CompleteStatus == None:
        statusStarter = 'For today, as have the following to read!'
        CompleteStatus = '%s\nDownloaded %s Chapter %s' % (statusStarter, 
                                                           series, chapter)
      else:
        CompleteStatus = '%s\nDownloaded %s Chapter %s' % (CompleteStatus, 
                                                           series, chapter)
 
    
    # Check for which site we're using. Parse pages for site-specifiy ref.
    pageNums, finalPics = mod.getPages(series, chapter)

    # Loop for every Picture
    for i in range(1, pageNums+1):
        getPic(mod, series, chapter, i, finalPics, pageNums)
    
    # Zip our chapter up, and remove the temp folder.
    zipIt('./%s/%s' % (series, chapter), '%s/%s' % (series, zipName),
          chapter)
    shutil.rmtree(os.path.realpath('%s/%s' % (series, chapter)))
    

def getSeries(series, mod):
    global CompleteStatus
    global ChapterHold
    chaptrs = []
    holdTime = time.localtime()
    
    # Let the user know what's going on, then flush stdout.
    sys.stdout.write('Looking up the index page for %s...\n' % series)
    sys.stdout.flush()
    
    timeRun = '%02d%02d%02d' % (holdTime.tm_year, holdTime.tm_mon, 
                              holdTime.tm_mday)
    updateName = 'update.%s' % timeRun
    if os.path.exists(os.path.realpath(updateName)):
      CompleteStatus=' '
    
    chaptrs, ChapterHold = mod.parseChapters(series)
    sys.stdout.write('Chapter index found... %d chapters to get.\n' %
                     len(chaptrs))
    sys.stdout.flush()
    
    argsPass = [series, mod]
    utilities.threadIt(getChap, chaptrs, argsPass)
    if not CompleteStatus == None:
      if not CompleteStatus == ' ':
        with open(updateName, 'ab') as f:
          f.write('%s\n' % CompleteStatus)
          f.flush()
          f.close()


def zipIt(path, name, top):
    # Walk an entire directory, recursively creating a zip.
    zip = zipfile.ZipFile(name, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(path):
      for file in files:
        zip.write(os.path.join(root, file), '%s/%s' % (top, file))
    zip.close()


def searchMod(mod, srchStr):
    srchTitle, srchUrl = mod.searchSite(srchStr)
    sys.stdout.write('%s \n' % mod.resultHeader)
    for title in range(1, len(srchTitle)):
      sys.stdout.write('%d. %s\n' % (title, srchTitle[title]))
    selection = raw_input('Please select from the above: ')
    try:
      selNum = int(selection)
      sys.stdout.write('Your download string is: %s \n' % srchUrl[selNum])
      return srchUrl[selNum]
    except ValueError:
      sys.stdout.write('Invalid Entry. Exiting... \n')


def importer():
    modNames = ['mangaGet.sites.%s' % f for f in sites.__all__]
    mods = map(importlib.import_module, modNames)
    return mods


if __name__ == 'mangaGet':
    Mods = importer()
