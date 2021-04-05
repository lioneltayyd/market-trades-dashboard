# %%
# # Python modules.
import logging
import streamlit as st
import holoviews as hv
import bokeh
from datetime import datetime

# Holoview config. 
hv.extension('bokeh')

# Personal modules. 
from autovisualise_data import ticker_plot, fred_plot
from config.config_dashboard import (
    ST_MAX_WIDTH,
    ST_PADDING_TOP,
    ST_PADDING_RIGHT,
    ST_PADDING_LEFT,
    ST_PADDING_BOTTOM,
    ST_COLOR,
    ST_BACKGROUND_COLOR,
    ST_TABS,
    FORMAT_WIDGET_OPTIONS_TITLE_CASE, 
    FORMAT_WIDGET_OPTIONS_LOWERCASE, 
    XLIM, 
)
from config.config_logger import setup_logger
from config.config import (
    LOG_PROCESSING_FILEPATH, ETF_EQUITY, 
    YR_RANGE, FREQ_KEYS, HOLIDAYS_KEYS, 
    SPECIAL_DAYS_KEYS, FRED_DATA_GROUPING, 
)


# %%
# --------------------------------------------------------------
# Logger setup. 
# --------------------------------------------------------------

logger = logging.getLogger(__name__)
logger, file_handler, stream_handler = setup_logger(logger, LOG_PROCESSING_FILEPATH) 


# %%
# ----------------------------------------------------------------------
# CSS Styling
# ----------------------------------------------------------------------

st.markdown(
    f'''
    <style>
        .reportview-container .main .block-container {{
            max-width: {ST_MAX_WIDTH}px;
            padding-top: {ST_PADDING_TOP}rem;
            padding-right: {ST_PADDING_RIGHT}rem;
            padding-left: {ST_PADDING_LEFT}rem;
            padding-bottom: {ST_PADDING_BOTTOM}rem;
        }}
        .reportview-container .main {{
            color: {ST_COLOR};
            background-color: {ST_BACKGROUND_COLOR};
        }}
    </style>
    ''', 
    unsafe_allow_html=True
)


# %%
# ----------------------------------------------------------------------
# Initial Setup 
# ----------------------------------------------------------------------

# Set the title. 
st.title('''ETF Seasonal Trend''')

# For selecting the tabs. 
selector_main_tabs = st.selectbox(label='Dashboard Tabs', options=ST_TABS, index=0) 

col_1, col_2 = st.beta_columns(2)

if selector_main_tabs in ST_TABS[:5]:
    with col_1: 
        # For selecting the ETF directory to get a list of ticker options for that directory. 
        etf_categories = ['ETF_sector'] + ['/'.join(['ETF_equity', etf]) for etf in ETF_EQUITY] 
        selector_etf_dir = st.selectbox(label='ETF Categories', options=etf_categories, index=0) 
    with col_2: 
        # For selecting the ticker symbol. 
        selector_ticker_option = st.selectbox(label='Ticker Options', options=ticker_plot.get_ticker_options(selector_etf_dir), index=0) 

elif selector_main_tabs == ST_TABS[5]:
    # For selecting the economic data category. 
    selector_eco_category = st.selectbox(
        label='Economic Data Category', options=list(FRED_DATA_GROUPING.keys()), index=0, format_func=FORMAT_WIDGET_OPTIONS_TITLE_CASE)


# %%
# ----------------------------------------------------------------------
# Develop Sidebar Widget 
# ----------------------------------------------------------------------

st.sidebar.header('''For Data Exploration''')

if selector_main_tabs in ST_TABS[:5]:
    # For selecting year range category.
    selector_yr_range = st.sidebar.selectbox(
        label='Year Range', options=YR_RANGE, index=0, format_func=FORMAT_WIDGET_OPTIONS_TITLE_CASE
    )

if selector_main_tabs == ST_TABS[0] or selector_main_tabs == ST_TABS[1]:
    # For selecting date interval.
    selector_interval = st.sidebar.selectbox(
        label='Date Interval', options=FREQ_KEYS, index=0, format_func=FORMAT_WIDGET_OPTIONS_TITLE_CASE
    ) 

    # For selecting the period such as month / week number. 
    slider_period = None 
    if selector_interval == 'daily_by_trdr_day': 
        slider_period = st.sidebar.slider(label='Period', min_value=1, max_value=12, value=1, step=1) 
    elif selector_interval == 'daily_by_weekday': 
        slider_period = st.sidebar.slider(label='Period', min_value=1, max_value=53, value=1, step=1) 

# For selecting the holiday. 
if selector_main_tabs == ST_TABS[2]:
    selector_unique_period = st.sidebar.selectbox(
        label='Holiday Period', options=HOLIDAYS_KEYS, index=0, format_func=FORMAT_WIDGET_OPTIONS_TITLE_CASE
    ) 

# For selecting the TWW period. 
if selector_main_tabs == ST_TABS[3]:
    selector_unique_period = st.sidebar.selectbox(
        label='TWW Period', options=SPECIAL_DAYS_KEYS[5:9], index=0, format_func=FORMAT_WIDGET_OPTIONS_TITLE_CASE
    ) 
    
# For selecting the special period. 
if selector_main_tabs == ST_TABS[4]:
    selector_unique_period = st.sidebar.selectbox(
        label='Special Period', options=SPECIAL_DAYS_KEYS[:5], index=0, format_func=FORMAT_WIDGET_OPTIONS_TITLE_CASE
    ) 
    slider_unique_period_month = None
    if selector_unique_period == 'first_trdr_dom_by_month' or selector_unique_period == 'super_day_by_month':
        slider_unique_period_month = st.sidebar.slider(label='Period', min_value=1, max_value=12, value=1, step=1) 

if selector_main_tabs == ST_TABS[5]:
    # For selecting the economic category and showing recession. 
    multiselector_eco_data_1 = st.sidebar.multiselect(
        label='Select Economic Data For 1st Chart (Max 2)', options=FRED_DATA_GROUPING[selector_eco_category], 
        default=FRED_DATA_GROUPING[selector_eco_category][0], format_func=FORMAT_WIDGET_OPTIONS_LOWERCASE, 
    )
    multiselector_eco_data_2 = st.sidebar.multiselect(
        label='Select Economic Data For 2nd Chart (Max 2)', options=FRED_DATA_GROUPING[selector_eco_category], 
        default=FRED_DATA_GROUPING[selector_eco_category][1], format_func=FORMAT_WIDGET_OPTIONS_LOWERCASE, 
    )
    try: 
        multiselector_eco_data_3 = st.sidebar.multiselect(
            label='Select Economic Data For 3rd Chart (Max 2)', options=FRED_DATA_GROUPING[selector_eco_category], 
            default=FRED_DATA_GROUPING[selector_eco_category][2], format_func=FORMAT_WIDGET_OPTIONS_LOWERCASE, 
        )
    except: 
        multiselector_eco_data_3 = None
    
    # For selecting the date range.
    slider_date_range = st.sidebar.slider('Period', datetime(1960,1,1), datetime(datetime.today().year, 12, 1), XLIM)

    # For showing economic recession. 
    checkbox_show_recession = st.sidebar.checkbox(f'''Show Recession / Bear Period''', value=True)


# %%
# ----------------------------------------------------------------------
# Develop Dashboard 
# ----------------------------------------------------------------------

if selector_main_tabs == ST_TABS[0]:
    # Read the price data. 
    pivot_stats = ticker_plot.read_pickle(selector_etf_dir, selector_ticker_option, 'pivot_stats.pickle')

    # Create multiple plots. 
    pivot_data, multi_plots = ticker_plot.plot_price_diff(pivot_stats, selector_interval, selector_yr_range, slider_period)
    bar_avg_diff, bar_up_prob, bar_counts = multi_plots 

    # Display the table data for price difference. 
    with st.beta_expander(label='Price Difference Table'): 
        st.table(ticker_plot.display_styled_table(pivot_stats, selector_interval, selector_yr_range)) 

    # Display the plot for price difference. 
    with st.beta_expander(label='Price Difference Plots', expanded=True): 
        st.header('__Average Price Difference__')
        st.bokeh_chart(hv.render(bar_avg_diff, backend='bokeh'), use_container_width=True)
        st.header('__Up Probability__')
        st.bokeh_chart(hv.render(bar_up_prob, backend='bokeh'), use_container_width=True)
        st.header('__Up / Down Counts__')
        st.bokeh_chart(hv.render(bar_counts, backend='bokeh'), use_container_width=True) 

elif selector_main_tabs == ST_TABS[1]:
    # Read the trade volume data. 
    pivot_stats = ticker_plot.read_pickle(selector_etf_dir, selector_ticker_option, 'pivot_vol_stats.pickle')

    checkbox_overall_vol = None
    if selector_interval == 'daily_by_trdr_day' or selector_interval == 'daily_by_weekday': 
        # To indicate whether or not to compute the overall volume without breakdown. 
        checkbox_overall_vol = st.checkbox(label='Compute Overall Vol Diff', value=False) 

    # Create mutliple plots. 
    pivot_data_vol, multi_plots = ticker_plot.plot_vol_avg(
        pivot_stats, selector_interval, slider_period, checkbox_overall_vol
    ) 
    pivot_data_vol_col, pivot_data_vol_row = pivot_data_vol
    bar_yearly_vol, bar_avg_vol, bar_vol_counts = multi_plots

    # Display the plot for volume average. 
    with st.beta_expander(label='Volume Difference Plots', expanded=True): 
        st.header('__Yearly Average Volume__')
        st.bokeh_chart(hv.render(bar_yearly_vol, backend='bokeh'), use_container_width=True)
        st.header('__Monthly Average Volume__')
        st.bokeh_chart(hv.render(bar_avg_vol, backend='bokeh'), use_container_width=True)
        st.header('__Volume Above Monthly Average Counts__')
        st.bokeh_chart(hv.render(bar_vol_counts, backend='bokeh'), use_container_width=True)

elif selector_main_tabs == ST_TABS[2]:
    # Read the price data. 
    pivot_stats = ticker_plot.read_pickle(selector_etf_dir, selector_ticker_option, 'pivot_unique_days.pickle', get_idx=0)

    # Create multiple plots. 
    pivot_data, multi_plots = ticker_plot.plot_price_diff_holiday_period(pivot_stats, selector_unique_period, selector_yr_range) 
    bar_avg_diff, bar_up_prob, bar_counts = multi_plots 

    # Display the table data for price difference. 
    with st.beta_expander(label='Price Difference Table'): 
        st.table(ticker_plot.display_styled_table(
            pivot_stats, 'compiled_holiday', selector_yr_range, 'holiday_category', [selector_unique_period]
        )) 

    # Display the plot for price difference. 
    with st.beta_expander(label='Price Difference Plots', expanded=True): 
        st.header('__Average Price Difference__')
        st.bokeh_chart(hv.render(bar_avg_diff, backend='bokeh'), use_container_width=True)
        st.header('__Up Probability__')
        st.bokeh_chart(hv.render(bar_up_prob, backend='bokeh'), use_container_width=True)
        st.header('__Up / Down Counts__')
        st.bokeh_chart(hv.render(bar_counts, backend='bokeh'), use_container_width=True) 

elif selector_main_tabs == ST_TABS[3]:
    # To indicate whether or not to compute the show the TWW by weekly data. 
    checkbox_show_weekly = None
    checkbox_show_weekly = st.checkbox(label='Show Weekly TWW', value=False)
    
    # Change the data baed on the 'checkbox_show_weekly' value. 
    get_idx = 2 if checkbox_show_weekly else 1

    # Read the price data. 
    pivot_stats = ticker_plot.read_pickle(selector_etf_dir, selector_ticker_option, 'pivot_unique_days.pickle', get_idx=get_idx)

    # Create multiple plots. 
    pivot_data, multi_plots = ticker_plot.plot_price_diff_tww_period(pivot_stats, selector_unique_period, selector_yr_range) 
    bar_avg_diff, bar_up_prob, bar_counts = multi_plots 

    # Display the table data for price difference. 
    with st.beta_expander(label='Price Difference Table'): 
        st.table(ticker_plot.display_styled_table(
            pivot_stats, 'compiled_tww', selector_yr_range, 'tww_period', [selector_unique_period, f'{selector_unique_period}_week_aft']
        ))

    # Display the plot for price difference. 
    with st.beta_expander(label='Price Difference Plots', expanded=True): 
        st.header('__Average Price Difference__')
        st.text('Week before & after TWW')
        st.bokeh_chart(hv.render(bar_avg_diff, backend='bokeh'), use_container_width=True)
        st.header('__Up Probability__')
        st.text('Week before & after TWW')
        st.bokeh_chart(hv.render(bar_up_prob, backend='bokeh'), use_container_width=True)
        st.header('__Up / Down Counts__')
        st.text('Week before TWW')
        st.bokeh_chart(hv.render(bar_counts[0], backend='bokeh'), use_container_width=True) 
        st.text('Week after TWW')
        st.bokeh_chart(hv.render(bar_counts[1], backend='bokeh'), use_container_width=True) 

elif selector_main_tabs == ST_TABS[4]:
    # Read the price data. 
    pivot_stats = ticker_plot.read_pickle(selector_etf_dir, selector_ticker_option, 'pivot_unique_days.pickle', get_idx=1)

    # Create multiple plots. 
    pivot_data, multi_plots = ticker_plot.plot_price_diff_special_period(
        pivot_stats, selector_unique_period, selector_yr_range, slider_unique_period_month
    ) 
    bar_avg_diff, bar_up_prob, bar_counts = multi_plots 

    # Display the table data for price difference. 
    with st.beta_expander(label='Price Difference Table'): 
        period_col = None
        if selector_unique_period == 'first_trdr_dom_by_month' or selector_unique_period == 'super_day_by_month':
            period_col = 'month' if selector_unique_period == 'first_trdr_dom_by_month' else 'super_day_spec_month' 

        st.table(ticker_plot.display_styled_table(
            pivot_stats, selector_unique_period, selector_yr_range, period_col, [slider_unique_period_month]
        ))

    # Display the plot for price difference. 
    with st.beta_expander(label='Price Difference Plots', expanded=True): 
        st.header('__Average Price Difference__')
        st.bokeh_chart(hv.render(bar_avg_diff, backend='bokeh'), use_container_width=True)
        st.header('__Up Probability__')
        st.bokeh_chart(hv.render(bar_up_prob, backend='bokeh'), use_container_width=True)
        st.header('__Up / Down Counts__')
        st.bokeh_chart(hv.render(bar_counts, backend='bokeh'), use_container_width=True) 

elif selector_main_tabs == ST_TABS[5]:
    # Read the fred data. 
    fred_data = fred_plot.read_pickle('fred_data.pickle')

    # Create plots. 
    line_eco_trend_1 = fred_plot.plot_eco_trend(fred_data, multiselector_eco_data_1, slider_date_range, checkbox_show_recession) 
    line_eco_trend_2 = fred_plot.plot_eco_trend(fred_data, multiselector_eco_data_2, slider_date_range, checkbox_show_recession) 
    line_eco_trend_3 = fred_plot.plot_eco_trend(fred_data, multiselector_eco_data_3, slider_date_range, checkbox_show_recession) 
    
    # Display plots for fred data. 
    with st.beta_expander(label=f'{selector_eco_category} Trend'.title(), expanded=True): 
        st.bokeh_chart(hv.render(line_eco_trend_1, backend='bokeh'), use_container_width=True)
        st.bokeh_chart(hv.render(line_eco_trend_2, backend='bokeh'), use_container_width=True)
        try: 
            st.bokeh_chart(hv.render(line_eco_trend_3, backend='bokeh'), use_container_width=True)
        except: pass
