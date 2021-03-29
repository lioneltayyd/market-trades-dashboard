

# %%
import os, logging
import pandas as pd
import streamlit as st
import holoviews as hv
import hvplot.pandas

from typing import Dict, List, Text, Optional, Tuple

# Holoview config. 
hv.extension('bokeh')

# Pandas config. 
pd.options.display.float_format = '{:,.5f}'.format 

# Personal modules. 
from config.config import (
    LOG_PROCESSING_FILEPATH, 
    FRED_DATA_ABS_DIR, 
)
from config.config_logger import setup_logger
from config.config_dashboard import (
    HV_PN_WIDTH, 
    HV_PN_HEIGHT, 
    HV_TOOLS_FOR_ECO, 
    XLIM, 
    V_SPAN_ECO_RECESSION
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

@st.cache(persist=True)
def read_pickle(filename:Text) -> Dict[Text, pd.DataFrame]: 
    
    '''
    Purpose : 
        Read pickle file which contains a dict obj. 

    Input   :
        eco_data_dir: Str. Full absolute path for the ETF directory. 
        filename    : Str. Name of the pickle file. 
                          
    Output  : 
        Dict obj containing multiple dataframes. 
    '''

    logger.info('Start running (read_pickle) function.')

    # REFINE: Need to test how the data is being extracted on Streamlit Sharing. 
    # Change directory. 
    default_dir = os.getcwd()
    os.chdir(os.environ['DATA_ABS_DIR'])
    logger.debug(f'----- Changed to the data warehouse directory.') 
    print(f'---------- {os.getcwd()}')
    print(f'---------- {FRED_DATA_ABS_DIR}/{filename}')

    try:
        with open(f'{FRED_DATA_ABS_DIR}/{filename}', 'rb') as in_file: 
            fred_data = pd.read_pickle(in_file) 
            logger.debug(f'----- Read data from ({filename}) file.') 
    except: 
        logger.exception(f'----- Exception occurs while trying to read data from ({filename}) file.') 

    # Change back to the original directory. 
    os.chdir(default_dir) 
    logger.debug(f'----- Changed to original directory.') 

    return fred_data 


# %%
# --------------------------------------------------------------
# Decorator
# --------------------------------------------------------------

# To perform combination for certain economic data plots. 
def combine_plots(plot_func):
    logger.info('Start running (combine_plots) decorator.')

    def wrapper(eco_data, eco_cat, date_range, show_recession):
        # Try creating a plot to see if the data exist. 
        try:
            plot_main = plot_func(eco_data, eco_cat[0], date_range, show_recession)
            plot_add = None
            if show_recession:
                plot_main = plot_main * V_SPAN_ECO_RECESSION
                logger.debug('----- Added economic recession for plot.')
        except Exception: 
            logger.warning(f'----- Data is unavaialble for ({plot_func}).') 
            return None
        
        # If two (max) economic data is selected, creating additional plot. 
        if len(eco_cat) >= 2: 
            plot_add = eco_data[eco_cat[1]].hvplot(
                kind='line', y='value', label=eco_cat[1], width=HV_PN_WIDTH, 
                xlim=date_range, shared_axes=False, tools=HV_TOOLS_FOR_ECO, 
            )
            logger.debug('----- Added additional economic data plot.')

            return (plot_main * plot_add).opts(legend_position='top')

        return plot_main
        
    return wrapper


# %%
# --------------------------------------------------------------
# Plot Economic Data
# --------------------------------------------------------------

@combine_plots
def plot_eco_trend(
        eco_data:pd.DataFrame, 
        eco_cat:List[Text], 
        date_range:Tuple=XLIM, 
        show_recession:bool=False
    ):

    logger.info('Start running (plot_eco_trend) function.')

    line_eco_trend = eco_data[eco_cat].hvplot(
        kind='line', y='value', label=eco_cat, width=HV_PN_WIDTH,
        xlim=date_range, shared_axes=False, tools=HV_TOOLS_FOR_ECO
    )
    logger.debug('----- Plotted (plot_eco_trend).') 

    return  line_eco_trend
