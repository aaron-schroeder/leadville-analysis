import glob
import json
import os

import pandas as pd

from processing import cleaners
from processing.util import td_to_secs


DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, 'data')
INDEX_NAME = 'label'
SPLIT_INFO_FNAME = 'metadata.json'
ATHLETE_DATA_FNAME = 'athletes.json'
RACE_URLS_FNAME = 'race_urls.json'
SPLIT_SECS_FNAME = 'times.csv'
SPLIT_INFO_FNAME = 'splits.csv'


def get_race_url(race_year):
  with open(os.path.join(DATA_DIR, 'race_urls.json'), 'r') as f:
    dict_race_years = json.load(f)
  return dict_race_years[str(race_year)]


def get_race_data_dir(race_year):
  return os.path.join(DATA_DIR, str(race_year))


def get_raw_race_data_dir(race_year):
  return os.path.join(get_race_data_dir(race_year), 'raw')


def get_raw_race_data_dir(race_year):
  return os.path.join(get_race_data_dir(race_year), 'clean')


def load_df_split_info_raw(race_year):
  """Assumes we're working with single json object.

  Is this the ideal storage format, anyway??
  I need to load the json myself before pandas knows what to do with it.
  If I stored the metadata as its own json file, or as a single line
  in a .jl file, pandas would be able to read directly from file.
  https://pandas.pydata.org/docs/reference/api/pandas.read_json.html
  
  TODO:
    * Make more general:
      - Write a variety of different loaders for .jl, .json default, ...
        and control which is called thru a kw
      - Then split them out into constituent functions.
  """
  # Easiest approach for pandas
  raw_data_dir = get_raw_race_data_dir(race_year)
  fname = os.path.join(raw_data_dir, 'metadata.json')
  with open(fname, 'r') as f:
    raw_json = json.load(f)
  # return pd.DataFrame.from_records(raw_json['split_info'])
  return pd.DataFrame.from_records(raw_json[0]['split_info']
    ).set_index('name')

  # Maybe if this approach makes sense:
  # fname = os.path.join(data_dir, 'split_info.json')
  # with open(fname, 'r') as f:
  #   raw_json = json.load(f)
  # return pd.DataFrame.from_records(raw_json)

  # Single-object file (from custom pipeline)
  # fname = os.path.join(data_dir, 'race.json')
  # with open(fname, 'r') as f:
  #   raw_json = json.load(f)
  # return pd.DataFrame.from_records(raw_json['split_info'])


def load_df_split_info_clean(data_dir):
  return pd.read_csv(os.path.join(data_dir, SPLIT_INFO_FNAME), index_col=INDEX_NAME)


def load_df_split_ms_jl_raw(data_dir):
  # Option 1: json lines
  fname = os.path.join(data_dir, 'athletes.jl')
  with open(fname) as f:
    dict_cols = {
      json_line['name']: {split['name']: split['time_ms'] for split in json_line['split_data']}
      for json_line in [json.loads(line) for line in f]
    }
  return pd.DataFrame.from_dict(dict_cols)


def load_df_split_ms_json_raw(data_dir):
  # Option 2: custom-pipeline json
  fname = os.path.join(data_dir, 'race.json')
  with open(fname, 'r') as f:
    raw_json = json.load(f)
  dict_cols = {
    item['name']: {
      split['name']: split['time_ms']
      for split in item['split_data']
    }
    for item in raw_json['athletes']
  }
  return pd.DataFrame.from_dict(dict_cols)


def load_df_split_ms_json_simple_raw(data_dir):
  # Option 3: simple json, just athletes in file.
  fname = os.path.join(data_dir, 'athletes.json')
  with open(fname, 'r') as f:
    athlete_list = json.load(f)
  dict_cols = {
    athlete['name']: {
      split['name']: split['time_ms']
      for split in athlete['split_data']
    }
    for athlete in athlete_list
  }
  return pd.DataFrame.from_dict(dict_cols)


def load_df_split_ms_raw(data_dir):
  # # Option 1: jsonlines
  # return load_df_split_ms_jl_raw(data_dir)

  # # Option 2: custom-pipeline json
  # return load_df_split_ms_json_raw(data_dir)

  # Option 3: simple json
  return load_df_split_ms_json_simple_raw(data_dir)


# def load_athlete_split_times(clean=True, include_start=False):
# def load_df_split_times_raw(data_dir):
def load_df_split_times_raw(race_year):
  """
  For now, just assume all splits are chip time, so everyone was on
  the starting line at 0:00:00 on their chip.
  I could put this in the scraper file and re-scrape all athlete pages
  to find the actual chip start time (eg. 4:00:45).
  """
  # df_athlete_split_secs = load_athlete_split_secs(clean=clean)

  raw_data_dir = get_raw_race_data_dir(race_year)
  df_athlete_split_times = cleaners.process_df_ms(
    load_df_split_ms_raw(raw_data_dir)
  ).apply(pd.to_timedelta, axis=0, unit='ms')
  
  # if include_start:
  #   return pd.concat(
  #     [
  #       pd.DataFrame(
  #         data=pd.to_timedelta(0, unit='s'),
  #         index=pd.Index(['Start'], name=df_athlete_split_times.index.name),
  #         columns=df_athlete_split_times.columns,
  #       ),
  #       # pd.DataFrame(
  #       #   # data=[0 for _ in range(len(all_athlete_split_times.columns))],
  #       #   index=['Start'],
  #       #   columns=all_athlete_split_times.columns,
  #       #   dtype='timedelta64[ns]',
  #       # ),
  #       df_athlete_split_times
  #     ],
  #     # axis='columns',
  #     axis='index',
  #     # ignore_index=True,
  #   )

  return df_athlete_split_times


def load_df_split_secs_clean(data_dir):
  return pd.read_csv(
    os.path.join(data_dir, SPLIT_SECS_FNAME),
    index_col=INDEX_NAME
  ).astype('Int64')


def load_df_split_times_clean(data_dir):
  """
  For now, just assume all splits are chip time, so everyone was on
  the starting line at 0:00:00 on their chip.
  I could put this in the scraper file and re-scrape all athlete pages
  to find the actual chip start time (eg. 4:00:45).
  """
  # df_athlete_split_secs = load_athlete_split_secs(clean=clean)

  df_athlete_split_times = load_df_split_secs_clean(data_dir
    ).apply(pd.to_timedelta, axis=0, unit='s')
  
  # if include_start:
    # return pd.concat(
    #   [
    #     pd.DataFrame(
    #       data=pd.to_timedelta(0, unit='s'),
    #       index=pd.Index(['Start'], name=df_athlete_split_times.index.name),
    #       columns=df_athlete_split_times.columns,
    #     ),
    #     # pd.DataFrame(
    #     #   # data=[0 for _ in range(len(all_athlete_split_times.columns))],
    #     #   index=['Start'],
    #     #   columns=all_athlete_split_times.columns,
    #     #   dtype='timedelta64[ns]',
    #     # ),
    #     df_athlete_split_times
    #   ],
    #   # axis='columns',
    #   axis='index',
    #   # ignore_index=True,
    # )

  return df_athlete_split_times
  

def df_td_to_csv(df, fname):
  df.apply(td_to_secs).to_csv(fname)


def load_df_td_from_csv(fname):
  return pd.read_csv(fname, index_col=INDEX_NAME
    ).astype('Int64'
    ).apply(pd.to_timedelta, axis=0, unit='s')