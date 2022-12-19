# https://share.streamlit.io/

# https://share.streamlit.io/danielemarobin/monitor/main/Home.py
# https://docs.streamlit.io/library/api-reference
# https://streamlit-aggrid.readthedocs.io/en/docs/

# Memory issues
# https://blog.streamlit.io/common-app-problems-resource-limits/

from datetime import datetime as dt

import numpy as np
import pandas as pd

import streamlit as st
import functions as fu

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, ColumnsAutoSizeMode

st.set_page_config(page_title='Ranking Tables',layout="wide",initial_sidebar_state="expanded")

markdown=\
"""
# Ranking Tables
---
"""

st.markdown(markdown)


# Functions
if True:
    def apply_filters(df):
        # First and Last Delivery
        mask =  (pd.to_datetime(df.leg_1_delivery, dayfirst=True)>=first_delivery)
        mask = mask & (pd.to_datetime(df.leg_1_delivery, dayfirst=True)<=last_delivery)
        mask = mask & ((df.trade_category=='flat price') | ((pd.to_datetime(df.leg_2_delivery, dayfirst=True)>=first_delivery) & (pd.to_datetime(df.leg_2_delivery, dayfirst=True)<=last_delivery)))

        # Trade Entry and Exit
        mask = mask & ((df.interval_days>=min_holding_days) & (df.interval_days<=max_holding_days))
        mask = mask & ((pd.to_datetime(df.interval_start, dayfirst=True)>=trade_entry_from) & (pd.to_datetime(df.interval_start, dayfirst=True)<=trade_entry_to))
        mask = mask & ((pd.to_datetime(df.interval_end, dayfirst=True)>=trade_exit_from) & (pd.to_datetime(df.interval_end, dayfirst=True)<=trade_exit_to))

        # Success Rate
        mask = mask & ((df.interval_success_rate>=min_success_rate/100.0) & (df.interval_success_rate<=max_success_rate/100.0))

        # Asset class
        for sel_asset in sel_asset_classes:
            mask = mask & ((df.asset_class_1==sel_asset) | (df.asset_class_2==sel_asset))

        # Selected Legs
        for sel_ticker in sel_tickers:
            mask = mask & ((df.leg_1_ticker==sel_ticker) | (df.leg_2_ticker==sel_ticker))

        # Range
        if len(sel_ranges)>0:
            for i, sel_ in enumerate(sel_ranges):
                if i==0:
                    temp_mask = df.analysis_range==sel_
                else:
                    temp_mask = temp_mask | (df.analysis_range==sel_)
            mask = mask & (temp_mask)

        # Range
        if len(sel_last_n_years)>0:
            for i, sel_ in enumerate(sel_last_n_years):
                if i==0:
                    temp_mask = df.last_n_years==sel_
                else:
                    temp_mask = temp_mask | (df.last_n_years==sel_)
            mask = mask & (temp_mask)

        # Selected Categories
        if len(sel_category)>0:
            for i, sel_ in enumerate(sel_category):
                if i==0:
                    temp_mask = df.trade_category==sel_
                else:
                    temp_mask = temp_mask | (df.trade_category==sel_)
            mask = mask & (temp_mask)

        # Interval Type
        if len(sel_interval_type)>0:
            for i, sel_ in enumerate(sel_interval_type):
                if i==0:
                    temp_mask = df.interval_type==sel_
                else:
                    temp_mask = temp_mask | (df.interval_type==sel_)
            mask = mask & (temp_mask)

        return mask

# Declarations
if True:
    x='interval_pnl_succ_rate_interaction'
    y='interval_sign_price_perc_interaction'

# Get the data
if True:
    df_full=fu.get_data()

# Reading 'max' and 'min' of variables
if True:
    # Deliveries
    opt_1=pd.to_datetime(df_full['leg_1_delivery'], dayfirst=True)
    opt_2=pd.to_datetime(df_full['leg_2_delivery'], dayfirst=True)
    options = list(set(list(opt_1)+list(opt_2)))
    options.remove(pd.NaT)
    min_delivery = min(options)
    max_delivery= max(options)

    # Trade Entry and Exit
    opt_1=pd.to_datetime(df_full['interval_start'], dayfirst=True)
    opt_2=pd.to_datetime(df_full['interval_end'], dayfirst=True)        
    options =list(pd.date_range(min(opt_1), max(opt_2)))
    min_interval_start=min(opt_1)
    max_interval_end=max(opt_2)

    # Holding period
    min_holding=df_full['interval_days'].min()
    max_holding=df_full['interval_days'].max()

# Grains Calendar
if True:
    st.markdown('#### Grains Calendar Spreads (3 months range, last 10 Years)')

    # Filters
    sel_tickers = [] # tickers
    sel_asset_classes = ['grains'] # grains, oilseeds    
    sel_ranges = [3] # 3,6,9
    sel_last_n_years = [10] # 10, 15, 20, 25, 30, 100
    sel_category = ['calendar'] # Trade Category
    sel_interval_type = []    
    first_delivery, last_delivery = min_delivery, max_delivery # Deliveries    
    trade_entry_from, trade_entry_to = min_interval_start, max_interval_end # Trade Entry
    trade_exit_from, trade_exit_to = min_interval_start, max_interval_end # Trade Exit    
    min_holding_days, max_holding_days = min_holding, max_holding # Holding period    
    min_success_rate, max_success_rate = 0, 100 # Success Rate

    # Table Creation
    mask = apply_filters(df_full)
    df=df_full[mask]
    df=fu.calculate_indicator(df,x,y)
    grid_response = fu.aggrid_table_ranking_page(df,rows_per_page=20)


# Grains Calendar
if True:
    st.markdown('#### Oilseeds Calendar Spreads (3 months range, last 10 Years)')

    # Filters
    sel_tickers = [] # tickers
    sel_asset_classes = ['oilseeds'] # grains, oilseeds    
    sel_ranges = [3] # 3,6,9
    sel_last_n_years = [10] # 10, 15, 20, 25, 30, 100
    sel_category = ['calendar'] # Trade Category
    sel_interval_type = []    
    first_delivery, last_delivery = min_delivery, max_delivery # Deliveries    
    trade_entry_from, trade_entry_to = min_interval_start, max_interval_end # Trade Entry
    trade_exit_from, trade_exit_to = min_interval_start, max_interval_end # Trade Exit    
    min_holding_days, max_holding_days = min_holding, max_holding # Holding period    
    min_success_rate, max_success_rate = 0, 100 # Success Rate

    # Table Creation
    mask = apply_filters(df_full)
    df=df_full[mask]
    df=fu.calculate_indicator(df,x,y)
    grid_response = fu.aggrid_table_ranking_page(df,rows_per_page=20)