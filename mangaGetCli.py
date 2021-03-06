#!/usr/bin/env python

import mangaGet
import optparse
import signal
import sys

from mangaGet.utilities import sigIntHandler

if __name__ == '__main__':
    tags = []
    searched = False
    for site in mangaGet.Mods:
        for tagHold in list((', '.join(site.tags[:]), 'or')):
            tags.append(tagHold)
  
    parser=optparse.OptionParser('MangaGet Second Edition')
  
    parser.add_option('-c', action='store', dest='chap', 
                      help='Specify a chapter number.%s' % 
                      'For this, -s is a requirement.')
    parser.add_option('-l', action='store', dest='lastNum',
                      help='Download the latest given number of chapters')
    parser.add_option('-s', action='store', dest='seriesName',
                      help='Specify a series name. Match the site.')
    parser.add_option('--search', action='store', dest='search', 
                      help='Specify search keywords.')
    parser.add_option('--site', action='store', dest='siteName', 
                      help='Specify a site name. %s %s' %
                      ('Valid options are:\n', ' '.join(tags[:-1])))
    parser.add_option('--sp', action='store_true', dest='searchPass', default=False, 
                      help='Pass search selection as series name.')
    
    (results, args) = parser.parse_args()
    signal.signal(signal.SIGINT, sigIntHandler)
    
    mod = None
    if not results.siteName == None:
      for site in mangaGet.Mods:
          if results.siteName in site.tags:
            mod=site
          if hasattr(site, 'htags'):
           if results.siteName in site.htags:
                mod = site
                mod.site = mod.hsite
      if mod == None:
        sys.stdout.write('Your options are mangaPark, mp, mangaEden or me!!!\n')
        sys.exit(0)
    else:
      for site in mangaGet.Mods:
        if 'me' in site.tags:
          mod=site
          
    if not results.search == None:
      results.seriesName = mangaGet.searchMod(mod, results.search)
      searched = True
      
    if searched:
      if not results.searchPass:
        sys.exit(0)
      
    if not results.chap == None:
      if not results.seriesName == None:
        sys.stdout.write('Starting on %s... \n' % results.seriesName)
        if '-' in results.chap:
          holdChaps = results.chap.split('-')
          argsPass = [results.seriesName, mod]
          chaptrs = range(int(holdChaps[0]), int(holdChaps[1])+1)
          mangaGet.utilities.threadIt(mangaGet.getChap, chaptrs[::-1], argsPass)
        else:
          mangaGet.getChap(results.seriesName, results.chap, mod)
          sys.stdout.write('\nFinished!!!\n')
      else:
        sys.stdout.write('Please provide a -s (series) with -c\n')
    elif not results.lastNum == None:
      if not results.seriesName == None:
        chaptrs, chapHold = mod.parseChapters(results.seriesName)
        passChap = []
        argsPass = [results.seriesName, mod]
        sys.stdout.write('The %s latest chapters for %s are: ' % 
                         (results.lastNum, results.seriesName))
        for i in range(0, int(results.lastNum)):
          if i < int(results.lastNum)-1:
            sys.stdout.write('%s, ' % chaptrs[i])
          else:
            sys.stdout.write('%s. \n' % chaptrs[i])
          passChap.append(chaptrs[i])
        if results.lastNum == '1':
          mangaGet.getChap(results.seriesName, passChap[0], mod)
          sys.stdout.write(' Finished!!!\n')
        else:
           mangaGet.utilities.threadIt(mangaGet.getChap, passChap, argsPass)
    elif not results.seriesName == None:
      mangaGet.getSeries(results.seriesName, mod)
    else:
      parser.print_help()
