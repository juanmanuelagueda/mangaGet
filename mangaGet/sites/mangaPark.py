import re
from .. import utilities

site = 'http://www.mangapark.com/manga'
tags = ['mp', 'mangaPark', 'MangaPark']
resultHeader = '***//////// MangaPark Search Results \\\\\\\\\\\\\\\\***'

def getPages(series, chapter, chapterHold = None):
    chapterUrl = ''
    chapCompile=re.compile('<a href="/manga(?P<chap>[^"]*%s)" target="_blank">all</a>' % chapter)
    picCompile=re.compile('a target="_blank" href="(?P<pic>[^"]*)" title=')

    # Check to see if ChapterHold alredy has what we need.
    if not chapterHold:
      chapUrl = utilities.getUrl('%s/%s' % (site, series), series)
      chapterUrl = chapCompile.search(chapUrl.read()).groups()[0]
    
    # If ChapterHold has what we need, just use it!
    else:
      chapterUrl = chapCompile.search(chapUrl.read()).groups()[0]
    
    # Once we have the chapter's URL, lets open it.
    pageUrl = utilities.getUrl('%s%s' % (site, chapterUrl), series)
    finalPics = picCompile.findall(pageUrl.read())
    
    return len(finalPics), finalPics


def parseChapters(series):
    seriesUrl = utilities.getUrl('%s/%s' % (site, series), series)
    seriesCompile=re.compile('[^/c]*/c(?P<chaps>[^"]*)" target="_blank">all</a>')
    holdCompile=re.compile('a href=".*/s1[^"]*" target="_blank">all</a>')
    
    chaptrHold = holdCompile.findall(seriesUrl.read())
    chaptrs = seriesCompile.findall(" ".join(chaptrHold))
    return chaptrs, chaptrHold


def searchSite(srchStr):
    title = ['']
    urlRoot = ['']
    
    url = 'http://www.mangapark.com/search?q=%s' % srchStr
    urlHold = utilities.getUrl(url)
    
    while True:
      buffer = utilities.safeRead(urlhold, '.')
      
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
