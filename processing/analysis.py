import pandas as pd

from processing import util


def group_athletes_by_last_valid_split(df_split_times):
  # Group athletes (finishers and non-finishers) by the last split they reached.
  # AKA group dataframes by last_valid_index.
  return (
    (
      split_label,
      # print(split_name)
      df_split_times.loc[
        # subset of rows up to and including current split
        :split_label,
        # subset of columns whose last valid split is the current split
        df_split_times.apply(pd.Series.last_valid_index) == split_label
      ]
    )
    for split_label in df_split_times.index
  )


def series_number_stopped_by_split(df_split_times):
  return pd.Series({
    split_name: len(df_split_times_stn.columns)
    for split_name, df_split_times_stn 
    in group_athletes_by_last_valid_split(df_split_times)
  })


def series_athletes_through_each_split(df_split_times):
  s = series_number_stopped_by_split(df_split_times)
  return s.sum() - s.cumsum().shift(1, fill_value=0)


def series_gross_dnf_rate_after_split(df_split_times):
  s = series_number_stopped_by_split(df_split_times)
  return 100 * s / s.sum()


def series_net_dnf_rate_after_split(df_split_times):
  return 100 * series_number_stopped_by_split(df_split_times
    ).div(series_athletes_through_each_split(df_split_times))


def df_split_stats(df_split_times):
  return pd.DataFrame({
    'num_athletes_to_split': series_athletes_through_each_split(df_split_times),
    'num_athletes_dnf_after_split': series_number_stopped_by_split(df_split_times),
    'gross_dnf_rate_after_split': series_gross_dnf_rate_after_split(df_split_times).round(1),
    'net_dnf_rate_after_split': series_net_dnf_rate_after_split(df_split_times).round(1),
  }).convert_dtypes()


def df_split_times_none_missing(df_split_times):
  """Find athletes who aren't missing any split times."""
  util.print_td(df_split_times)
  return df_split_times[df_split_times.columns[
    ~df_split_times.isnull().any()]]


def df_segment_times(df_split_times):
  """figure out how much time each athlete spent between each aid
  
  NOTE: This function has only been tested on a DataFrame with 
  NO missing split data. 
  """
  df_out = df_split_times.diff(1)  # .fillna(df_split_times)
  df_out.iloc[0, :] = df_split_times.iloc[0, :]
  # df_out.index = create_segment_index(df_split_times)
  return df_out


def df_segment_percent_of_total(df_split_times):
  """% of total time
  
  aka "split_fraction"
  """
  return 100.0 * df_segment_times(df_split_times) / df_split_times.iloc[-1, :]


def stats_df(df):
  df_stats = pd.DataFrame(index=df.index)
  df_stats['median'] = df.median(axis=1)
  df_stats['mean'] = df.mean(axis=1)
  df_stats['std'] = df.std(axis=1)
  df_stats['min'] = df.min(axis=1)
  df_stats['max'] = df.max(axis=1)
  return df_stats


def stats_df_td(df_td):
  """Idk if this works, idk if I care."""
  df_td_stats = stats_df(df_td)
  return df_td_stats.apply(util.series_td_to_series_hr)


def create_segment_index(data_splits, include_start=True):
  """Find all valid segments, even if there are missing aid stations.

  Segments are defined by the aid stations at their start and end.

  MuliIndex seems to be the best solution here. Trying it out.
  One level for the split label at the start of the segment,
  one for the split label at the end.

  Refs:
    https://pandas.pydata.org/docs/user_guide/advanced.html#multiindex-advanced-indexing

  NOTE: A tuple index probably does the same thing, more simply.
  But let's seeeeeee.

  NOTE: IntervalIndex couldn't do this - it seemed I was using it in an
  unintended way. Integer-based indexes could create an IntervalIndex
  from splits, but there's no inherent order in string indexes.
  Behind the scenes, I was assuming a certain order. Bleh.

  ```
  return pd.IntervalIndex.from_breaks(
    series_split_times.index[series_split_times.notnull()].to_list(),
    closed='both')
  ```
  """
  index_split_labels = data_splits.index

  if include_start:
    split_arrays = [
      ['Start'] + index_split_labels[:-1].to_list(),
      index_split_labels
    ]
  else:
    split_arrays = [
      index_split_labels[:-1],
      index_split_labels[1:]
    ]

  return pd.MultiIndex.from_arrays(split_arrays,
    names=('label_st', 'label_ed'))


def create_segment_index_valid(series_split_times):
  """Find all valid segments, even if there are missing aid stations.

  Segments are defined by the aid stations at their start and end.

  See `create_segment_index` above.
  """
  index_split_labels_valid = series_split_times.index[series_split_times.notnull()]
  return pd.MultiIndex.from_arrays(
    [
      index_split_labels_valid[:-1],
      index_split_labels_valid[1:],
    ],
    names=('label_st', 'label_ed'))
