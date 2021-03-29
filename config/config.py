

import os 
import regex as re


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
    'employment': [
        'unemploy', 'unemployNat', 'participation', 'popGrowth_YoY'
    ],
    'household': [
        'pDispIncome_YoY', 'pConsumeExp_YoY', 'pConsumeExpReal_YoY', 'pSaveRatio', 
        'mortgageDebt', 'consumeDebt'
    ],
    'manufacture_and_business': [
        'indusProduce', 'capacUtilise', 'manufactProduce', 'manufactNewOrderExDef', 
        'manufactNewOrderExTrans', 'onlineSales_YoY', 'onlineSalesRatio', 'retailSales_YoY', 
        'retailSalesAdv_YoY', 'vehicleSales_YoY', 'businessInventory_YoY', 
        'businessInventorySalesRatio', 'manufactInventorySalesRatio', 'retailInventorySalesRatio'
    ],
    'housing': [
        'houseStarts', 'houseStarts_YoY', 'newHomeSales', 'newHomeSales_YoY', 'existHomeSales', 
        'houseInventoryEst'
    ],
    'gov_fiscal': [
        'govFiscalBudget', 'usGDP_YoY', 'usGDPReal_YoY', 'govBudgetGDP'
    ],
    'fed_monetary': [
        'fedFFR', 'mortgageRate30Yr', 'mortgageRate15Yr', 'primeLoanRate', 'libor3mth', 
        'excessReserveDepo', 'liqM1_YoY', 'veloM1', 'liqM2_YoY', 'veloM2'
    ],
    'forex_trade': [
        'tradeBalance', 'tradeIndexUSD', 'forexUS_CHINA'
    ],
    'price': [
        'usGDP_deflator_YoY', 'pConsume_deflator_YoY', 'producerPPI', 'producerPPI_YoY', 
        'caseShillerHPI', 'caseShillerHPI_YoY', 'nonFarm_unitLabour', 'nonFarm_unitLabour_YoY'
    ],
    'debt': [
        'houseDebt', 'govDebt_GDP_ratio', 'houseDebt_GDP_ratio'
    ],
    'bond_yield': [
        'yield10Yr_minusFFR', 'yield10Yr_minus2Yr'
    ],
}
