# https://share.streamlit.io/

# https://share.streamlit.io/danielemarobin/monitor/main/Home.py
# https://docs.streamlit.io/library/api-reference
# https://streamlit-aggrid.readthedocs.io/en/docs/

# Memory issues
# https://blog.streamlit.io/common-app-problems-resource-limits/

from datetime import datetime as dt

import numpy as np

import streamlit as st
import func as fu
import GDrive as gd
import plotly.express as px

st.set_page_config(page_title='Trade Radar Home Page',layout="wide",initial_sidebar_state="expanded")

markdown=\
"""
# Trade Radar
---
#### In this application there are 2 pages (see sidebar on the left):
1) Ranking Tables:
    * Simple Ranking Tables to spot highly ranked trades
#####
2) Trade Radar:
    * Full Exploratory tool to get more information about the above trades and explore the results
"""

markdown_with_links=\
"""
# Trade Radar
---
#### In this application there are 2 pages (see sidebar on the left):
1) <a href="https://danielemarobin-traderadar-home.streamlit.app/Ranking_Tables" target="_self"> Ranking Tables </a>:
    * Simple Ranking Tables to spot highly ranked trades
#####
2) <a href="https://danielemarobin-traderadar-home.streamlit.app/Trade_Radar" target="_self"> Trade Radar </a>:
    * Full Exploratory tool to get more information about the above trades and explore the results
"""

st.markdown(markdown, unsafe_allow_html=True)

use_column_width=True
column_sizes=[1,10,1]


st.markdown('---')
st.markdown('# Ranking Explanation')

col1, col2, col3 = st.columns(column_sizes)
with col2:
    st.image('RankingExplanation.png', use_column_width=use_column_width)

st.markdown('---')

st.markdown('# Price Percentile Explanation')
st.markdown('# ')
st.markdown('# ')
st.markdown('# ')
col1, col2, col3 = st.columns(column_sizes)
with col2:
    st.image('PricePercentaile.png', use_column_width=use_column_width)


# Get the data
if True:
    # Delete all the items in Session state (to save memory)
    for key in st.session_state.keys():
        if key!='df_full':
            del st.session_state[key]

    df_full=None
    if ('df_full' in st.session_state):
        df_full=st.session_state['df_full']
    else:
        # st.write('Getting data from Google Drive')
        sel_date=dt.today().strftime('%Y-%m-%d')
        # st.session_state['df_full'] = gd.read_csv(file_path=f'Data/Spreadinator/spreadinator_{sel_date}.csv')
        st.session_state['df_full'] = gd.read_csv(file_path=f'Data/Spreadinator/spreadinator_last_update.csv')
        
        df_full=st.session_state['df_full']




