import holoviews as hv
from datetime import datetime
from bokeh.models import HoverTool


# ----------------------------------------------------------------------
# Styled Dataframes. 
# ---------------------------------------------------------------------- 

# To store styled dataframes. 
PIVOT_STATS_STYLED = {}


# ----------------------------------------------------------------------
# Streamlit CSS Styling. 
# ----------------------------------------------------------------------

ST_MAX_WIDTH = 1000
ST_PADDING_TOP = 1
ST_PADDING_RIGHT = 1
ST_PADDING_LEFT = 1
ST_PADDING_BOTTOM = 1
ST_COLOR = "rgb(50,50,50)"
ST_BACKGROUND_COLOR = "rgb(255,255,255)"


# ----------------------------------------------------------------------
# Holoviews Styling. 
# ---------------------------------------------------------------------- 

HV_PN_HEIGHT, HV_PN_WIDTH = (350,850)
HV_PN_VSPACE, HV_PN_HSPACE = (10,10)
XLIM = (datetime(1980,1,1), datetime(datetime.today().year, 12, 1))


# ----------------------------------------------------------------------
# Holoviews Tool. 
# ---------------------------------------------------------------------- 

# Hover.
hover_for_eco = HoverTool(
    tooltips=[('date','@date{%F}'), ('value','@{value}{0.2f}')],
    formatters={'@date': 'datetime'}, mode='vline'
)
HV_TOOLS_FOR_TICKER = ['crosshair'] 
HV_TOOLS_FOR_ECO = [hover_for_eco, 'crosshair'] 


# ----------------------------------------------------------------------
# For Tabs. 
# ---------------------------------------------------------------------- 

# Name for the tabs. 
ST_TABS = [
    'Price Difference', 
    'Average Volume Trend', 
    'Price Difference During Holiday Period', 
    'Price Difference During TWW Period', 
    'Price Difference During Special Period', 
    'Economic Data From FRED'
]


# ----------------------------------------------------------------------
# For Widget. 
# ---------------------------------------------------------------------- 

FORMAT_WIDGET_OPTIONS = lambda x: x.replace('_', ' ').title()


# ----------------------------------------------------------------------
# For Including Span 
# ---------------------------------------------------------------------- 

# Period / Span for rinancial trouble / recession / crisis. 
DEBT_CRISIS_2008 = hv.VSpan(datetime(2007,12,1), datetime(2009,6,1)).opts(line_width=1, color='lightgray')
DOT_COM_2001 = hv.VSpan(datetime(2001,3,1), datetime(2001,11,1)).opts(line_width=1, color='lightgray')
TROUBLE_1990 = hv.VSpan(datetime(1990,7,1), datetime(1991,3,1)).opts(line_width=1, color='lightgray')
TROUBLE_1982 = hv.VSpan(datetime(1981,11,1), datetime(1982,7,1)).opts(line_width=1, color='lightgray')
TROUBLE_1980 = hv.VSpan(datetime(1980,1,1), datetime(1980,7,1)).opts(line_width=1, color='lightgray')
TROUBLE_1974 = hv.VSpan(datetime(1973,11,1), datetime(1975,3,1)).opts(line_width=1, color='lightgray')
TROUBLE_1970 = hv.VSpan(datetime(1969,12,1), datetime(1970,11,1)).opts(line_width=1, color='lightgray')
TROUBLE_1960 = hv.VSpan(datetime(1960,4,1), datetime(1961,2,1)).opts(line_width=1, color='lightgray')
TROUBLE_1957 = hv.VSpan(datetime(1957,8,1), datetime(1958,4,1)).opts(line_width=1, color='lightgray')
TROUBLE_1953 = hv.VSpan(datetime(1953,7,1), datetime(1954,5,1)).opts(line_width=1, color='lightgray')
TROUBLE_1949 = hv.VSpan(datetime(1948,11,1), datetime(1949,10,1)).opts(line_width=1, color='lightgray')

# Combine the span. 
V_SPAN_ECO_RECESSION = (
    DEBT_CRISIS_2008 * DOT_COM_2001 \
    * TROUBLE_1990 * TROUBLE_1982 * TROUBLE_1980 * TROUBLE_1974 * TROUBLE_1970 * TROUBLE_1960
)
