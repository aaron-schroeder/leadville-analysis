"""
The idea is basically to replicate functionality in the scrapy binary
(./env/bin/scrapy).

https://github.com/scrapy/scrapy/blob/2.6.2/scrapy/cmdline.py#L118
"""
import getopt
import sys

from processing.scrapers import LeadvilleScraper


def execute(argv=None):
  if argv is None:
    argv = sys.argv

  arg_help = (
    f'Usage\n'
    f'=====\n'
    f'  {argv[0]} -y <year>\n\n'
    f'Run the spider for the Leadville results in the given year\n\n'
    f'Optional Arguments\n'
    f'==================\n'
    f'  -h, --help            show this help message and exit\n'
  )
  
  try:
    opts, args = getopt.getopt(
      argv[1:],
      'hy:',
      ['help', 'year=']
    )
    print((opts, args))
  except:
    print(arg_help)
    sys.exit(2)

  for opt, arg in opts:
    if opt in ('-h', '--help'):
      print(arg_help)
      sys.exit(0)  # because it worked as expected
    elif opt in ('-y', '--year'):
      LeadvilleScraper(int(arg)).run_spider_pandas()
    

if __name__ == "__main__":
  sys.exit(execute())

  # Hardcoded alternative
  # scraper = LeadvilleScraper(2019)
  # scraper.run_spider_pandas()