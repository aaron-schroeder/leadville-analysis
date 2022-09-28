"""Run scrapy from a python script rather than command line.

TODO:
  * Make these scraper scripts generally available,
    so I don't have to copy them over to every new project.
  * In terms of working with pandas, what works best is:
    * athletes: a simple json file with a list of athleteitems
    * metadata: a simple json file with the single raceitem
    ...so how do we get a pipeline/settings combination to
    accomplish that for us?

Refs:
  https://doc.scrapy.org/en/latest/topics/practices.html#run-scrapy-from-a-script
  https://stackoverflow.com/questions/53542201/when-scrapy-finishes-i-want-to-create-a-dataframe-from-all-data-crawled
  https://gitlab.com/gallaecio/versiontracker/blob/master/versiontracker/pipelines.py
  https://gitlab.com/gallaecio/versiontracker/blob/master/versiontracker/__init__.py#L212
 
"""
import os

from scrapy.crawler import CrawlerProcess
from scrapy_athlinks import RaceSpider

from processing import io


class LeadvilleScraper:
  def __init__(self, race_year):
    self.spider = RaceSpider
    self.race_year = race_year
    self.dir_out = io.get_raw_race_data_dir(race_year)

  def _get_uri(self, fname):
    return os.path.join(self.dir_out, fname)

  def run_spider(self, settings={}):
    if not os.path.exists(self.dir_out):
      os.makedirs(self.dir_out)
    process = CrawlerProcess(settings=settings)
    process.crawl(self.spider, io.get_race_url(self.race_year))
    process.start()

  def run_spider_pandas(self):
    """Saves items in the most pandas-available file formats."""
    self.run_spider(settings={
      # https://docs.scrapy.org/en/latest/topics/feed-exports.html#feeds
      'FEEDS': {
        # https://docs.scrapy.org/en/latest/topics/feed-exports.html#storage-uri-parameters
        self._get_uri('athletes.json'): {
          'format':'json',
          # default False for local storage
          'overwrite': True,

          'item_classes': ['scrapy_athlinks.items.AthleteItem'],
        },
        self._get_uri('metadata.json'): {
          'format':'json',
          'overwrite': True,
          'item_classes': ['scrapy_athlinks.items.RaceItem'],
          # TODO: How to make it a single json object though?
          # (Rather than a single-item list)
        },
      }
    })

  def run_spider_athlete_results_jl(self):
    """Scrape a race's results and output athlete items as a jl file"""
    self.run_spider(settings={
      'FEEDS': {
        # self._get_uri('%(event_id)s_athletes.jl'): {
        self._get_uri('athletes.jl'): {
          'format':'jsonlines',
          'overwrite': True,
          'item_classes': ['scraper.items.AthleteItem'],
        }
      }
    })

  def run_spider_athlete_results_json(self):
    """Scrape a race's results and output as a json file"""
    self.run_spider(settings={
      'ITEM_PIPELINES': {
        'scrapy_athlinks.pipelines.SingleJsonWriterPipeline': 300,
      },
      'PATH_OUT': self._get_uri('race.json'),
    })

  def run_spider_athlete_results_json_simple(self):
    self.run_spider(settings={
      'FEEDS': {
        self._get_uri('simple.json'): { 
          'format':'json',
          'overwrite': True,
        },
      }
    })