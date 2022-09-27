import numpy as np
import pandas as pd
from IPython.display import display


def float64_to_int64(series_float_na):
  """Convert nullable float Series to nullable int Series.

  Will always round down, and will always return ints. eg. 0.9 -> 0

  I believe this also works for object dtype as long as the data is
  definitely numeric.

  This does not work:
  `split_time = split_time_td.dt.total_seconds().astype('Int64')`
  ...which is apparently intended Pandas behavior, with a workaround:
  https://github.com/pandas-dev/pandas/issues/37429#issue-729916930

  """
  return np.floor(pd.to_numeric(series_float_na, errors='coerce')).astype('Int64')


def td_to_secs(series_td):
  return float64_to_int64(series_td.dt.total_seconds())


def td_fmt(total_seconds):
  if np.isnan(total_seconds):
    return None
  hours, rem = divmod(total_seconds, 3600)
  minutes, seconds = divmod(rem, 60)
  return f'{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f}'


def scalar_td_fmt(td):
  return td_fmt(td.total_seconds())


def series_td_fmt(series_td):
  return series_td.dt.total_seconds(
    ).apply(td_fmt
    ).astype('string')


def df_td_fmt(df_td):
  return df_td.apply(series_td_fmt)


def print_td(obj):
  if isinstance(obj, pd.DataFrame):
    print(df_td_fmt(obj))
  elif isinstance(obj, pd.Series):
    print(series_td_fmt(obj))
  elif isinstance(obj, pd.Timedelta):
    print(scalar_td_fmt(obj))


def series_td_to_series_hr(series_td):
  return series_td.dt.total_seconds() / 3600


def full_df_to_file(df, fname):
  pd.set_option('display.max_columns', 1000)
  pd.set_option('display.width', 1000000000000)
  with open(fname, 'w') as f:
    print(df, file=f)
    # f.write(f'{df!r}')
  pd.reset_option('display.max_columns', 'display.width')

  # The following options are equivalent
  # final_splits = pd.Series({
  #   athlete: split_times.last_valid_index()
  #   for athlete, split_times in df_all_athlete_split_times.iteritems()})
  # final_splits_2 = df_all_athlete_split_times.apply(pd.Series.last_valid_index)
  # pd.testing.assert_series_equal(final_splits, final_splits_2)
  # print(final_splits)


def display_full_df(df):
  pd.set_option('display.max_columns', 1000)
  pd.set_option('display.width', 1000000000000)
  display(df)
  pd.reset_option('display.max_columns', 'display.width')