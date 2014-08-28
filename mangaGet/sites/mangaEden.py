#!/usr/bin/python

import re
import urllib2

site = "http://www.mangaeden.com/en-manga"
tags = ['me', 'mangaEden', 'MangaEden']

def getPages(series, chapter, chapterHold = None):
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
    return len(pageNums), None 

def getPicUrl(series, chapter, page):
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
    
    return picUrl


def parseChapters(buffer):
    if 'chapterLink' in buffer:
      buffer = re.sub('/1/".*', '', buffer)
      buffer = re.sub('.*/', '', buffer)
    return buffer, None
