

import os 
import regex as re

# Personal modules. 
from config.config_naming import *


# ----------------------------------------------------------------------
# Date & Year Range.
# ----------------------------------------------------------------------

YR_RANGE = ['max_yr', 'range_20_yr', 'range_15_yr', 'range_10_yr', 'range_5_yr']


# ----------------------------------------------------------------------
# Ticker (Equity).
# ----------------------------------------------------------------------

ETF_EQUITY = [ 
    'PPA', 
    # 'XLB', 'XLE', 'XLF', 'XLI', 'XLP', 'XLU', 'XLV', 'XLY', 'IYR', 
    # 'IYW', 'IYZ', 'XRT', 'XHB',
]


# ----------------------------------------------------------------------
# Directory / File Path.
# ---------------------------------------------------------------------- 

# Logging file path. 
LOG_PROCESSING_FILEPATH = 'logs/runtime/log_processing.log'

# Others.  
PROJECT_PATH = os.getcwd()

# # Path to the ETF directory. 
# ETF_SECTOR_ABS_DIR = os.path.join(os.environ['DATA_ABS_DIR'], 'ETF_sector') 
# ETF_EQUITY_ABS_DIR = os.path.join(os.environ['DATA_ABS_DIR'], 'ETF_equity') 

# Path to the FRED data directory.
os.environ['DATA_ABS_DIR'] = '.'
FRED_DATA_ABS_DIR = os.path.join(os.environ['DATA_ABS_DIR'], 'docs', 'dataset', 'economic_data', 'FRED') 

# # Compile a list of ticker names. 
# re_compile = re.compile(r'(?<!\..*)[A-Z]') 
# LS_ETF_SECTOR = list( filter(re_compile.match, os.listdir(ETF_SECTOR_ABS_DIR)) ) 
# LS_ETF_EQUITY = list( filter(re_compile.match, os.listdir(ETF_EQUITY_ABS_DIR)) ) 


# ----------------------------------------------------------------------
# For Ticker Data Processing. 
# ---------------------------------------------------------------------- 

# Store keys for dictionary indexing. 
FREQ_KEYS = ['monthly', 'weekly', 'daily_by_trdr_day', 'daily_by_weekday']

# Column names for creating pivot tables. 
FREQ_COLS = ['month', 'week', 'trdr_day', 'weekday']

# Store keys for dictionary indexing. 
HOLIDAYS_KEYS = [
    'new_year', 'mar_lut_king_jr', 'valentine', 'president', 
    'good_friday', 'memorial', 'independence', 'labour', 
    'event_911', 'columbus', 'veteran', 'thanksgiving','christmas'
]
SPECIAL_DAYS_KEYS = [
    'first_trdr_dom', 'first_trdr_dom_by_month', 'super_day', 'super_day_by_month',
    'santa_rally', 'tww_q1', 'tww_q2', 'tww_q3', 'tww_q4', 
    'tww_q1_week_aft', 'tww_q2_week_aft', 'tww_q3_week_aft', 'tww_q4_week_aft'
]

# Holidays that falls on specific weekday. 
SPEC_WEEKDAY_HOLIDAYS = ['mar_lut_king_jr', 'president', 'memorial', 'labour', 'columbus', 'thanksgiving']

# Holidays that falls on Friday. 
SPEC_WEEKDAY_HOLIDAYS_BACKWARD = ['good_friday']

# Holidays that falls on specific date.
NON_SPEC_HOLIDAYS = ['independence', 'christmas']

# Observances that falls on specific date.
NON_SPEC_OBSERVANCES = ['valentine', 'event_911', 'veteran']


# ----------------------------------------------------------------------
# For Economic Data Processing 
# ----------------------------------------------------------------------

# FRED economic data grouping. 
FRED_DATA_GROUPING = {
    GROUP_EMPLOYMENT: [
        UNEMPLOY,
        UNEMPLOY_NAT,
        UNEMPLOY_PARTICIPATION,
        POP_GROWTH_YOY,
    ],
    GROUP_EMPLOYMENT: [
        PERSONAL_DISPENSABLE_INC_YOY,
        PERSONAL_CONSUMPTION_EXP_YOY,
        PERSONAL_CONSUMPTION_EXP_REAL_YOY,
        PERSONAL_SAVINGS_RATIO,
        HOUSEHOLD_DEBT,
        MORTGAGE_DEBT,
        CONSUMPTION_DEBT,
    ],
    GROUP_MANUFACT_BUSINESS: [
        INDUSTRY_PRODUCTION,
        CAPACITY_UTILISATION,
        MANUFACT_PRODUCTION,
        MANUFACT_NEW_ORDER_EX_DEF,
        MANUFACT_NEW_ORDER_EX_TRANS,
        ONLINE_SALES_YOY,
        ONLINE_SALES_RATIO,
        RETAIL_SALES_YOY,
        RETAIL_SALES_ADV_YOY,
        VEHICLE_SALES_YOY,
        BUSINESS_INVENTORY_YOY,
        BUSINESS_INVENTORY_SALES_RATIO,
        MANUFACT_INVENTORY_SALES_RATIO,
        RETAIL_INVENTORY_SALES_RATIO,
    ],
    GROUP_HOUSING: [
        HOUSING_STARTS,
        HOUSING_STARTS_YOY,
        NEW_HOME_SALES,
        NEW_HOME_SALES_YOY,
        EXIST_HOME_SALES,
        HOUSING_INVENTORY_EST,
    ],
    GROUP_GOV_FISCAL: [
        GOV_FISCAL_BUDGET,
        US_GDP_YOY,
        US_GDP_REAL_YOY,
        GOV_BUDGET_GDP,
    ],
    GROUP_FED_MONETARY: [
        FED_FFR,
        MORTGAGE_RATE_30_YR,
        MORTGAGE_RATE_15_YR,
        PRIME_LOAN_RATE,
        # LIBOR_3_MTH,
        EXCESS_RESERVE_DEPO,
        LIQUDITY_M1_YOY,
        VELOCITY_M1,
        LIQUDITY_M2_YOY,
        VELOCITY_M2,
    ],
    GROUP_FOREX_TRADE: [
        TRADE_BALANCE,
        TRADE_INDEX_USD,
        FOREX_US_CHINA,
    ],
    GROUP_PRICE: [
        US_GDP_DEFLATOR_YOY,
        PERSONAL_CONSUMPTION_DEFLATOR_YOY,
        PRODUCER_PPI,
        PRODUCER_PPI_YOY,
        CASE_SHILLER_HPI,
        CASE_SHILLER_HPI_YOY,
        NON_FARM_UNIT_LABOUR,
        NON_FARM_UNIT_LABOUR_YOY,
    ],
    GROUP_DEBT: [
        HOUSEHOLD_DEBT,
        GOV_DEBT_GDP_RATIO,
        HOUSEHOLD_DEBT_GDP_RATIO,
    ],
    GROUP_BOND_YIELD: [
        YIELD_10_YR_MINUS_FFR,
        YIELD_10_YR_MINUS_2_YR,
    ],
}
