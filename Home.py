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

st.markdown(markdown)

link='Trade Radar Link: [Trade Radar](https://danielemarobin-traderadar-home.streamlit.app/Trade_Radar)'
st.markdown(link)

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
        st.write('Getting data from Google Drive')
        st.session_state['df_full'] = gd.read_csv('Data/Spreadinator/exported.csv', comment=True)
        df_full=st.session_state['df_full']


