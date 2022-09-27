import os

from scrapy.crawler import CrawlerProcess
from scrapy_athlinks import RaceSpider

from processing import io


RACE_YEAR = 2019

# DIR_OUT = settings.RAW_RACE_DATA_DIR
DIR_OUT = io.get_raw_race_data_dir(RACE_YEAR)

if not os.path.exists(DIR_OUT):
  os.makedirs(DIR_OUT)

fname_athletes = os.path.join(DIR_OUT, 'athletes.json')
fname_meta = os.path.join(DIR_OUT, 'metadata.json')
settings = {}
settings['FEEDS'] = {
  fname_athletes: {
    'format':'json',
    'overwrite': True,
    'item_classes': ['scrapy_athlinks.items.AthleteItem'],
  },
  fname_meta: {
    'format':'json',
    'overwrite': True,
    'item_classes': ['scrapy_athlinks.items.RaceItem'],
    # TODO: How to make it a single json object though?
    # (Rather than a single-item list)
  },
}

process = CrawlerProcess(settings=settings)
process.crawl(RaceSpider, io.get_race_url(RACE_YEAR))
process.start()