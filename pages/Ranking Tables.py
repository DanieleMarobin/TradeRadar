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

# Filters and Settings
if True:
    with st.sidebar: #.form('run'):
        # Trade Category
        opt_1=df_full['trade_category'].astype(str)
        options = list(set(list(opt_1)))
        options.sort()
        loop_category = st.multiselect( 'Trade Category', options, ['calendar', 'flat price'])

        # Interval Type
        opt_1=df_full['analysis_range']
        options = list(set(list(opt_1)))
        options.sort()
        loop_ranges = st.multiselect( 'Range (months)', options,[3,6])

        # Last N Years
        opt_1=df_full['last_n_years']
        options = list(set(list(opt_1)))
        options.sort()
        loop_n_years = st.multiselect( 'Last N years', options,[15])

        # Deliveries
        opt_1=pd.to_datetime(df_full['leg_1_delivery'], dayfirst=True)
        opt_2=pd.to_datetime(df_full['leg_2_delivery'], dayfirst=True)
        options = list(set(list(opt_1)+list(opt_2)))
        options.remove(pd.NaT)
        options.sort()
        first_delivery, last_delivery = st.select_slider('Delivery', options=options, value=(min(options), max(options)), format_func=fu.format_delivery)

        # Trade Entry and Exit
        opt_1=pd.to_datetime(df_full['interval_start'], dayfirst=True)
        opt_2=pd.to_datetime(df_full['interval_end'], dayfirst=True)        
        options =list(pd.date_range(min(opt_1), max(opt_2)))
        
        trade_entry_from, trade_entry_to = st.select_slider('Trade Entry', options=options, value=(options[0], options[0]+pd.DateOffset(months=1)), format_func=fu.format_trade_entry)
        trade_exit_from, trade_exit_to = st.select_slider('Trade Exit', options=options, value=(options[0], options[-1]), format_func=fu.format_trade_entry)

        # Holding period
        min_=df_full['interval_days'].min(); max_=df_full['interval_days'].max()
        min_holding_days, max_holding_days = st.select_slider('Minimum Holding (Days)',options=range(min_,max_+1),value=(7, max_))

        # Success Rate
        min_success_rate, max_success_rate = st.select_slider('Success Rate', options=range(0,101), value=(55, 100), format_func=fu.format_succ_rate)

        # Form Submit Button
        # st.form_submit_button('Apply')

    # Rows per page
    rows_per_page = st.sidebar.number_input('Rows per Page',1,100,15,1)

# Creating and Printing Tables
if True:
    loop_assets=['grains','oilseeds']

    for asset in loop_assets:
        for category in loop_category:
            for range in loop_ranges:
                for n_years in loop_n_years:
                    st.markdown('##### '+asset.title()+' '+category.title()+', '+str(range)+ ' months range, last '+str(n_years)+' Years')

                    # Filters
                    sel_tickers = []
                    sel_asset_classes = [asset]
                    sel_ranges = [range] # 3,6,9
                    sel_last_n_years = [n_years] # 10, 15, 20, 25, 30, 100
                    sel_category = [category] # Trade Category
                    sel_interval_type = []

                    # Table Creation
                    mask = apply_filters(df_full)
                    df=df_full[mask]

                    if (len(df)>0):
                        df=fu.calculate_indicator(df,x,y)
                        grid_response = fu.aggrid_table_ranking_page(df,rows_per_page=rows_per_page)
                    else:
                        st.markdown('No trades matching criteria')
                        st.markdown('---')