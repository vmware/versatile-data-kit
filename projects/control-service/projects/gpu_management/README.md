# A project for Efficient Management of GPUs


## Overview
This project contains java library that can be used to manage GPU resources between teams and jobs.
Also contained in this project is a UI for monitoring the current GPU consumption, per machine and per team.

## Monitoring UI Setup


1. Install postgres if not already installed
2. Update the application.properties with the postgres connection details for this instance.
3. Download the metabase oss jar from here: https://www.metabase.com/docs/latest/installation-and-operation/running-the-metabase-jar-file
4. startup metabase with `java -jar metabase.jar`
5. Go to http://localhost:3000
6. login with gpuManager@gpus.com and pw: gpu123
7. click settings in top right corner, choose admin setting
8. Choose databases from the top row, choose 'demo' update the credentials to be your local postgres database
9. choose the GPU Management Dashboard
10. ./gradlew build
11. Run a test and watch how jobs are moved between machines through the UI



## Algorithm Implementation




### Reshuffle
To reshuffle the jobs we use a linear programming solver.
Linear programming is an optimization technique for a system of linear constraints and a linear objective function.

Before you can use linear programming we need to decide what the variables are for our system.
In our case we will create a list of variables where each one represents if a node is on that machine.
1 => the job is running on the node. 0 => job is not running on the node
For example if there are 6 jobs and 3 machines our variables will look like.

|      | Job 1 | Job 2 | Job 3 | Job 4 | Job 5 | Job 6 |
|-----------|--------------|----|----|--------------|--------------|--------------|
| Machine 1 | ✅(1)         | ❌(0) | ✅(1) | ❌(0)         | ❌(0)         | ❌(0)         |
| Machine 2 | ❌(0)         | ❌(0) |  ❌(0)| ✅(1)         | ❌(0)         | ❌(0)         |
| Machine 3 | ❌(0)         | ❌(0) | ❌(0) | ❌(0)         | ✅(1)         | ❌(0)         |


In this case we have 18 (jobs*nodes) variables.


Next we need to decide on the constraints of our system.


#### Constraint 1:
A job can only exist on a single machine.
It would be senseless to deploy a job to more than one machine.

|                               | Job 1 | Job 2 | Job 3 | Job 4 | Job 5 | Job 6 |
|-------------------------------|--|--|--|--------------|--------------|--------------|
| Machine 1                     |  ✅(1) | ❌(0) |  ✅(1) | ❌(0)         | ❌(0)         | ❌(0)         |
| Machine 2                     | ❌(0) | ❌(0) | ❌(0) | ✅(1)         | ❌(0)         | ❌(0)         |
| Machine 3                     | ❌(0) | ❌(0) | ❌(0) | ❌(0)         | ✅(1)         | ❌(0)         |
| Constaint 1:<br/> Column <= 1 |   1 |  0 | 1 | 1            | 0            | 0            |

```
job_1___machine_1 + job_1___machine_2 + job_1___machine_3 <= 1
job_2___machine_1 + job_2___machine_2 + job_2___machine_3 <= 1
job_3___machine_1 + job_3___machine_2 + job_3___machine_3 <= 1
job_4___machine_1 + job_4___machine_2 + job_4___machine_3 <= 1
job_5___machine_1 + job_5___machine_2 + job_5___machine_3 <= 1
job_6___machine_1 + job_6___machine_2 + job_6___machine_3 <= 1
```

#### Constraint 2:
Constraint 2 is a tightening of constraint 1
All jobs marked as high priority or belonging to teams within budget must still be running at the end of the reshuffle.

Imagine the scenario where Team A and Team B both have a budget of 6.

Team A has two jobs running; Job 1 and Job 3. Both of these consume 4 device which means Team A is overconsuming.They are using 8 devices when they should only be using 6.
Team A have marked Job 3 as High Priority. They are happy to see their other jobs killed but they want to keep this alive.

Team  has two jobs running; Job 4 and Job 5. Both of these consume 2 device which means Team A is within budget.


Here was add a constraint that all these jobs will still running at the end of the reshuffle.
The absence of a value in the last row indicates no constraint on that column.

|                               | Job 1/Team A | Job 2/Team A | Job 3/Team A/High Priority | Job 4/Team B | Job 5/Team B | Job 6/Team B |
|-------------------------------|-------------|--|----------------------------|--------------|--------------|-------------|
| Machine 1                     | ✅(1)        | ❌(0) | ✅(1)                       | ❌(0)         | ❌(0)         | ❌(0)        |
| Machine 2                     | ❌(0)        | ❌(0) | ❌(0)                       | ✅(1)         | ❌(0)         | ❌(0)        |
| Machine 3                     | ❌(0)        | ❌(0) | ❌(0)                       | ❌(0)         | ✅(1)         | ❌(0)        |
| Constaint 1:<br/> Column == 1 |             |  | 1                          | 1            | 1            |             |




```
job_3___machine_1 + job_3___machine_2 + job_3___machine_3 == 1
job_4___machine_1 + job_4___machine_2 + job_4___machine_3 == 1
job_5___machine_1 + job_5___machine_2 + job_5___machine_3 == 1
```

#### Constraint 3
The total number of jobs on a machine must be less than the amount of resources available on that machine.
For this we are going to multiply the variable by the amount of resources in consumes.
For this example we will say:
1. All machines have 10 devices.
2. Job 1,2,3 need 4 devices and job 4,5,6 need 6 devices


|               | Job 1  | Job 2 | Job 3 | Job 4  | Job 5 | Job 6 | constraint 2:<rb/> Row must be less than number of devices |
|---------------|--------|--|--|--------|--|--|-----------------------------------------------------------|
| Machine 1 (devices == 10) | ✅(1*4) | ❌(0*4) |  ✅(1*4) | ❌(0*6) | ❌(0*6) | ❌(0*6) | 8 devices consumed                                        |
| Machine 2 (devices == 10)    | ❌(0*4)   | ❌(0*4) | ❌(0*4) | ✅(1*6)   | ❌(0*6) | ❌(0*6) | 6 devices consumed                                        |
| Machine 3 (devices == 10)    | ❌(0*4)   | ❌(0*4) | ❌(0*4) | ❌(0*6)   |  ✅(1*6) | ❌(0*6) | 6 devices consumed                                                         |



```
job_1___machine_1*job_1_required_resources + job_2___machine_1*job_2_required_resources + job_3___machine_1*job_3_required_resources + job_4___machine_1*job_4_required_resources + job_5___machine_1*job_5_required_resources + job_6___machine_1*job_6_required_resources <= devices_on_machines_1
job_1___machine_2*job_1_required_resources + job_2___machine_2*job_2_required_resources + job_3___machine_2*job_3_required_resources + job_4___machine_2*job_4_required_resources + job_5___machine_2*job_5_required_resources + job_6___machine_2*job_6_required_resources <= devices_on_machines_2
job_1___machine_3*job_1_required_resources + job_2___machine_3*job_2_required_resources + job_3___machine_3*job_3_required_resources + job_4___machine_3*job_4_required_resources + job_5___machine_3*job_5_required_resources + job_6___machine_3*job_6_required_resources <= devices_on_machines_3
```




#### Objective function
Broadly speaking we want to optimize for it to run the maximum amount of jobs.
If a variable represents a job running on a machine we want to maximise the amount of these variables set.

[//]: # ($Max[\sum_{i}^{jobs}\sum_{j}^{machines} presentOnNode_{ij}]$)

However we want to ensure that we don't move too many jobs around.
Moving and ML training job from one machine to another will cause some loss of work.
To encourage the system to avoid moving jobs there is a configurable parameter called jobPortability.
The value of jobPortability is (0,1].
Now the formula looks like:



![$Maximize[\sum_{i}^{jobs}\sum_{j}^{machines} \begin{cases} presentOnMachine_{ij} & \text{if } jobAlreadyPresentOnNode \\ presentOnMachine_{ij}*jobPortability & \text{otherwise.} \end{cases}]$](docs/CodeCogsEqn.svg#gh-dark-mode-only)
![$Maximize[\sum_{i}^{jobs}\sum_{j}^{machines} \begin{cases} presentOnMachine_{ij} & \text{if } jobAlreadyPresentOnNode \\ presentOnMachine_{ij}*jobPortability & \text{otherwise.} \end{cases}]$](docs/black.svg#gh-light-mode-only)


jobPortability at 0.1 indicates jobs are not very portable.
When jobPortability is set to 0.1 it is better to keep one job running where it is running than kill it to allow 9 jobs to take its place.
