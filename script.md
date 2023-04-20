In this video, we will cover how vdk-dag allows VDK users to manage job dependencies in a native way.

* ingest-comments
* preprocess-comments
* sentiment-analysis
* sentiment-plot

These four jobs here cover a simple sentiment analysis demo which pulls comments from Reddit posts which contain a given keyword,
and plots how many of them are positive, how many are negative, and how many are neutral.

The first job initally creates a target table in our configured database only if this table does not already exist, and then queries for Reddit comments from posts from the subreddits 'ChatGPT', 'MachineLearning', and 'OpenAI'. Additionally, we only scan posts which
contain the keyword 'gpt4' in their title. Then, the data job ingests the comments to the newly created table.

The second job performs simple preprocessing on our ingested comments - in this case we only clean the data of any duplicates.

The third job performs the sentiment analysis using the `vaderSentiment` library, which offers off-the-shelf models for sentiment
analysis. First, we create a new table, which will store the sentiment score for individual comments. Then, in the second step of
the data job, we query our database for the Reddit comments, and perform the sentiment analysis. Finally, we store every comment
with its corresponding sentiment score in the new table.

The fourth job plots the results in a simple graph, where we count the number of positive, negative, and neutral comments, assuming
positive comments have a sentiment score >0.1, negative ones have a score <-0.1, and neutral are in between.

What's important to note about these workloads is that they only work if ran sequentially. The `ingest-comments` job
must finish before the `preprocess-comments` job can start, otherwise what comments would it be preprocessing? Previously,
VDK users would stagger the executions to ensure that their executions do not overlap, meaning that a job would be scheduled
to run some hours after the previous one, with the assumption that the execution of the previous one must have completed by then.
However, that execution is not always true due to downtime, platform issues, or any other potential reason.

This is where our DAG comes into play - the data job `dag-sentiment` uses a newly-introduced API to manage the executions of other
data jobs. Let us look at the source code of the only step in the DAG. We see that we construct a list of dictionaries, which is
passed as a parameter to the `run_dag` method of the new `DagInput` API - this list of dictionaries is our configuration object for
the DAG, and it outlines the order in which jobs should execute.

Any individual job config in the configuration object contains 4 fields.
The first field is the name of the job - this name must correspond to the name of a job currently deployed in your Control Service instance.
The second name is the team of the job - similarly it must correspond to the team of the deployed job of the same name. If `team_name` isn't provided, the team name of the DAG is passed instead.
The third, `fail_dag_on_error` is a boolean which configures the DAG to fail if that specific job fails, or not.
The fourth, `depends_on`, is a list of job names which this job depends on, meaning that the execution of this job will not be started
until all the jobs listed finish.

I'd also like to mention that VDK DAGs are native VDK data jobs, and benefit from all the same features that other jobs benefit  from , such as monitoring, notifications, and more.

Now, let's run our DAG. We'll be running our DAG locally, but note that DAGs be deployed and configured to run periodically.

We can use the VDK CLI to see that this has triggered an execution for our first data job. The rest will follow in a bit.

Let's query our database to check whether the data we expect to see has appeared there. We see both of our new tables, and we see
that they have been filled with the appropriate data.

Finally, we see a status log, which describes all the jobs which were ran as part of this DAG, and their status.
