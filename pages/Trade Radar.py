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

import func as fu
import plotly.express as px

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, ColumnsAutoSizeMode

st.set_page_config(page_title='Trade Radar',layout="wide",initial_sidebar_state="expanded")

# Functions
if True:
    def func_reset():
        if ('df_full' in st.session_state):
            del st.session_state['df_full']

    def func_refresh():
        grid_response = None

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
            # mask = mask & ((df.asset_class_1==sel_asset) | (df.asset_class_2==sel_asset))
            # print(df.asset_class_2.unique)            
            mask = mask & ((df.asset_class_1==sel_asset) & (pd.isna(df.asset_class_2))) | ((df.asset_class_1==sel_asset) & (df.asset_class_2==sel_asset))

        # Selected Legs
        for sel_ticker in sel_tickers:
            mask = mask & ((df.leg_1_ticker==sel_ticker) | (df.leg_2_ticker==sel_ticker))

        # Excluded legs        
        for sel_ticker in excluded_tickers:
            mask = mask & ((df.leg_1_ticker!=sel_ticker) & (df.leg_2_ticker!=sel_ticker))

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
 
# Sidebar controls
if df_full is not None:
    st.sidebar.button('Get Latest File', on_click=func_reset)
    chart_placeholder = st.empty()
    trades_n_placeholder = st.empty()

    with st.sidebar.form('run'):
        # Asset
        opt_1=df_full['asset_class_1'].astype(str)
        opt_2=df_full['asset_class_2'].astype(str)
        options = list(set(list(opt_1)+list(opt_2)))
        options.sort()
        options.remove('nan')
        sel_asset_classes = st.multiselect('Asset Class', options)

        # Trade Category
        opt_1=df_full['trade_category'].astype(str)
        options = list(set(list(opt_1)))
        options.sort()
        sel_category = st.multiselect('Trade Category', options)

        # Interval Type
        opt_1=df_full['analysis_range']
        options = list(set(list(opt_1)))
        options.sort()
        sel_ranges = st.multiselect('Range (months)', options)

        # Last N Years
        opt_1=df_full['last_n_years']
        options = list(set(list(opt_1)))
        options.sort()
        sel_last_n_years = st.multiselect('Last N years', options)

        st.markdown('---')

        # Must contain Tickers
        opt_1=df_full['leg_1_ticker'].astype(str)
        opt_2=df_full['leg_2_ticker'].astype(str)
        options = list(set(list(opt_1)+list(opt_2)))
        options.sort()
        options.remove('nan')
        sel_tickers = st.multiselect( 'Must contain Tickers (Max 2)', options, max_selections=2)

        # Must exclude Tickers
        excluded_tickers = st.multiselect( 'Excluded Tickers', options)

        # Interval Type
        opt_1=df_full['interval_type'].astype(str)
        options = list(set(list(opt_1)))
        options.sort()
        sel_interval_type = st.multiselect( 'Interval Type', options)

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
        st.form_submit_button('Apply')

    mask_filters = apply_filters(df_full)
    df=df_full.loc[mask_filters]

# Edit columns (and add settings that depend on the modified columns)
if df_full is not None:
    x='interval_pnl_succ_rate_interaction'
    y='interval_sign_price_perc_interaction'

    df['id']=df.index
    df['analysis_range'] = df['analysis_range'].astype(str)
    df['last_n_years'] = df['last_n_years'].astype(str)

    df['leg_1'] = df['leg_1'].astype(str)
    df['leg_2'] = df['leg_2'].astype(str)

    df['leg_1']=[x.replace('_',',') for x  in df['leg_1']]
    df['leg_2']=[x.replace('_',',') for x  in df['leg_2']]

    df['trade']=[x.replace('_',',') for x  in df['trade']]
    df['trade_VaR']=[x.replace('_',',') for x  in df['trade_VaR']]
    df['interval'] = pd.to_datetime(df['interval_start'], dayfirst=True).dt.strftime('%d %b %Y') + ' --> ' + pd.to_datetime(df['interval_end'], dayfirst=True).dt.strftime('%d %b %Y')
    df['trade_direction'] = ['Buy' if x > 0 else 'Sell'  for x  in df['interval_strength']]
    df['price_percentile'] = df['price_percentile']/100.0
    df['success_str'] = df['interval_success_n'].astype(str) + ' out of ' + df['seasonal_years_n'].astype(str)

    df['interval_successful_years_and_returns'] = df['interval_successful_years_and_returns'].astype(str)
    df['interval_successful_years_and_returns']=[x.replace('_','`').replace('|',',') for x  in df['interval_successful_years_and_returns']]

    df['interval_unsuccessful_years_and_returns'] = df['interval_unsuccessful_years_and_returns'].astype(str)
    df['interval_unsuccessful_years_and_returns']=[x.replace('_','`').replace('|',',') for x  in df['interval_unsuccessful_years_and_returns']]

    df=fu.calculate_indicator(df,x,y)

    color_scales = fu.get_plotly_colorscales()
    cols=list(color_scales.keys())
    cols.sort()
    chart_color_key = st.sidebar.selectbox('Chart Color',cols, cols.index('RdYlGn-diverging')) # Plotly, Jet, RdYlGn-diverging
    color_list=color_scales[chart_color_key]
    

    # Variable Chart Color
    cols = list(df.columns)
    chart_color_variable = st.sidebar.selectbox('Chart Color Variable',cols, cols.index('indicator')) # trade_tickers, indicator

    # Chart Bubble Size
    chart_bubble_size = st.sidebar.selectbox('Chart Bubble Size',cols, cols.index('seasonal_years_n'))

    # Chart Labels
    cols_with_none = ['None']
    cols_with_none.extend(cols)
    chart_labels = st.sidebar.selectbox('Chart Labels',cols_with_none, cols_with_none.index('None'))    

    # Rows per page
    rows_per_page = st.sidebar.number_input('Rows per Page',1,100,30,1)

# Table
if df_full is not None:    
    grid_response = fu.aggrid_table_radar_page(df,rows_per_page=rows_per_page)
    selected_rows=grid_response['selected_rows']
    selected_df=pd.DataFrame(grid_response['selected_rows'])

    if (len(selected_df)>0):
        # st.write('len(selected_df)')
        # st.write(len(selected_df))
        mask_table=selected_df['id']
    else:
        # st.write('len(selected_df)')
        # st.write(len(selected_df))
        mask_table = df.notnull().any(axis=1)

# Filtering with table selection
if df_full is not None:
    df=df.loc[mask_table]
    trades_n_placeholder.text('Number of Trades in the chart: '+ str(df.shape[0]))    

# Chart
if df_full is not None:   
    text = chart_labels
    if chart_labels=='None':
        chart_labels=None

    custom_data=['trade','trade_VaR','interval_type', 'interval','interval_days','interval_pnl_per_day','interval_success_rate','success_str', 'trade_direction', 'price_percentile','analysis_range','last_n_years','seasonal_years_n','combination','x','y','indicator']
    hovertemplate="<br>".join([
            "<b>Trade:</b>",
            "<b>%{customdata[8]} %{customdata[0]}</b>",
            "100k VaR",
            "%{customdata[1]}",
            "",
            "<b>Interval Info:</b>",
            "Type: %{customdata[2]}",
            "%{customdata[3]}",
            "Days: %{customdata[4]}",        
            "",
            "<b>Performance:</b>",
            "PnL per Day (usd): %{customdata[5]:,.0f}",
            "Success: %{customdata[6]:.1%}",     
            "Success: %{customdata[7]}",   
            "",
            "<b>Price:</b>",            
            "Price Position: %{customdata[9]:.1%}",
            "",
            "<b>Analysis:</b>",
            "Range (months): %{customdata[10]}",
            "Last N Years (input): %{customdata[11]}",
            "Last N Years (output): %{customdata[12]}",
            "Id: %{customdata[13]}",
            "x: %{customdata[14]:,.1f} y: %{customdata[15]:,.1f} indicator: %{customdata[16]:,.1f} ",
            "<extra></extra>",
            ])
    
    # labels={x: 'Historical Performance',y: 'Current Opportunity'} # When changing the axis or legend names
    labels={}
    try:
        # fig=px.scatter(df,x='x',y='y', color=chart_color_variable, size=chart_bubble_size, custom_data=custom_data,labels=labels, text=chart_labels, color_continuous_scale=color_name, color_discrete_sequence=color_list)
        fig=px.scatter(df,x='x',y='y', color=chart_color_variable, size=chart_bubble_size, custom_data=custom_data,labels=labels, text=chart_labels, color_continuous_scale=color_list, color_discrete_sequence=color_list)

        fig.update_traces(hovertemplate=hovertemplate, textposition='top center')
        fig.update_layout(width=1500,height=850)
        
        chart_placeholder.plotly_chart(fig)
    except:
        chart_placeholder.error('Cannot pick a qualitative color scheme for Continuos Variables')
        # st.write('Cannot pick a qualitative color scheme for Continuos Variables')