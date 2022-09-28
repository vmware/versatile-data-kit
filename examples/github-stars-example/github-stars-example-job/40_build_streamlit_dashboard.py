import os
import pathlib
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

# Page title
st.title('⭐️ Github Star History ⭐️')

# Sub-header
st.header('Star count over time')

# Make the current directory the same as the job directory
os.chdir(pathlib.Path(__file__).parent.absolute())

# Create connection to SQLITE DB
db_connection = sqlite3.connect(
        '/tmp/vdk-sqlite.db'
    )

# Fetch data
df = pd.read_sql_query(
    f'SELECT * FROM github_star_history', db_connection
)

# Use starred time date part without time and timezone information
df['starred_date'] = pd.to_datetime(df['starred_time']).dt.date

# Read starred date and star count into the chart, set the line color and labels
chart = px.line(data_frame=df, x = 'starred_date', y = 'count', color_discrete_sequence=['#C996CC'], labels={
                     "starred_date": "Date",
                     "count": "Star Count"
                 })

# Display the chart in streamlit
# To run streamlit app use the command
# streamlit run 40_build_streamlit_dashboard.py 
st.plotly_chart(chart)
