#!/usr/bin/python

import re
import sys
import urllib2
import utilities

site = 'http://www.mangapark.com/manga'
tags = ['mp', 'mangaPark', 'MangaPark']
resultHeader = '***//////// MangaPark Search Results \\\\\\\\\\\\\\\\***'

def getPages(series, chapter, chapterHold = None):
    holdPics=[]
    finalPics=[]
    chapterUrl=''
    
    # Check to see if ChapterHold alredy has what we need.
    if not chapterHold:
      holdChap=utilities.getUrl('%s/%s' % (site, series))
      
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
    holdPage=utilities.getUrl('%s%s' % (site, chapterUrl))
    
    # Loop through the chapter's URL line by like, parsing the pics out.
    while True:
      buffer=holdPage.readline(8192)
      if not buffer:
        break
      if 'a target="_blank' in buffer:
        firstCut=re.sub('.*href..', '', buffer)
        finalPics.append(re.sub('" .*', '', firstCut))
    return len(finalPics), finalPics


def parseChapters(buffer, series):
    finalCut = ''
    chapterHold = None
    if '/manga/%s' % series in buffer:
      if '/s1' in buffer:
        if 'class' in buffer:
          chapterHold = buffer
          firstCut = re.sub('.*/c', '', buffer)
          secondCut = re.sub('/1.*', '', firstCut)
          finalCut = secondCut.replace('\n', '')
    return finalCut, chapterHold


def searchSite(srchStr):
    url = 'http://www.mangapark.com/search?q=%s' % srchStr
    urlHold = utilities.getUrl(url)
    title = ['']
    urlRoot = ['']
    while True:
      buffer = urlHold.readline()
      
      if not buffer:
        break
  
      if '/manga/' in buffer:
        if 'cover' in buffer:
          firstCut = re.sub('.*/manga/', '', buffer)
          secondCut = re.sub('">', '', firstCut)
          urlRootHold, titleHold = re.split('".*"', secondCut)
          
          urlRoot.append(urlRootHold)
          title.append(titleHold.replace('\n', ''))
    return title, urlRoot
