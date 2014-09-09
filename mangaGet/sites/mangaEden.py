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
    compilePic = re.compile('mainImg" src="(?P<imgUrl>[^"]*.[jpg,png])[^"]*" a')
    
    return "".join(['http:', compilePic.search(picUrl.read()).group('imgUrl')]) 


def getPages(series, chapter, chapterHold = None):
    chapUrl = utilities.getUrl('%s/%s/%s/1' % (site, series, chapter), series)
    pageCompile=re.compile('(?P<pageNum>[0-9]*)</a><a class="ui-state-default"')
    
    return int(pageCompile.findall(chapUrl.read())[-1]), []


def parseChapters(series):
    seriesUrl = utilities.getUrl('%s/%s' % (site, series), series)
    seriesCompile = re.compile('<a href="/en-manga/%s/(?P<chap>[^/]*)/1/" class="chapterLink">' % series)
    return seriesCompile.findall(seriesUrl.read()), None


def searchSite(srchStr):
    searchCompile=re.compile('href="(?P<seriesUrl>[^"]*)" class="[a-z]*Manga">(?P<sTitle>[^<]*)<')
    url = 'http://www.mangaeden.com/en-directory/?title=%s' % srchStr
    searchUrl = utilities.getUrl(url, '.')
    
    title = ['']
    urlRoot = ['']
    
    matches=searchCompile.findall(searchUrl.read())
    for m in matches:
        urlRoot.append(m[0])
        title.append(m[1])
    return title, urlRoot
