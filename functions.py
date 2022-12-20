
import streamlit as st
import GDrive as gd
import numpy as np

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, ColumnsAutoSizeMode

def get_data():
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
    return df_full

def format_trade_entry(item):
    return item.strftime("%b %d")

def format_delivery(item):
    return item.strftime("%b %y")

def format_succ_rate(item):
    return str(item)+"%"

def dm_scaler(df, col_to_rescale, new_min=-100.0, new_max=100.0):
    # I take the abs values because I want to have a summetric range (so that the signs will remain the same)
    old_max=abs(df[col_to_rescale].max())
    old_min=abs(df[col_to_rescale].min())

    old_max = max(old_max, old_min)
    old_min = -old_max

    to_rescale = df[col_to_rescale]
    rescaled = ((new_max - new_min) / (old_max - old_min)) * (to_rescale - old_min) + new_min
    return rescaled

def calculate_indicator(df,x,y):
    df['x'] = dm_scaler(df=df,col_to_rescale= x)
    df['y'] = dm_scaler(df=df,col_to_rescale= y)
    df['indicator'] = 100.0*np.sqrt(pow(df['x'],2)+pow(df['y'],2))/np.sqrt(20000.0)    
    df=df.sort_values(by='indicator',ascending=False)
    df['rank'] = list(range(1,len(df)+1))    
    return df

def aggrid_table_radar_page(df,rows_per_page):
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
    return grid_response


def aggrid_table_ranking_page(df,rows_per_page):
    statusPanels = {'statusPanels': [
    { 'statusPanel': 'agFilteredRowCountComponent', 'align': 'left' },
    { 'statusPanel': 'agSelectedRowCountComponent', 'align': 'left' },
    { 'statusPanel': 'agAggregationComponent', 'align': 'left' },
    ]}

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=rows_per_page)
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True,rowMultiSelectWithClick=False)
    gb.configure_selection('multiple', use_checkbox=False)
    gb.configure_grid_options(enableRangeSelection=True, statusBar=statusPanels)
    gb.configure_side_bar(defaultToolPanel='test')


    gridOptions = gb.build()

    grid_response = AgGrid(df, gridOptions=gridOptions, data_return_mode=DataReturnMode.FILTERED, update_mode=GridUpdateMode.NO_UPDATE, columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS, enable_enterprise_modules=True)
    return grid_response