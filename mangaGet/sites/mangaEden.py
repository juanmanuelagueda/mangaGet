import re
from .. import utilities

site = "http://www.mangaeden.com/en-manga"
tags = ['me', 'mangaEden', 'MangaEden']
resultHeader = '***//////// MangaEden Search Results \\\\\\\\\\\\\\\\***'

def getPages(series, chapter, chapterHold = None):
    holdPage = None
    retries = 0
    while retries < 4:
      try:
        holdPage=utilities.getUrl('%s/%s/%s/1' % (site, series, chapter))
      except Exception:
        retries += 1
        print 'Error getting the url for chapter %s pagelist...' % chapter
        continue
      break
    
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
    return len(pageNums), []

def getPicUrl(series, chapter, page, chapterHold = None):
    url='%s/%s/%s/%s' % (site,series,chapter,page)
    buf=utilities.getUrl(url)
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


def parseChapters(buffer, series):
    firstCut = ''
    finalCut = ''
    if 'chapterLink' in buffer:
      firstCut = re.sub('/1/".*', '', buffer)
      secondCut = re.sub('.*/', '', firstCut)
      finalCut = secondCut.replace('\n', '')
    return finalCut, None


def searchSite(srchStr):
    url = 'http://www.mangaeden.com/en-directory/?title=%s' % srchStr
    urlHold = utilities.getUrl(url)
    title = ['']
    urlRoot = ['']
    while True:
      buffer = urlHold.readline()
      
      if not buffer:
        break
  
      if 'en-manga' in buffer:
        if 'class' in buffer:
          firstCut = re.sub('^<.*manga.', '', buffer)
          secondCut = re.sub('<.*', '', firstCut)
          urlRootHold, titleHold = re.split('.".*Manga..', secondCut)
          
          urlRoot.append(urlRootHold)
          title.append(titleHold.replace('\n', ''))
    return title, urlRoot
