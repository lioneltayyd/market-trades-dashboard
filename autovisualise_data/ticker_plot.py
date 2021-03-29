

# %%
import os, logging, re
import pandas as pd
import streamlit as st
import holoviews as hv 
import hvplot.pandas

from datetime import datetime
from typing import Dict, List, Text, Optional, Tuple

# Holoview config. 
hv.extension('bokeh')

# Pandas config. 
pd.options.display.float_format = '{:,.4f}'.format 

# Personal modules. 
from config.config import FREQ_KEYS, LOG_PROCESSING_FILEPATH
from config.config_logger import setup_logger
from config.config_dashboard import (
    HV_PN_WIDTH, HV_TOOLS_FOR_TICKER
)


# --------------------------------------------------------------
# Logger setup. 
# --------------------------------------------------------------

logger = logging.getLogger(__name__)
logger, file_handler, stream_handler = setup_logger(logger, LOG_PROCESSING_FILEPATH) 


# %%
# --------------------------------------------------------------
# Read File.
# --------------------------------------------------------------

def get_ticker_options(etf_dir:Text) -> List[Text]:
    '''
    Purpose : 
        Output a list of ticker options based on the specified ETF directory. 

    Input   :
        etf_dir : Str. Full absolute path for the ETF directory. 
                          
    Output  : 
        List obj containing a list of ticker options. 
    '''

    logger.info('Start running (ticker_selector) function.')

    # REFINE: Need to test how the data is being extracted on Streamlit Sharing. 
    # Change directory. 
    default_dir = os.getcwd()
    os.chdir(os.environ['DATA_ABS_DIR'])
    logger.debug(f'----- Changed to the data warehouse directory.') 

    # Try, get a list of ticker symbols. 
    # Otherwise, output an empty list. 
    try:
        ticker_list_dir = os.path.join(os.getcwd(), 'docs', 'dataset', etf_dir) 
        re_compile = re.compile(r'[^.][A-Z]')
        ls_tickers = list( filter(re_compile.match, os.listdir(ticker_list_dir)) )
        logger.debug(f'----- Captured a list of ticker symbol for ({etf_dir}) directory.') 
    except:
        ls_tickers = []
        logger.debug(f'----- Failed to capture a list of ticker symbol for ({etf_dir}) directory.') 
    
    # Change back to the original directory. 
    os.chdir(default_dir) 
    logger.debug(f'----- Changed to original directory.') 

    return ls_tickers


# %%
# --------------------------------------------------------------
# Read File.
# --------------------------------------------------------------

@st.cache(persist=True)
def read_pickle(
        etf_dir:Text, 
        ticker:Text, 
        filename:Text, 
        get_idx:Optional[int]=None
    ) -> Dict[Text, pd.DataFrame]: 
    
    '''
    Purpose : 
        Read pickle file which contains a tuple of dict obj. Each dict obj 
        contains multiple dataframes. 

    Input   :
        etf_dir : Str. Full absolute path for the ETF directory. 
        ticker  : Str. Ticker symbol. 
        filename: Str. Name of the pickle file. 
        get_idx : Int. To get the specified internal tuple obj from an 
                          external tuple if the pickle contains a tuple of tuples, 
                          
    Output  : 
        Dict obj containing multiple dataframes. 
    '''

    logger.info('Start running (read_pickle) function.')

    # REFINE: Need to test how the data is being extracted on Streamlit Sharing. 
    # Change directory. 
    default_dir = os.getcwd()
    os.chdir(os.environ['DATA_ABS_DIR'])
    logger.debug(f'----- Changed to the data warehouse directory.') 

    # Path to the directory that contains all the pickle files. 
    storage_dir = os.path.join(os.getcwd(), 'docs', 'dataset', etf_dir, ticker, 'storage') 

    try:
        with open(f'{storage_dir}/{filename}', 'rb') as in_file: 
            # Get the second dict obj which contains the statistics data from the tuple 
            # if the pickle obj doesn't contain a tuple of tuples. 
            pivot_stats = pd.read_pickle(in_file)[get_idx][1] if isinstance(get_idx, int) else pd.read_pickle(in_file)[1] 
            logger.debug(f'----- Read data from ({filename}) file.') 
    except: 
        logger.exception(f'----- Exception occurs while trying to read data from ({filename}) file.') 

    # Change back to the original directory. 
    os.chdir(default_dir) 
    logger.debug(f'----- Changed to original directory.') 

    return pivot_stats 


# %%
# --------------------------------------------------------------
# Display Price Change Table.
# --------------------------------------------------------------

def formatting_dataframe(df, freq):
    '''
    Purpose: 
        Formatting the dataframe. 

    Input  :
        df  : Dataframe. 
        freq: Str. Must be either monthly / weekly / daily_by_trdr_day / daily_by_weekday. 
        
    Return :
        Formatted dataframe.
    '''
    
    df_copy = df.copy()
    
    # Rearrange the column names. 
    columns = df_copy.columns.tolist()
    freq_to_compare = set(['monthly', 'weekly', 'first_trdr_dom', 'super_day', 'santa_rally'])
    col_idx = 1 if freq in freq_to_compare else 2 
    df_copy = df_copy.loc[:, columns[-col_idx:] + columns[:-col_idx]]
    
    # Apply formatting. 
    df_formatted = df_copy.style.format(formatter={
        "avg_diff": "{:.3%}", 
        "med_diff": "{:.3%}", 
        "tot_diff": "{:.3%}",
        "max_diff": "{:.3%}",
        "min_diff": "{:.3%}",
        "std_diff": "{:.3%}",
        "pos_avg_diff": "{:.3%}",
        "neg_avg_diff": "{:.3%}",
        "up_prob": "{:.2%}",
        "down_prob": "{:.2%}",})\
    .hide_index()\
    .highlight_null(null_color='gray')\
    .applymap(lambda x: f'background-color: {"lightblue" if x > 0 else ""}', subset=['up_overall'])\
    .applymap(lambda x: f'background-color: {"lightblue" if x >= .70 else ""}', subset=['up_prob','down_prob'])\
    .bar(align='mid', color=['#FFA07A', 'lightgreen'], axis=0, 
         subset=['avg_diff', 'med_diff', 'tot_diff', 'pos_avg_diff', 'neg_avg_diff'])

    # Get the current month or week of the year. 
    today, freq_col = datetime.today().month, 'month'
    if freq in set(['weekly','daily_by_weekday']):
        today, freq_col = datetime.today().isocalendar()[1], 'week'

    # Highlight today (light blue). 
    if freq in set(['monthly', 'weekly', 'daily_by_trdr_day', 'daily_by_weekday']): 
        df_formatted = df_formatted.applymap(
            lambda x: f'background-color: {"lightblue" if x == today else ""}', subset=[freq_col]
        )  
    return df_formatted


def styling_dataframe(pivot_stats:Dict[Text, pd.DataFrame]) -> Dict[Text, pd.DataFrame]:
    '''
    Purpose: 
        (Depreciated) Style the dataframe. 

    Input  :
        pivot_stats       : Dict. Containing multiple pivot tables (dataframes). 
        pivot_stats_styled: (Depreciated) Dict. To store the styled pivot tables (dataframes). 
        freq_keys         : (Depreciated) List. Must contain monthly, weekly, 
                            daily_by_trdr_day, daily_by_weekday. 
        
    Return :
        Return styled pivot tables (dataframes).

    Notice : 
        This function is only useful if Streamlit can cache all the style dataframes. 
        Since Streamlit is unable to save the styled dataframes in PICKLE to perform 
        caching, it defeats the purpose of this function. 
    '''

    pivot_stats_styled = {}
    
    # Extract the relevant keys with regex. 
    for freq in FREQ_KEYS:    
        re_compile = re.compile(f'(?:{freq})(?:_R.*Yr)?(?!_)')
        stats_keys = list( filter(re_compile.match, pivot_stats.keys()) )
        
        # Perform formatting for multiple dataframes for each 'freq'. 
        for key in stats_keys: 
            pivot_stats_styled[key] = formatting_dataframe(pivot_stats[key], freq) 
    return pivot_stats_styled


def display_styled_table(
        pivot_stats:Dict[Text, pd.DataFrame], 
        pivot_stats_key:Text, 
        yr_range:Text, 
        col_filter_by:Optional[Text]=None, 
        val_filter_to:Optional[List[Text]]=None, 
    ) -> pd.DataFrame:

    '''
    Purpose : 
        Style the dataframe. 

    Input   : 
        pivot_stats  : Dict. Containing multiple pivot tables (dataframes). 
        freq         : Str. Must be monthly / weekly / daily_by_trdr_day / daily_by_weekday. 
        yr_range     : Str. Year range. 
        col_filter_by: Str. The column name to perform filtering. 
        val_filter_to: Str. The value for filtering the data. 

    Return  :
        Return specific styled pivot table (dataframe). 
    '''
    
    stats_key = pivot_stats_key if yr_range == 'max_yr' else f'{pivot_stats_key}_{yr_range}' 
    if (
        pivot_stats_key == 'compiled_holiday'
        or pivot_stats_key == 'compiled_tww'
        or pivot_stats_key == 'first_trdr_dom_by_month'
        or pivot_stats_key == 'super_day_by_month'
    ): 
        to_filter = pivot_stats[stats_key][col_filter_by].isin(val_filter_to)
        return formatting_dataframe(pivot_stats[stats_key].loc[to_filter,:], pivot_stats_key) 
    return formatting_dataframe(pivot_stats[stats_key], pivot_stats_key) 
    

# %%
# --------------------------------------------------------------
# Plot Price Change.
# --------------------------------------------------------------

def plot_price_diff(
        pivot_stats:Dict[Text, pd.DataFrame], 
        freq:Text, 
        yr_range:Text, 
        period_spec:Optional[int]=None, 
    ) -> Tuple:

    '''
    Purpose: 
        Visualise the price change.

    Input  :
        pivot_stats : Str. Ticker symbol.
        freq        : Str. Must be monthly / weekly / daily_by_trdr_day / daily_by_weekday. 
        yr_range    : Str. Year range. 
        period_spec : Int. To indicate the specific period for either month or week. 

    Return :
        Tuple obj containing the holoview plots.
    '''

    logger.info('Start running (plot_price_diff) function.')

    # Look for the dataframe within the dictionary. 
    pivot_data = pivot_stats[freq] if yr_range == 'max_yr' else pivot_stats[f'{freq}_{yr_range}']

    # Horizontal lines for probability. 
    upper_prob_hline = hv.HLine(0.7).opts(line_width=1, color='black')
    lower_prob_hline = hv.HLine(0.3).opts(line_width=1, color='black')

    if freq in ['daily_by_trdr_day', 'daily_by_weekday']:
        try: 
            # Filter the data to that specific period. 
            period = 'month' if freq == 'daily_by_trdr_day' else 'week' 
            pivot_data = pivot_data.loc[pivot_data[period] == period_spec,:].copy()

            # Visualise the price change by month or week. 
            errorbar = pivot_data.hvplot.errorbars(y='avg_diff', yerr1='std_diff') 
            bar_avg_diff = pivot_data.hvplot(kind='bar', y='avg_diff', width=HV_PN_WIDTH, tools=HV_TOOLS_FOR_TICKER)
            logger.debug('----- Plotted (bar_avg_diff).')

            # Visualise the probability counts by month or week. 
            bar_up_prob = pivot_data.hvplot(kind='bar', y='up_prob', width=HV_PN_WIDTH, ylim=(0,1), tools=HV_TOOLS_FOR_TICKER)
            logger.debug('----- Plotted (bar_up_prob).')

            # Visualise up and down counts by month or week. 
            bar_counts = pivot_data.hvplot(
                kind='bar', y=['up_counts', 'down_counts'], width=HV_PN_WIDTH, 
                stacked=True, legend='top', tools=HV_TOOLS_FOR_TICKER
            )
            logger.debug('----- Plotted (bar_counts).')
        except: 
            logger.exception('----- Exception occurs while trying to plot the graph.') 
        
    else:
        # Visualise the price change.
        errorbar = pivot_data.hvplot.errorbars(y='avg_diff', yerr1='std_diff') 
        bar_avg_diff = pivot_data.hvplot(kind='bar', y='avg_diff', width=HV_PN_WIDTH, tools=HV_TOOLS_FOR_TICKER) 
        logger.debug('----- Plotted (bar_avg_diff).')

        # Visualise the probability counts. 
        bar_up_prob = pivot_data.hvplot(kind='bar', y='up_prob', width=HV_PN_WIDTH, ylim=(0,1), tools=HV_TOOLS_FOR_TICKER) 
        logger.debug('----- Plotted (bar_up_prob).')

        # Visualise up and down counts. 
        bar_counts = pivot_data.hvplot(
            kind='bar', y=['up_counts', 'down_counts'], width=HV_PN_WIDTH, 
            stacked=True, legend='top', tools=HV_TOOLS_FOR_TICKER
        )
        logger.debug('----- Plotted (bar_counts).')

    logger.info('Returning the holoview plot objs for (plot_price_diff).')
    return pivot_data, ( (bar_avg_diff * errorbar), (bar_up_prob * upper_prob_hline * lower_prob_hline), bar_counts )


# %%
# --------------------------------------------------------------
# Plot Volume Change.
# --------------------------------------------------------------

def plot_vol_avg(
        pivot_stats:Dict[Text, pd.DataFrame], 
        freq:Text, 
        period_spec:Optional[int]=None, 
        overall_vol:Optional[bool]=None, 
    ) -> Tuple:
    
    '''
    Purpose: 
        Visualise volume difference. 

    Input  :
        pivot_stats : Str. Ticker symbol.
        freq        : Str. Must be monthly / weekly / daily_by_trdr_day / daily_by_weekday. 
        period_spec : Int. To indicate the specific period for either month or week. 
        overall_vol : Boo. To indicate whether or not to compute the overall volume without breakdown. 

    Return :
        Tuple obj containing the holoview plots.
    '''

    logger.info('Start running (plot_vol_avg) function.')

    # Visualise the yearly volume. 
    pivot_data_vol_col = pivot_stats[f'{freq}_avg_vol_col'] 
    bar_yearly_vol = pivot_data_vol_col.hvplot(kind='bar', y='avg_vol_col', width=HV_PN_WIDTH, tools=HV_TOOLS_FOR_TICKER) 
    logger.debug('----- Plotted (bar_yearly_vol).')

    # Look for the dataframe within the dictionary. 
    pivot_data_vol_row = pivot_stats[f'{freq}_avg_vol_row'] 

    # FIX: Level and axis for averaging. 
    if (freq == 'daily_by_trdr_day') or (freq == 'daily_by_weekday'):
        try: 
            period = 'month' if freq == 'daily_by_trdr_day' else 'week' 
            col_for_computing_overall_avg = 'trdr_day' if freq == 'daily_by_trdr_day' else 'weekday' 
            boo_period_spec = pivot_stats[freq][period] == period_spec

            if overall_vol:
                # Set multi-level index for computing (mean) for specific index level at later stage. 
                pivot_data_vol_row_multi_index = pivot_data_vol_row.set_index([period, col_for_computing_overall_avg]).copy()
                
                # Average volume horizontal line. 
                avg_hline = hv.HLine(pivot_data_vol_row_multi_index.mean(level=1, axis=0).mean(axis=0)[0]).opts(line_width=1, color='black')

                # Average volume by month / week. 
                bar_avg_vol = pivot_data_vol_row_multi_index.mean(level=1, axis=0).hvplot(
                    kind='bar', y='avg_vol_row', width=HV_PN_WIDTH, tools=HV_TOOLS_FOR_TICKER
                )
                logger.debug('----- Plotted (bar_avg_vol).')

                # Above and below average counts by month / week. 
                pivot_stats_filtered = pivot_stats[freq].loc[boo_period_spec,:]\
                    .set_index([period, col_for_computing_overall_avg])\
                    .copy()
                bar_counts = pivot_stats_filtered.mean(level=1, axis=0).hvplot(
                    kind='bar', y=['abv_avg_vol_counts','blw_avg_vol_counts'], width=HV_PN_WIDTH, 
                    stacked=True, legend='top', tools=HV_TOOLS_FOR_TICKER
                )
                logger.debug('----- Plotted (bar_counts).')
            else:
                # Filter the data to that specific period. 
                pivot_data_vol_row_filtered = pivot_data_vol_row.loc[pivot_data_vol_row[period] == period_spec,:]

                # Average volume horizontal line. 
                avg_hline = hv.HLine(pivot_data_vol_row_filtered.mean(axis=0)[0]).opts(line_width=1, color='black', tools=HV_TOOLS_FOR_TICKER)

                # Average volume by month / week. 
                bar_avg_vol = pivot_data_vol_row_filtered.hvplot(kind='bar', y='avg_vol_row', width=HV_PN_WIDTH, tools=HV_TOOLS_FOR_TICKER)
                logger.debug('----- Plotted (pbar_avg_vol).')

                # Above and below average counts by month / week. 
                pivot_stats_filtered = pivot_stats[freq].loc[boo_period_spec,:]
                bar_counts = pivot_stats_filtered.hvplot(
                    kind='bar', y=['abv_avg_vol_counts','blw_avg_vol_counts'], width=HV_PN_WIDTH, 
                    stacked=True, legend='top', tools=HV_TOOLS_FOR_TICKER
                )
                logger.debug('----- Plotted (bar_counts).')
        except: 
            logger.exception('----- Exception occurs while trying to plot the graph.') 

    else:
        # Average volume. 
        avg_hline = hv.HLine(pivot_data_vol_row.mean(axis=0)[0]).opts(line_width=1, color='black', tools=HV_TOOLS_FOR_TICKER)

        # Average volume by month / week. 
        bar_avg_vol = pivot_data_vol_row.hvplot(kind='bar', y='avg_vol_row', width=HV_PN_WIDTH, tools=HV_TOOLS_FOR_TICKER) 
        logger.debug('----- Plotted (pbar_avg_vol).')

        # Above and below average counts by month / week. 
        bar_counts = pivot_stats[freq].hvplot(
            kind='bar', y=['abv_avg_vol_counts','blw_avg_vol_counts'], 
            width=HV_PN_WIDTH, stacked=True, legend='top', tools=HV_TOOLS_FOR_TICKER
        )
        logger.debug('----- Plotted (bar_counts).')

    logger.info('Returning the holoview plot objs for (plot_vol_avg).')
    return (pivot_data_vol_col, pivot_data_vol_row), ( bar_yearly_vol, (bar_avg_vol * avg_hline), bar_counts )


# --------------------------------------------------------------
# Plot Price Change For Holiday.
# --------------------------------------------------------------

def plot_price_diff_holiday_period(        
        pivot_stats:Dict[Text, pd.DataFrame], 
        holiday_key:Text, 
        yr_range:Text, 
    ) -> Tuple:

    '''
    Purpose: 
        Visualise the price change for holiday period. 

    Input  :
        pivot_stats : Str. Ticker symbol.
        holiday_key : Str. Specify the name of the holiday. 
        yr_range    : Str. Year range. 
    
    Return :
        Tuple obj containing the holoview plots.
    '''

    logger.info('Start running (plot_price_diff_holiday_period) function.')

    # Look for the dataframe within the dictionary. 
    pivot_data = pivot_stats['compiled_holiday'] if yr_range == 'max_yr' else pivot_stats[f'compiled_holiday_{yr_range}']
    boo_holiday = pivot_data['holiday_category'] == holiday_key

    # Visualise the price change.
    errorbar = pivot_data.loc[boo_holiday, :].hvplot.errorbars(y='avg_diff', yerr1='std_diff') 
    bar_avg_diff = pivot_data.loc[boo_holiday, :].hvplot(kind='bar', y='avg_diff', width=HV_PN_WIDTH, tools=HV_TOOLS_FOR_TICKER)
    logger.debug('----- Plotted (bar_avg_diff).')

    # Visualise the probability and horizontal lines for probability. 
    upper_prob_hline = hv.HLine(0.7).opts(line_width=1, color='black')
    lower_prob_hline = hv.HLine(0.3).opts(line_width=1, color='black')
    bar_up_prob = pivot_data.loc[boo_holiday, :].hvplot(kind='bar', y='up_prob', width=HV_PN_WIDTH, ylim=(0,1), tools=HV_TOOLS_FOR_TICKER)
    logger.debug('----- Plotted (bar_up_prob).')

    # Visualise up and down counts. 
    bar_counts = pivot_data.loc[boo_holiday, :].hvplot(
        kind='bar', y=['up_counts', 'down_counts'], 
        width=HV_PN_WIDTH, stacked=True, legend='top', tools=HV_TOOLS_FOR_TICKER
    )
    logger.debug('----- Plotted (bar_counts).')

    logger.info('Returning the holoview plot objs for (plot_price_diff_holiday_period).')
    return pivot_data, ( (bar_avg_diff * errorbar), (bar_up_prob * upper_prob_hline * lower_prob_hline), bar_counts )


# --------------------------------------------------------------
# Plot Price Change For TWW.
# --------------------------------------------------------------

def plot_price_diff_tww_period(
        pivot_stats:Dict[Text, pd.DataFrame], 
        tww_key:Text, 
        yr_range:Text, 
        show_weekly:Optional[bool]=None, 
    ) -> Tuple: 
    '''
    Purpose: 
        Visualise the price change for TWW period. 

    Input  :
        pivot_stats : Str. Ticker symbol.
        tww_key     : Str. Specify the name of the holiday. 
        yr_range    : Str. Year range. 
        show_weekly : Boo. To indicate whether to show the TWW by weekly data.  

    Return :
        Tuple obj containing the holoview plots.
    '''

    logger.info('Start running (plot_price_diff_tww_period) function.')

    # Look for the dataframe within the dictionary. 
    pivot_data = pivot_stats['compiled_tww'] if yr_range == 'max_yr' else pivot_stats[f'compiled_tww_{yr_range}']
    boo_tww = pivot_data['tww_period'] == tww_key
    boo_tww_week_aft = pivot_data['tww_period'] == f'{tww_key}_week_aft'
    pivot_data_tww = pivot_data.loc[boo_tww, :]
    pivot_data_tww_week_aft = pivot_data.loc[boo_tww_week_aft, :]

    upper_prob_hline = hv.HLine(0.7).opts(line_width=1, color='black')
    lower_prob_hline = hv.HLine(0.3).opts(line_width=1, color='black')

    # Visualise the price change.
    bar_avg_diff_tww = pivot_data_tww.hvplot(
        kind='bar', y='avg_diff', width=HV_PN_WIDTH, shared_axes=False, tools=HV_TOOLS_FOR_TICKER)
    bar_avg_diff_tww_week_aft = pivot_data_tww_week_aft.hvplot(
        kind='bar', y='avg_diff', width=HV_PN_WIDTH, shared_axes=False, tools=HV_TOOLS_FOR_TICKER)
    logger.debug('----- Plotted (bar_avg_diff).')

    # Visualise the probability. 
    bar_up_prob_tww = pivot_data_tww.hvplot(
        kind='bar', y='up_prob', width=HV_PN_WIDTH, ylim=(0,1), tools=HV_TOOLS_FOR_TICKER
    )
    bar_up_prob_tww_week_aft = pivot_data_tww_week_aft.hvplot(
        kind='bar', y='up_prob', width=HV_PN_WIDTH, ylim=(0,1), tools=HV_TOOLS_FOR_TICKER
    )
    logger.debug('----- Plotted (bar_up_prob).')

    # Visualise up and down counts. 
    bar_counts_tww = pivot_data_tww.hvplot(
        kind='bar', y=['up_counts','down_counts'], 
        width=HV_PN_WIDTH, stacked=False, legend='top', tools=HV_TOOLS_FOR_TICKER
    )
    bar_counts_tww_week_aft = pivot_data_tww_week_aft.hvplot(
        kind='bar', y=['up_counts','down_counts'], 
        width=HV_PN_WIDTH, stacked=False, legend='top', tools=HV_TOOLS_FOR_TICKER
    )
    logger.debug('----- Plotted (bar_counts).')

    logger.info('Returning the holoview plot objs for (plot_price_diff_tww_period).')
    return pivot_data, (
        (bar_avg_diff_tww * bar_avg_diff_tww_week_aft), 
        (bar_up_prob_tww * bar_up_prob_tww_week_aft * upper_prob_hline * lower_prob_hline), 
        (bar_counts_tww, bar_counts_tww_week_aft), 
    )
    

# --------------------------------------------------------------
# Plot Price Change For Special Period.
# --------------------------------------------------------------

def plot_price_diff_special_period(        
        pivot_stats:Dict[Text, pd.DataFrame], 
        special_period_key:Text, 
        yr_range:Text, 
        period_spec:int, 
    ) -> Tuple:

    '''
    Purpose: 
        Visualise the price change for special period. 

    Input  :
        pivot_stats         : Str. Ticker symbol.
        special_period_key  : Str. Specify the name of the holiday. 
        yr_range            : Str. Year range. 
        period_spec         : Int. To indicate the specific month. 

    Return :
        Tuple obj containing the holoview plots.
    '''

    logger.info('Start running (plot_price_diff_special_period) function.')

    # Look for the dataframe within the dictionary. 
    pivot_data = pivot_stats[special_period_key] if yr_range == 'max_yr' else pivot_stats[f'{special_period_key}_{yr_range}']

    upper_prob_hline = hv.HLine(0.7).opts(line_width=1, color='black')
    lower_prob_hline = hv.HLine(0.3).opts(line_width=1, color='black')

    if special_period_key == 'first_trdr_dom_by_month' or special_period_key == 'super_day_by_month': 
        # Filter the data to that specific period. 
        period = 'month' if special_period_key == 'first_trdr_dom_by_month' else 'super_day_spec_month' 
        pivot_data = pivot_data.loc[pivot_data[period] == period_spec,:].copy()

        # Visualise the price change by month or week. 
        errorbar = pivot_data.hvplot.errorbars(y='avg_diff', yerr1='std_diff') 
        bar_avg_diff = pivot_data.hvplot(kind='bar', y='avg_diff', width=HV_PN_WIDTH, tools=HV_TOOLS_FOR_TICKER)

        # Visualise the probability counts by month or week. 
        bar_up_prob = pivot_data.hvplot(
            kind='bar', y='up_prob', width=HV_PN_WIDTH, ylim=(0,1), tools=HV_TOOLS_FOR_TICKER
        )

        # Visualise up and down counts by month or week. 
        bar_counts = pivot_data.hvplot(
            kind='bar', y=['up_counts', 'down_counts'], width=HV_PN_WIDTH, stacked=True, legend='top', tools=HV_TOOLS_FOR_TICKER
        )

    else:
        # Visualise the price change.
        errorbar = pivot_data.hvplot.errorbars(y='avg_diff', yerr1='std_diff') 
        bar_avg_diff = pivot_data.hvplot(kind='bar', y='avg_diff', width=HV_PN_WIDTH, tools=HV_TOOLS_FOR_TICKER)
        logger.debug('----- Plotted (bar_avg_diff).')

        # Visualise the probability counts. 
        bar_up_prob = pivot_data.hvplot(kind='bar', y='up_prob', width=HV_PN_WIDTH, ylim=(0,1), tools=HV_TOOLS_FOR_TICKER)
        logger.debug('----- Plotted (bar_up_prob).')

        # Visualise up and down counts. 
        bar_counts = pivot_data.hvplot(
            kind='bar', y=['up_counts', 'down_counts'], width=HV_PN_WIDTH, 
            stacked=True, legend='top', tools=HV_TOOLS_FOR_TICKER
        )
        logger.debug('----- Plotted (bar_counts).')

    logger.info('Returning the holoview plot objs for (plot_price_diff_special_period).')
    return pivot_data, ( (bar_avg_diff * errorbar), (bar_up_prob * upper_prob_hline * lower_prob_hline), bar_counts )
