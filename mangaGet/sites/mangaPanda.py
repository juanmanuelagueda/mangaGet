import re
from .. import utilities

site = "http://www.mangapanda.com"
tags = ['mpand', 'mangaPanda', 'MangaPanda']
resultHeader = '***//////// MangaPanda Search Results \\\\\\\\\\\\\\\\***'


def getPicUrl(series, chapter, page, chapterHold = None):
    url='%s/%s/%s/%s' % (site,series,chapter,page)
    buf=utilities.getUrl(url)
    holdPic=''
    
    # Read the HTML, grabbing the line we need.
    while True:
      buffer=buf.readline(1024)
      if not buffer:
        break
      if 'img id="img"' in buffer:
        holdPic=buffer
    
    # Parse the picture's URL from the page's HTML
    firstCut=re.sub('.*src..', '', holdPic)
    picUrl=re.sub('".*', '', firstCut)
    
    return picUrl


def getPages(series, chapter, chapterHold = None):
    holdPage = None
    pageHold = []
    retries = 0
    while retries < 4:
      try:
        holdPage=utilities.getUrl('%s/%s/%s/1' % (site, series, chapter))
      except Exception:
        retries += 1
        sys.stdout.write('Error getting the url for chapter %s pagelist...\n' % chapter)
        continue
      break
    
    # Read the html line by line, looking the the one we need.
    while True:
      buffer=holdPage.readline(8192)
      if not buffer:
        break
      if 'option value' in buffer:
        pageHold.append(buffer)
    
    # Parse each page name from the line.
    pageNums=[]
    for i in pageHold:
      firstCut = re.sub('.*value../%s/%s/' % (series, chapter), '', i)
      pageNums.append(re.sub('".*', '', firstCut))
    return len(pageNums), []


def parseChapters(series):
    global site
    chaptrs = []
    startCount = 0
    
    index = utilities.getUrl('%s/%s' % (site, series))
    # Enumerate the list of chapters for the series.
    while True:
      buffer = index.readline(8192)
      if not buffer:
        break
      firstCut = ''
      finalCut = ''
      if startCount >= 1:
        if '/%s/' % series in buffer:
          if 'chapter-' in buffer:
            firstCut = re.sub('.*chapter-', '', buffer)
            secondCut = re.sub('\..*', '', firstCut)
          else:
            firstCut = re.sub('.*/%s/' % series, '', buffer)
            secondCut = re.sub('".*', '', firstCut)
          finalCut = secondCut.replace('\n', '')
      if finalCut != '':
        chaptrs.append(finalCut)
      if 'Chapter Name' in buffer:
        startCount += 1
    return chaptrs[::-1], None


def searchSite(srchStr):
    url = 'http://www.mangapanda.com/search/?w=%s' % srchStr
    urlHold = utilities.getUrl(url)
    title = ['']
    urlRoot = ['']
    searchStart = 0
    
    while True:
      buffer = urlHold.readline()
      
      if not buffer:
        break
  
      if searchStart >= 1:
        if 'href' in buffer:
          firstCut = re.sub('.*href...', '', buffer)
          secondCut = re.sub('</a.*', '', firstCut)
          urlRootHold, titleHold = re.split('">', secondCut)
          
          if 'html' in urlRootHold:
            firstCut = re.sub('.*/', '', urlRootHold)
            urlRoot.append(firstCut.replace('.html', ''))
          else:
            urlRoot.append(urlRootHold)
          title.append(titleHold.replace('\n', ''))
      if 'Results' in buffer:
        if 'Author' in buffer:
          break
        else:
          searchStart += 1
    return title, urlRoot
