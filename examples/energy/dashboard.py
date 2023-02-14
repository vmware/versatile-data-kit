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
    schema="energy",
)


# Design the UI
st.markdown("# Does the Natural Gas Price in the US depend on the temperature?")

st.markdown(
    """We consider two types of temperature:
    * much above normal
    * much below normal.
    The following figure shows that if the temperature is much above normal,
    the gas price decreases. This happened in 1998, 2012, 2015-2018.
    A temperature much below normal seems to not affect the gas price."""
)

df = pd.read_sql_query(
    f"SELECT Year, NormPrice, NormTemperatureMuchAboveNormal, NormTemperatureMuchBelowNormal FROM merged_tables",
    conn,
)

palette = ["#ff9494", "#ff5252", "#8B0000"]
indicators = [
    "NormPrice",
    "NormTemperatureMuchAboveNormal",
    "NormTemperatureMuchBelowNormal",
]

price_bar = (
    alt.Chart(df)
    .mark_bar(size=30)
    .encode(x="Year:O", y="NormPrice:Q", color=alt.value("#8B0000"))
)

temp_list = ["MuchAboveNormal", "MuchBelowNormal"]
temp_type = st.selectbox("Select Temperature", temp_list, key="temp_type")

temp_line = (
    alt.Chart(df)
    .mark_line()
    .encode(x="Year:O", y=f"NormTemperature{temp_type}:Q", color=alt.value("#ff9494"))
)

c = (price_bar + temp_line).properties(height=350, width=800)

st.altair_chart(c)
