#!/usr/bin/python

import re
import urllib2

site = 'http://www.mangapark.com/manga'
tags = ['mp', 'mangaPark', 'MangaPark']

def getPages(series, chapter, chapterHold = None):
    holdPics=[]
    finalPics=[]
    chapterUrl=''
    
    # Check to see if ChapterHold alredy has what we need.
    if not chapterHold:
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
      for lines in chapterHold:
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
    return len(finalPics), finalPics


def parseChapters(buffer):
    if '/manga/%s' % series in buffer:
      if '/s1' in buffer:
        if 'class' in buffer:
          chapterHold = buffer
          firstCut=re.sub('.*/c', '', buffer)
          secondCut=re.sub('/1.*', '', firstCut)
    return secondCut, chapterHold
