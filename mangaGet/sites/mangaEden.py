#!/usr/bin/python

import re
import urllib2

site = "http://www.mangaeden.com/en-manga"

def getPages(series, chapter):
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
    return pageNums, None 
