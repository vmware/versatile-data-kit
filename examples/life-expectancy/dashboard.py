# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import math

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import trino

# connect to server
conn = trino.dbapi.connect(
    host="localhost",
    port=8080,
    user="root",
    catalog="mysql",
    http_scheme="HTTP",
    verify=True,
    schema="life-expectancy",
)

palette = ["#ff9494", "#ff5252", "#8B0000", "#000000"]

# Design the UI
st.markdown("# Life Expectancy in the US")
st.markdown(
    """According to the U.S. Small-area Life Expectancy Estimates Project (USALEEP),
in 2018 in the US, Life Expectancy was greater than 76 years old for all the Regions.
**Southern Regions had the lowest life expectancy**, with an average life expectancy of 76.66,
and Northeastern Regions the highest one, with an average life expectancy of 79.52.
A similar behaviour happened in the 2010-2015 period.
"""
)

periods = pd.read_sql_query(
    f"SELECT DISTINCT(Period) FROM merged_life_expectancy", conn
)
period = st.selectbox("Select Period", periods["Period"], key="period")
df = pd.read_sql_query(
    f"SELECT Region, avg(LifeExpectancy) AS AvgLifeExpectancy FROM merged_life_expectancy WHERE Period = '{period}' GROUP BY Region",
    conn,
)

c = (
    alt.Chart(df)
    .mark_bar(size=90)
    .encode(
        y=alt.Y("AvgLifeExpectancy:Q", scale=alt.Scale(domain=[0, 100]), axis=None),
        x=alt.X("Region:N", axis=alt.Axis(labelAngle=0), title="US Regions"),
        color=alt.condition(
            alt.datum.Region == "South",  # If the year is 1810 this test returns True,
            alt.value("#8B0000"),  # which sets the bar orange.
            alt.value("gray"),  # And if it's not true it sets the bar steelblue.
        ),
    )
    .properties(
        width=500,
    )
)

text = c.mark_text(align="center", baseline="middle", dy=-15).encode(
    text="AvgLifeExpectancy:Q"
)

bars = (
    (c + text)
    .properties(height=300, title=f"Average Life Expectancy By Region ({period})")
    .configure_axis(grid=False, domain=False)
)
bars

st.markdown(
    "There is a correlation between the Life Expectancy and the Gross Domestic Product (GDP), as shown in the following graph:"
)

df = pd.read_sql_query(
    f"SELECT State, LifeExpectancy, GDP, Region FROM merged_life_expectancy WHERE Period = '2018'",
    conn,
)

scatter = (
    alt.Chart(df)
    .mark_circle(size=100)
    .encode(
        y=alt.Y("GDP:Q", title="GDP ($)", scale=alt.Scale(domain=[90e6, 3e9])),
        x=alt.X(
            "LifeExpectancy:Q",
            title="Life Expectancy",
            scale=alt.Scale(domain=[74, 81]),
        ),
        tooltip="State:N",
        color=alt.Color("Region:N", scale=alt.Scale(range=palette)),
    )
    .interactive()
)
st.altair_chart(scatter, use_container_width=True)

st.markdown(
    "In fact, most of the Southern Regions have the smallest GDP (see the bottom left part of the graph)."
)


st.markdown("## Detailed Report")
st.markdown("The following table shows an overview of the Life Expectancy Dataset.")

df = pd.read_sql_query(
    "SELECT LifeExpectancy, State, Region, Period FROM merged_life_expectancy ORDER BY LifeExpectancy DESC",
    conn,
)
df

st.markdown(
    "Select the reference Period and the top-N US states to dynamically update the bar chart."
)

n_records_per_year = math.ceil(df.shape[0] / 2)
period2 = st.selectbox("Select Period", periods["Period"], key="period2")
n_items = st.selectbox(
    "Select the number of States to show", np.arange(5, n_records_per_year + 5, step=5)
)

df_sorted = (
    df[df["Period"] == period2]
    .sort_values(by="LifeExpectancy", ascending=False)
    .head(n_items)
)
c = (
    alt.Chart(df_sorted)
    .mark_bar()
    .encode(
        x=alt.X("LifeExpectancy:Q", title="Life Expectancy"),
        y=alt.Y("State:N", sort="-x"),
        color=alt.Color("Region:N", scale=alt.Scale(range=palette)),
    )
)

st.altair_chart(c, use_container_width=True)
