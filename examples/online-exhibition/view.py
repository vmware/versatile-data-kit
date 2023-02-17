# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import math

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
    schema="online-exhibition",
)


st.markdown("# Van Gogh's Artworks")

provider = pd.read_sql_query(f"SELECT DISTINCT(provider) FROM cleaned_assets", conn)
provider = st.selectbox("Select a Provider", provider["provider"], key="provider")

df = pd.read_sql_query(
    f"SELECT * FROM cleaned_assets WHERE provider = '{provider}'", conn
)
n_cols = 5
n_items = df.shape[0]
n_items_for_col = math.ceil(n_items / n_cols)

cols = st.columns(n_cols)
images = df["edmpreview"].values

start = 0
end = n_items_for_col
for col in cols:
    with col:
        current_df = df[start:end]
        for index, row in current_df.iterrows():
            image = row["edmpreview"]
            caption = row["title"]
            # for image in images[start:end]:
            if image != "":
                st.image(image, caption=caption)
    start = end + 1
    end = end + n_items_for_col
