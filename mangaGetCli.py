#!/usr/bin/python

import mangaGet
import optparse
import signal

def sigIntHandler(signal, frame):
    # Catch all the CTRL+C
    print '  SigInt Caught, Terminating...'
    sys.exit(0)


if __name__ == '__main__':
  
  parser=optparse.OptionParser('MangaGet Second Edition')
  
  parser.add_option('-s', action='store', dest='seriesName',
                    help='Specify a series name. Match the site.')
  parser.add_option('-c', action='store', dest='chap', 
                    help='Specify a chapter number.%s' % 
                    'For this, -s is a requirement.')
  parser.add_option('--site', action='store', dest='siteName', 
                    help='Specify a site name.%s %s %s' %
                    ('Valid options are:', 'mangaEden, me',
                     'mangaPark, mp.'))
  
  (results, args) = parser.parse_args()
  signal.signal(signal.SIGINT, sigIntHandler)
  
  if not results.siteName == None:
    if results.siteName == 'mangaPark' or results.siteName == 'mp':
      mangaGet.site=mangaGet.MangaPark
    elif results.siteName == 'mangaEden' or results.siteName == 'me':
      mangaGet.site=mangaGet.MangaEden
    elif results.siteName == 'pervEden' or results.siteName == 'pe':
      mangaGet.site=mangaGet.PervEden
    else:
      print 'Your options are mangaPark, mp, mangaEden or me!!!'
      sys.exit(0)
  else:
    mangaGet.site=mangaGet.MangaEden
  if not results.chap == None:
    if not results.seriesName == None:
      mangaGet.getChap(results.seriesName, results.chap, mangaGet.Mods[0])
    else:
      print 'Please provide a -s (series) with -c'
  elif not results.seriesName == None:
    mangaGet.getSeries(results.seriesName, site)
  else:
    parser.print_help()
