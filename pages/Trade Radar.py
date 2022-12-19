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

import GDrive as gd
import plotly.express as px

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, ColumnsAutoSizeMode

st.set_page_config(page_title='Trade Radar',layout="wide",initial_sidebar_state="expanded")

def dm_scaler(df, col_to_rescale, new_min=-100.0, new_max=100.0):
    # I take the abs values because I want to have a summetric range (so that the signs will remain the same)
    old_max=abs(df[col_to_rescale].max())
    old_min=abs(df[col_to_rescale].min())

    old_max = max(old_max, old_min)
    old_min = -old_max

    to_rescale = df[col_to_rescale]
    rescaled = ((new_max - new_min) / (old_max - old_min)) * (to_rescale - old_min) + new_min
    return rescaled

def format_trade_entry(item):
    return item.strftime("%b %d")

def format_delivery(item):
    return item.strftime("%b %y")

def format_succ_rate(item):
    return str(item)+"%"

def func_reset():
    if ('df_full' in st.session_state):
        del st.session_state['df_full']

def func_refresh():
    grid_response = None

def apply_sidebar_filters(df):
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

    # Selected Legs
    for sel_ticker in sel_legs:
        mask = mask & ((df.leg_1_ticker==sel_ticker) | (df.leg_2_ticker==sel_ticker))

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


# Get the data
if True:
    x='interval_pnl_succ_rate_interaction'
    y='interval_sign_price_perc_interaction'

    # Delete all the items in Session state (to save memory)
    for key in st.session_state.keys():
        if key!='df_full':
            del st.session_state[key]

    df_full=None
    if ('df_full' in st.session_state):
        df_full=st.session_state['df_full']
    else:
        st.write('Getting data from Google Drive')
        st.session_state['df_full'] = gd.read_csv('Data/Spreadinator/exported.csv', comment=True)
        df_full=st.session_state['df_full']
 
# Create and apply the 'sidebar filters'
if df_full is not None:
    st.sidebar.button('Get Latest File', on_click=func_reset)
    chart_placeholder = st.empty()
    trades_n_placeholder = st.empty()

    with st.sidebar.form('run'):
        # Leg Tickers
        opt_1=df_full['leg_1_ticker'].astype(str)
        opt_2=df_full['leg_2_ticker'].astype(str)
        options = list(set(list(opt_1)+list(opt_2)))
        options.sort()
        options.remove('nan')
        sel_legs = st.multiselect( 'Filter Tickers (Max 2)', options, max_selections=2)

        # Trade Category
        opt_1=df_full['trade_category'].astype(str)
        options = list(set(list(opt_1)))
        options.sort()
        sel_category = st.multiselect( 'Trade Category', options)

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
        first_delivery, last_delivery = st.select_slider('Delivery', options=options, value=(min(options), max(options)), format_func=format_delivery)

        # Trade Entry and Exit
        opt_1=pd.to_datetime(df_full['interval_start'], dayfirst=True)
        opt_2=pd.to_datetime(df_full['interval_end'], dayfirst=True)        
        options =list(pd.date_range(min(opt_1), max(opt_2)))
        
        trade_entry_from, trade_entry_to = st.select_slider('Trade Entry', options=options, value=(options[0], options[0]+pd.DateOffset(months=1)), format_func=format_trade_entry)
        trade_exit_from, trade_exit_to = st.select_slider('Trade Exit', options=options, value=(options[0], options[-1]), format_func=format_trade_entry)

        # Holding period
        min_=df_full['interval_days'].min(); max_=df_full['interval_days'].max()
        min_holding_days, max_holding_days = st.select_slider('Minimum Holding (Days)',options=range(min_,max_+1),value=(7, max_))

        # Success Rate
        min_success_rate, max_success_rate = st.select_slider('Success Rate', options=range(0,101), value=(55, 100), format_func=format_succ_rate)

        # Form Submit Button
        st.form_submit_button('Apply')

    mask_filters = apply_sidebar_filters(df_full)
    df=df_full.loc[mask_filters]

# Edit columns (and add settings that depend on the modified columns)
if df_full is not None:
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

    df['x'] = dm_scaler(df=df,col_to_rescale= x)
    df['y'] = dm_scaler(df=df,col_to_rescale= y)
    df['indicator'] = 100.0*np.sqrt(pow(df['x'],2)+pow(df['y'],2))/np.sqrt(20000.0)
    
    df=df.sort_values(by='indicator',ascending=False)
    df['rank'] = list(range(1,len(df)+1))

    # Chart Color
    cols = list(df.columns)
    chart_color = st.sidebar.selectbox('Chart Color',cols, cols.index('trade_tickers'))

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
    statusPanels = {'statusPanels': [
        # { 'statusPanel': 'agTotalAndFilteredRowCountComponent', 'align': 'left' },
        # { 'statusPanel': 'agTotalRowCountComponent', 'align': 'center' },
        { 'statusPanel': 'agFilteredRowCountComponent', 'align': 'left' },
        { 'statusPanel': 'agSelectedRowCountComponent', 'align': 'left' },
        { 'statusPanel': 'agAggregationComponent', 'align': 'left' },
        ]}

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=rows_per_page)
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True,rowMultiSelectWithClick=False)
    gb.configure_selection('multiple', use_checkbox=True)
    gb.configure_grid_options(enableRangeSelection=True, statusBar=statusPanels)
    gb.configure_side_bar(defaultToolPanel='test')

    gb.configure_column('trade', headerCheckboxSelection = True, headerCheckboxSelectionFilteredOnly=True)
    # gb.configure_column('analysis_range', headerCheckboxSelection = True)
    gridOptions = gb.build()

    grid_response = AgGrid(df, gridOptions=gridOptions, data_return_mode=DataReturnMode.FILTERED, update_mode=GridUpdateMode.MANUAL, columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS, enable_enterprise_modules=True)
    # grid_response = AgGrid(df.head(1000), gridOptions=gridOptions, data_return_mode=DataReturnMode.FILTERED, update_mode=GridUpdateMode.MANUAL, columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS, enable_enterprise_modules=True)

    # st.write(grid_response.keys())
    # st.write('selected_rows')
    # st.write(grid_response['selected_rows'])

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

    fig=px.scatter(df,x='x',y='y', color=chart_color, size=chart_bubble_size, custom_data=custom_data,labels=labels, text=chart_labels)
    fig.update_traces(hovertemplate=hovertemplate, textposition='top center')
    fig.update_layout(width=1500,height=850)

    chart_placeholder.plotly_chart(fig)