# Overview

In this example we will use Versatile Data Kit to create Streamlit web app that displays GitHub Star History:

[<img src="https://user-images.githubusercontent.com/11227374/192750161-dfca62f0-5ea3-4300-8887-4413c8dbbf05.png" width="500"/>](Github)

The job will insert the data from GitHub API into local sqlite table and create a Streamlit app. It also edits the default streamlit color schema.

Before you continue, make sure you are familiar with the
[Getting Started](https://github.com/vmware/versatile-data-kit/wiki/Getting-Started) section of the wiki.

How to run this job locally
-----
To run this job, follow the steps: 

1. clone the repo 
```
git clone https://github.com/vmware/versatile-data-kit.git
```
2. install vdk 
```
pip install -U pip setuptools wheel
pip install quickstart-vdk
```
3. Now do vdk create, enter the job name, team and location
```
vdk create

Job Name: local-github-stars
Job Team: test
Path to where sample data job will be created locally [/home/gita/vdk]:
Data Job with name local-github-stars created locally in /home/gita/vdk/local-github-stars.
```
4. Clear the new directory and copy example files to it
```
rm local-github-stars/*
cp versatile-data-kit/examples/github-stars-example/github-stars-example-job/* local-github-stars/
```
5. Add your GitHub token and repo name to the file 00_properties.py
```
vim local-github-stars/00_properties.py
```
NB! Repo Path is only the username and reponame not the full link "repo_path": "vmware/versatile-data-kit"

6. Install requirements 
```
pip install -r local-github-stars/requirements.txt
```
7. Run the job
```
vdk run local-github-stars
```
8. Now you can see your data by running: 
```
vdk sqlite-query -q "Select * from github_star_history"
```
9. To create the dashboard, run: 
```
streamlit run local-github-stars/40_build_streamlit_dashboard.py
```
Your webapp should be up, here: http://localhost:8501 🥳

To change the streamlit colors you can modify the file: 
```
vim ~/.streamlit/config.toml
```

Code
----

The relevant Data Job and Airflow DAG code is available
[here](https://github.com/vmware/versatile-data-kit/tree/main/examples/github-stars-example).

The code can be reused to track Hithub Star History for any GitHub repo.

Data
--------

We get the data from GitHub API using PyGithub library.
To display the history we need to get the date when user starred the repository and count of the stars.

Requirements
------------

To run this example, you need
* Versatile Data Kit
* PyGithub
* Sqlite
* Streamlit
* Pandas
* Plotly
* Versatile Data Kit Properties FS plugin

Configuration
-------------

If you have not done so already, you can install Versatile Data Kit and the
plugins required for this example by running the following commands from a terminal:
```console
pip install quickstart-vdk
pip install vdk-properties-fs
```
Note that Versatile Data Kit requires Python 3.7+. See the
[Installation page](https://github.com/vmware/versatile-data-kit/wiki/Installation#install-sdk) for more details.

In the config.ini file following lines are necessary to enable the plugin and add Sqlite configuration

```
db_default_type=SQLITE
ingest_method_default=sqlite
properties_default_type=fs-properties-client
```

Data Job
--------

Data job has the following structure:

```
github-stars-example-job/
├── 00_properties.py
├── 10_drop_table.sql
├── 20_create_table.sql
├── 30_stargazers.py
├── 40_build_streamlit_dashboard.py
├── config.ini
├── requirements.txt
```

<details>
    <summary>00_properties.py</summary>

```py
import logging
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)

def run(job_input: IJobInput):
    properties = job_input.get_all_properties()

    # Insert your github token from https://github.com/settings/tokens
    # Repository path user/repo, for example 'vmware/versatile-data-kit'
    job_input.set_all_properties({
        'token': '',
        'repo_path': ''
    })
```
</details>

<details>
    <summary>10_drop_table.sql</summary>

```sql
DROP TABLE IF EXISTS github_star_history;
```
</details>

<details>
    <summary>20_create_table.sql</summary>

```sql
CREATE TABLE github_star_history (starred_time, count);
```
</details>

<details>
    <summary>30_stargazers.py</summary>

```py
import logging
from github import Github
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):

    # In order to use properties, install vdk server OR vdk-properties-fs plugin
    # [VDK server installation](https://github.com/vmware/versatile-data-kit/wiki/Installation#install-versatile-data-kit-control-service)
    # [vdk-properties-fs plugin](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/vdk-properties-fs)

    # Properties are in the 00_properties.py file
    properties = job_input.get_all_properties()
    token = properties['token']
    repo_path = properties['repo_path']

    # Set token and path for PyGithub
    g = Github(token)
    repo = g.get_repo(repo_path)

    # Get Stargazer data with starred date, put them into a list and get length
    users = repo.get_stargazers_with_dates()
    usr_list = list(users)
    count = len(usr_list)

    data_to_send = []

    # Go through the list and add Starred Time and count of stars
    for i, u in enumerate(range(count)):
        data_to_send.append(
            [str(usr_list[u].starred_at), i+1],
        )
    # Ingest the data in to github_star_history table
    job_input.send_tabular_data_for_ingestion(
        rows=data_to_send,
        column_names=['starred_time', 'count'],
        destination_table='github_star_history'
    )
```
</details>

<details>
    <summary>40_build_streamlit_dashboard.py</summary>

```py
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
```
</details>

<details>
    <summary>config.ini</summary>

```ini
nes (20 sloc)  928 Bytes

; Supported format: https://docs.python.org/3/library/configparser.html#supported-ini-file-structure

; This is the only file required to deploy a Data Job.
; Read more to understand what each option means:

; Information about the owner of the Data Job
[owner]

; Team is a way to group Data Jobs that belonged to the same team.
team = test

; Configuration related to running data jobs
[job]
; For format see https://en.wikipedia.org/wiki/Cron
; The cron expression is evaluated in UTC time.
; If it is time for a new job run and the previous job run hasn’t finished yet,
; the cron job waits until the previous execution has finished.
schedule_cron = 11 23 5 8 1

[vdk]
; Key value pairs of any configuration options that can be passed to vdk.
; For possible options in your vdk installation execute command vdk config-help
db_default_type=SQLITE
ingest_method_default=sqlite

properties_default_type=fs-properties-client
```
</details>


<details>
    <summary>requirements.txt</summary>

```txt
vdk-core
pygithub
streamlit
sqlite3
pandas
plotly
```
</details>
