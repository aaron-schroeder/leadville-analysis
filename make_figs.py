"""Originally from leadville-analysis/make_subplots_split_dnf_colorcoded

Relevant files to look at:
  * make_plot.py
  * make_subplots_split_dnf_colorcoded.py
    * Depends on some stuff in infer_dnfs.py
    * Then implement loaders so I can get the data here
  * analyze_split_times.py (mostly analysis)
  * analysis_two.py (mostly plots)
"""

from operator import index
import numpy as np
import plotly.graph_objects as go
from plotly.io import templates
from plotly.subplots import make_subplots
from plotly import colors
import pandas as pd

from processing import analysis, io, util


# Pass this around
RACE_YEAR = 2019
DF_SPLIT_INFO = io.load_df_split_info_clean(RACE_YEAR)

# colors.sequential.thermal
COLOR_SCALE = colors.sequential.Turbo  # could I just put 'Turbo'?
# NOTE: Could also build this dict manually.
COLORS = {
  split_label: COLOR_SCALE[i+2] 
  for i, split_label in enumerate(DF_SPLIT_INFO.index)
}

# ['ggplot2', 'seaborn', 'simple_white', 'plotly',
#  'plotly_white', 'plotly_dark', 'presentation', 'xgridoff',
#  'ygridoff', 'gridon', 'none']
TEMPLATE = 'plotly_dark'


def make_trace(series_split_times, series_split_data, last_valid_split_label):
  last_split_name = DF_SPLIT_INFO.loc[last_valid_split_label, 'name']

  return go.Scatter(
    x=util.series_td_to_series_hr(series_split_times),
    y=series_split_data,
    text=series_split_data.index,
    name=last_split_name.title(),
    legendgroup=last_split_name,
    mode='markers',
    marker_color=COLORS[last_valid_split_label],
    # marker_size=4,  # default 6 as of this writing
    # opacity=0.8,
    marker_size=5,
    opacity=0.7, # seems to help visibility
    # opacity=0.5,
  )


def make_trace_segment_times(df_split_times, split_label):
  """
  last_valid_split_label: defines the group of athletes we're plotting. But that can be
    inferred from df_split_times' last row...
  split_label: defines the trace we're making, and tells which row to get from
    both the segment times df and the cumulative times df.
  """
  last_valid_split_label = df_split_times.index[-1]
  last_split_name = DF_SPLIT_INFO.loc[last_valid_split_label, 'name']

  df_segment_times = analysis.df_segment_times(df_split_times)

  trace = make_trace(
    df_split_times.loc[split_label],
    # df_split_times.iloc[-1],  # ADS HERE
    util.series_td_to_series_hr(df_segment_times.loc[split_label]),
    last_valid_split_label
  )
  trace.update(dict(
    meta=[last_split_name],
    hovertemplate='<b>%{text}</b>:<br>'+
                  'This segment: %{y:.1f} hr<br>'+
                  'Total time: %{x:.1f} hr'+
                  '<extra>Furthest split:<br>%{meta[0]}</extra>',
  ))

  return trace


def make_trace_segment_fractions(df_split_times, split_label):
  last_valid_split_label = df_split_times.index[-1]
  last_split_name = DF_SPLIT_INFO.loc[last_valid_split_label, 'name']

  df_segment_fractions = analysis.df_segment_percent_of_total(df_split_times)

  trace = make_trace(
    df_split_times.loc[split_label],
    # df_split_times.iloc[-1],  # ADS HERE
    df_segment_fractions.loc[split_label],
    last_valid_split_label
  )

  trace.update(dict(
    meta=[last_split_name],
    hovertemplate='<b>%{text}</b>:<br>'+
                  'This segment: %{y:.1f}%<br>'+
                  'Total time: %{x:.1f} hr'+
                  '<extra>Furthest split:<br>%{meta[0]}</extra>',
  ))

  return trace


def df_segment_time_diffs(df_split_times):
  """Segment time differences by athlete, outbound vs inbound.

  NOTE: Only applies to leadville data.

  aka "split_deltas"

  TODO: Make this work like other analysis funcs.
  """
  df_segment_times = analysis.df_segment_times(df_split_times)

  # NOTE: if I ever start handling elapsed time as integer seconds (rather
  # than timedelta), I will have to change this code; a nonsense error 
  # about arithmetic operations needing numeric data (it IS!).
  # Seems to be related to IntegerArray being an experimental class.
  # See the note (https://pandas.pydata.org/docs/user_guide/integer_na.html):
  # "IntegerArray is currently experimental. Its API or implementation may change
  # without warning."
  return df_segment_times.iloc[:5:-1].values - df_segment_times.iloc[:6]


def make_trace_segment_deltas(df_split_times, split_label=None):
  """only finishers for now"""
  df_split_times_none_missing = analysis.df_split_times_none_missing(df_split_times)

  split_label = split_label or df_split_times.index[-1]
  last_valid_split_label = df_split_times.index[-1]
  last_split_name = DF_SPLIT_INFO.loc[last_valid_split_label, 'name']

  df_segment_deltas = df_segment_time_diffs(df_split_times_none_missing)

  trace = make_trace(
    df_split_times.iloc[-1],  # finishers only
    util.series_td_to_series_hr(df_segment_deltas.loc[split_label]),
    last_valid_split_label
  )
  trace.update(dict(
    hovertemplate='<b>%{text}</b>:<br>'+
                  'Time increase: %{y:.2f} hr<br>'+
                  'Finish time: %{x:.2f} hr'+
                  # '<extra></extra>',
                  '',
  ))

  return trace


def make_fig(df_split_times, trace_fn, split_label):
  fig = go.Figure(layout=dict(
    template=TEMPLATE,
    legend_title_text='Athletes by furthest split reached:',
    title_x=0.5,
  ))
  fig.update_xaxes(showticklabels=False)
  fig.update_yaxes(showticklabels=False)

  for _, df_split_times_stn in analysis.group_athletes_by_last_valid_split(df_split_times):
    if split_label in df_split_times_stn.index:
      trace_stn = trace_fn(
        df_split_times_stn, split_label=split_label)
      trace_stn.update(dict(showlegend=True))
      fig.add_trace(trace_stn)

  cutoff_hr = DF_SPLIT_INFO.loc[split_label, 'cutoff_hr']
  if not np.isnan(cutoff_hr):
    # Debug
    # print(f'Adding in subplt ({row_subplot}, {col_subplot}) at {cutoff_hr} hr')
    fig.add_vline(
      x=cutoff_hr,
      line_width=1, line_dash='dashdot', line_color='red',
    )
  return fig


def make_fig_segment_times(df_split_times, split_label):
  fig = make_fig(df_split_times, make_trace_segment_times, split_label)
  fig.update_layout(dict(
    title_text=f'Segment time: into {DF_SPLIT_INFO.loc[split_label, "name"]}', 
    xaxis_title='Cumulative time (hours)',
    yaxis_title='Segment time (hours)',
  ))
  fig.update_xaxes(dtick=1.0)
  fig.update_yaxes(dtick=1.0)
  return fig


def make_fig_segment_fractions(df_split_times, split_label):
  """Create scatterplots: percent of finish time vs. total finish time"""
  fig = make_fig(df_split_times, make_trace_segment_fractions, split_label)
  fig.update_layout(dict(
    title_text=f'Segment percentage: into {DF_SPLIT_INFO.loc[split_label, "name"]}',
    xaxis_title='Cumulative time (hours)',
    yaxis_title='% total time on course',
  ))
  return fig


# def make_fig_segment_deltas(df_split_times, split_label_end):
def make_fig_segment_deltas(df_split_times, split_label):
  """Create scatterplots: split delta vs. total finish time
  
  NOTE: This will be unique from the other two. It involves subtracting
  one split from another. Probably a new analysis function. GOOD NIGHT.
  """
  # TODO: Function-ize
  split_ix_ed = DF_SPLIT_INFO.index.get_loc(split_label)
  if split_ix_ed != 0:
    split_name_st = DF_SPLIT_INFO.iloc[split_ix_ed - 1]['name']
  else:
    split_name_st = 'Start'

  fig = go.Figure(layout=dict(
    template=TEMPLATE,
    legend_title_text='Athletes grouped by furthest split reached:',
    title=dict(
      text='Segment time difference, out and back: '+
        f'{split_name_st} <-> '+
        f'{DF_SPLIT_INFO.loc[split_label, "name"]}',
      x=0.5,
    ),
  ))
  fig.update_xaxes(showticklabels=False, dtick=1.0)
  fig.update_yaxes(showticklabels=False, dtick=1.0, zerolinewidth=5)

  # TODO: Something like this
  # for _, df_split_times_stn in analysis.group_athletes_by_last_valid_split(df_split_times):
  #   if split_label in df_split_times_stn.index:
  #     trace_stn = make_trace_segment_deltas(
  #       df_split_times_stn, DF_SPLIT_INFO, split_label=split_label)
  #     trace_stn.update(dict(showlegend=True))
  #     fig.add_trace(trace_stn)

  trace = make_trace_segment_deltas(df_split_times, split_label)
  fig.add_trace(trace)

  return fig


def get_subplot_rc(i_subplot):
  """Helper function for 2-row, 6-column subplot layout"""
  return (
    i_subplot + 1 if i_subplot < 6 else 12 - i_subplot,
    1 if i_subplot < 6 else 2
  )


def make_fig_subplots(df_split_times, trace_fn):
  """Make a 6x2 figure of some data vs. cumulative time."""
  # Initialize a figure with subplots for segment data.
  # rows = segments; cols = outbound/inbound
  fig = make_subplots(rows=6, cols=2,
    column_titles=['Outbound', 'Inbound'],
    specs=[[{'l': 0.05, 'r': 0.0}, {'l': 0.0, 'r': 0.05}] for _ in range(6)],
    # shared_yaxes=True,  # depends...
    )
  fig.update_layout(
    template=TEMPLATE,
    title=dict(x=0.5),
    legend=dict(
      orientation='h',
      xanchor='left', x=-0.05,
      title=dict(
        text='Athletes grouped by furthest split reached:',
        font_size=12,
      ),
    ),
    font_size=12,
  )
  fig.update_xaxes(showticklabels=False)
  fig.update_yaxes(showticklabels=False, title_font_size=12)
  fig.update_annotations(font_size=12)

  # Axis labels to identify what splits define each segment.
  all_labels = ['May Queen', 'Outward Bound', 'Half Pipe', 'Twin Lakes', 'Hope Pass', 'Winfield']
  left_labels = ['Start'] + all_labels[:-1]
  mid_labels = all_labels
  right_labels = ['Finish'] + all_labels[:-1]
  for i in range(len(mid_labels)):
    yaxis = fig.layout[f'yaxis{(i+1)*2-1}']
    yloc = sum(yaxis['domain']) / 2
    fig.add_annotation(text=left_labels[i],
                       xref='paper', yref='paper',
                       xanchor='right', x=0.04, 
                       y=yloc, showarrow=False)
    fig.add_annotation(text=mid_labels[i],
                    xref='paper', yref='paper',
                    x=0.5, y=yloc, showarrow=False)
    fig.add_annotation(text=right_labels[i],
                       xref='paper', yref='paper',
                       xanchor='left', x=0.96, 
                       y=yloc, showarrow=False)

  for _, df_split_times_stn in analysis.group_athletes_by_last_valid_split(df_split_times):
    if not df_split_times_stn.empty:
      for i_segment, label_ed in enumerate(df_split_times_stn.index):
        row_subplot, col_subplot = get_subplot_rc(i_segment)

        trace_stn_i = trace_fn(df_split_times_stn, split_label=label_ed)
        
        # Hide duplicate trace entries in the legend.
        trace_stn_i.update(dict(showlegend=i_segment==0))

        fig.add_trace(trace_stn_i, row=row_subplot, col=col_subplot)

        # Add a vertical line for cutoff time (if any) on each subplot.
        # for i_subplot, cutoff_hr  in enumerate(DF_SPLIT_INFO.loc[:, 'cutoff_hr']):
        cutoff_hr = DF_SPLIT_INFO.iloc[i_segment]['cutoff_hr']

        if not np.isnan(cutoff_hr):
          fig.add_vline(x=cutoff_hr,
            row=row_subplot, col=col_subplot,
            line=dict(width=1, dash='dashdot', color='red'))

  # TODO: Add synchronized hover functionality in JS...somewhere.
  # According to the gist here:
  # https://codepen.io/duyentnguyen/pen/LRVbyY
  # Plotly.newPlot('graph', data, layout);
  # var myPlot = document.getElementById('graph');
  # myPlot.on('plotly_hover', function (eventdata){
  # 	console.log(eventdata.xvals);
  #     Plotly.Fx.hover('graph',
  #     				[
  # 	    				{ curveNumber: 0, pointNumber:eventdata.points[0].pointNumber },
  #     					{ curveNumber: 1, pointNumber:eventdata.points[0].pointNumber },
  #     				],
  #         			['xy', 'x2y2']
  #     );
  # });

  return fig


def make_fig_subplots_times(df_split_times):
  """Make a 2x6 figure of segment times vs. cumulative time."""
  fig = make_fig_subplots(df_split_times, make_trace_segment_times)
  fig.update_layout(title_text='Segment time vs. cumulative time')
  fig.update_xaxes(dtick=1.0)
  fig.update_yaxes(dtick=1.0)
  return fig


def make_fig_subplots_frac(df_split_times):
  fig = make_fig_subplots(
    # This is really only instructive among finishers. There's too much
    # of an effect of the smaller denominator for DNFers, and it gets
    # noisy.
    # df_split_times,
    analysis.df_split_times_none_missing(df_split_times),
    make_trace_segment_fractions
  )
  fig.update_layout(title_text='Segment time (% of finish time) vs. cumulative time')
  fig.update_xaxes(dtick=1.0)
  fig.update_yaxes(dtick=2.5)
  return fig


if __name__ == '__main__':
  df_split_times = io.load_df_split_times_clean(2019)
  # util.print_td(df_split_times)

  # print(io.load_df_split_secs_clean(settings.CLEAN_RACE_DATA_DIR))

  # all_athlete_split_times = util.load_athlete_split_times(include_start=True)
  # all_aid_station_info = util.load_station_info(include_start=True)
  df_split_info = io.load_df_split_info_clean(2019)
  # TODO: Include start time? See ahead.
  # print(df_split_info)

  # Necessary to have sequential index, so we demote our aid station
  # names to the 'index' column. Work on this being pretty l8r.
  # df_split_info.reset_index(inplace=True)
  # print(df_split_info)

  # TODO: Consider whether a better index for aid info is just ints.
  #       They come in order, and that's more important than their names.
  # aid_station_info.reset_index(inplace=True)
  # print(aid_station_info)

  # print(df_split_info.index[-1:5:-1])

  # fig = make_fig_segment_times(df_split_times, df_split_times.index[4])
  # fig = make_fig_segment_fractions(df_split_times, df_split_times.index[1])
  fig = make_fig_segment_deltas(df_split_times, df_split_times.index[0])

  # fig = make_fig_subplots_times(df_split_times)
  # fig = make_fig_subplots_frac(df_split_times)

  fig.show()