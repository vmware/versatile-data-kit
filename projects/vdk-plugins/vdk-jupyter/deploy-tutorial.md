## Introduction

This guide will describe the step-by-step process of deploying a Data Job
through the Jupyter UI when using VDK on Jupyter.

## Deploying a job

This page will assume you have already created a job both locally and in the cloud,
and have developed the job.

1. Navigate to the data job directory and ensure that your Data Job is production
ready. This means tagging all production cells as VDK cells, and untagging any
   you do not want to be ran during the Data Job execution.

![VDK dropdown menu](./vdk-menu.png)

2. From the menu bar at the top, open the VDK section and select the 'Deploy' option.

![VDK Deploy menu](./deploy-menu.png)

3. Enter your job name, team, and describe the latest change to the job in the
'Deployment reason' section. The path should be configured automatically if
   you have navigated to the job directory. Note the tick box which specifies that
   the job will be ran once before deployment. The purpose of this job execution is
   to test the job end-to-end and verify it can pass successfully before deploying
   it to the cloud.
   
![Status dialog](./status-dialog.png)

4. The previous step will generate this status dialog, informing you that the
deploy operation is running. Additionally, you can track the time the operation
   takes by the status button in the upper right corner.
   
![Status buttton](./timer.png)

![The dialog shown upon successful deploy](success-text.png)

5. The following dialog will appear when the job deployment request has been
successful. Note that the job will require a few minutes to be fully deployed.
