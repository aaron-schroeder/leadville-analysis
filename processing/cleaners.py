import pandas as pd


def process_df_split_info(df_split_info):
  df_split_info['distance_mi'] = (df_split_info['distance_m'] / 1609.34
    ).round(decimals=1)

  df_split_info.index.name = 'label'
  
  return df_split_info.sort_values('distance_m', ascending=True)


def process_df_ms(df_ms):
  """Fixes millisecond data from Athlinks: missing value format.
  
  Athlinks uses -1 to represent missing data.
  This function changes that to Int64 dtype, which uses pd.NA to
  represent missing data.
  """

  return df_ms.where(lambda val: val != -1, pd.NA
    ).astype('Int64')


def sort_df_split_data_rows(df_split_data, df_split_info):
  """
  Args:
    df_split (pd.DataFrame): split data. Could be cumulative time to
      each split (seconds, timedeltas, etc), rankings, or whatever.
      Needs to have row labels contained in `df_split_info.index`.
  Returns:
    pd.DataFrame: split data sorted by the order of the splits in the
      (presumably) sorted `df_split_info`.
  """
  return df_split_data.loc[df_split_info.index]


def sort_df_split_data_columns(df_split_data, df_split_info=None):
  """
  Args:
    df_split (pd.DataFrame): split data that's sortable. Could be
      cumulative time to each split (seconds, timedeltas, etc),
      rankings, or whatever. Needs to have row labels contained in
      `df_split_info.index`.
  Returns:
    pd.DataFrame: split data sorted by the value of the split data
      at the furthest split each athlete reached.
      eg for split times, the last athlete to finish will come before
      all athletes who DNFed. 
  """
  row_labels_to_sort_by = df_split_data.index if df_split_info is None else df_split_info.index

  return df_split_data.sort_values(
    by=row_labels_to_sort_by[::-1].to_list(),
    axis=1
  )

def sort_df_split_data(df_split_times, df_split_info):
  """Sort rows and columns."""
  return sort_df_split_data_columns(
    sort_df_split_data_rows(df_split_times, df_split_info))