import re
from .. import utilities

site = "http://www.mangaeden.com/en-manga"
hsite = "http://www.perveden.com/en-manga"
tags = ['me', 'mangaEden', 'MangaEden']
htags = ['pe', 'pervEden', 'PervEden']
resultHeader = '***//////// MangaEden Search Results \\\\\\\\\\\\\\\\***'


def getPicUrl(series, chapter, page, chapterHold = None):
    url = '%s/%s/%s/%s' % (site,series,chapter,page)
    picUrl = utilities.getUrl(url, series)
    holdPic=''
    
    # Read the HTML, grabbing the line we need.
    while True:
      buffer = utilities.safeRead(picUrl, series)
      if not buffer:
        break
      if 'mainImg' in buffer:
        holdPic=buffer
    
    # Parse the picture's URL from the page's HTML
    firstCut=re.sub('.*Img" src="', '', holdPic)
    picUrl='http:%s' % re.sub('" alt=.*', '', firstCut)
    
    return picUrl


def getPages(series, chapter, chapterHold = None):
    chapUrl = None
    retries = 0
    while retries < 4:
      try:
        chapUrl = utilities.getUrl('%s/%s/%s/1' % (site, series, chapter), series)
      except Exception:
        retries += 1
        sys.stdout.write('Error getting the url for chapter %s pagelist...\n' % chapter)
        continue
      break
    
    # Read the html line by line, looking the the one we need.
    while True:
      buffer=utilities.safeRead(chapUrl, series)
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


def parseChapters(series):
    global site
    chaptrs = []
    
    chapUrl = utilities.getUrl('%s/%s' % (site, series), series)
    # Enumerate the list of chapters for the series.
    while True:
      buffer = utilities.safeRead(chapUrl, series)
      if not buffer:
        break
      firstCut = ''
      finalCut = ''
      if 'chapterLink' in buffer:
        firstCut = re.sub('/1/".*', '', buffer)
        secondCut = re.sub('.*/', '', firstCut)
        finalCut = secondCut.replace('\n', '')
      if finalCut != '':
        chaptrs.append(finalCut)
    return chaptrs, None


def searchSite(srchStr):
    url = 'http://www.mangaeden.com/en-directory/?title=%s' % srchStr
    searchUrl = utilities.getUrl(url, '.')
    title = ['']
    urlRoot = ['']
    while True:
      buffer = utilities.safeRead(searchUrl, '.')
      
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
