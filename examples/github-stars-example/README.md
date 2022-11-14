# Overview

In this example we will use Versatile Data Kit to create Streamlit web app that displays GitHub Star History:

[<img src="https://user-images.githubusercontent.com/11227374/192750161-dfca62f0-5ea3-4300-8887-4413c8dbbf05.png" width="500"/>](Github)

The job will insert the data from GitHub API into local sqlite table and create a Streamlit app. It also edits the default streamlit color schema.

Before you continue, make sure you are familiar with the
[Getting Started](https://github.com/vmware/versatile-data-kit/wiki/Getting-Started) section of the wiki.

How to run this job locally
-----
To run this job, follow the steps:

1. Clone the repo
```
git clone https://github.com/vmware/versatile-data-kit.git
```
2. Install vdk
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
5. Set your GitHub token and repo name
```
vdk properties --set-secret 'token' -n github-stars-example-job -t yourteam
vdk properties --set 'repo_path' -n github-stars-example-job -t yourteam
```
NB! Repo Path is only the username and reponame not the full link "repo_path": "vmware/versatile-data-kit"
See vdk properties --help for more info.

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
