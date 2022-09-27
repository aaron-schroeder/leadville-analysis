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

import io


def make_dir_out(race_year):
  dir_out = io.get_raw_race_data_dir(race_year)
  if not os.path.exists(dir_out):
    os.makedirs(dir_out)
  return dir_out


def run_scraper(settings, race_year):
  race_url = io.get_race_url(race_year)
  process = CrawlerProcess(settings=settings)
  process.crawl(RaceSpider, race_url)
  process.start()


def scrape_for_pandas(race_year):
  """Saves items in the most pandas-available file formats."""
  dir_out = make_dir_out(race_year)
  settings = {
    # https://docs.scrapy.org/en/latest/topics/feed-exports.html#feeds
    'FEEDS': {
      # https://docs.scrapy.org/en/latest/topics/feed-exports.html#storage-uri-parameters
      os.path.join(dir_out, 'athletes.json'): {
        'format':'json',
        # default False for local storage
        'overwrite': True,

        'item_classes': ['scrapy_athlinks.items.AthleteItem'],
      },
      os.path.join(dir_out, 'metadata.json'): {
        'format':'json',
        'overwrite': True,
        'item_classes': ['scrapy_athlinks.items.RaceItem'],
        # TODO: How to make it a single json object though?
        # (Rather than a single-item list)
      },
    }
  }
  run_scraper(settings, race_year)


def scrape_athlete_results_jl(race_year):
  """Scrape a race's results and output as a jl file"""
  dir_out = make_dir_out(race_year)
  settings = {
    'FEEDS': {
      # os.path.join(dir_out, '%(event_id)s_athletes.jl')
      os.path.join(dir_out, 'athletes.jl'): {
        'format':'jsonlines',
        'overwrite': True,
        'item_classes': ['scraper.items.AthleteItem'],
      }
    }
  }
  run_scraper(settings, race_year)


def scrape_athlete_results_json(race_year):
  """Scrape a race's results and output as a json file"""
  dir_out = make_dir_out(race_year)
  settings = {
    'ITEM_PIPELINES': {
      'scraper.pipelines.SingleJsonWriterPipeline': 300,
    },
    'PATH_OUT': os.path.join(dir_out, 'race.json'),
  }
  run_scraper(settings, race_year)


def scrape_athlete_results_json_simple(race_year):
  settings = {}
  dir_out = make_dir_out(race_year)
  settings['FEEDS'] = {
    os.path.join(dir_out, 'simple.json'): { 
      'format':'json',
      'overwrite': True,
    },
  }
  run_scraper(settings, race_year)