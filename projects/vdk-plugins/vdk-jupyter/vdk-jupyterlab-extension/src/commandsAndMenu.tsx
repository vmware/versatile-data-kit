import { CommandRegistry } from '@lumino/commands';
import { Dialog, showDialog, showErrorMessage } from '@jupyterlab/apputils';
import React from 'react';
import RunJobDialog from './components/RunJob';
import {
  createJobRequest,
  deleteJobRequest,
  downloadJobRequest,
  jobRunRequest
} from './serverRequests';
import CreateJobDialog from './components/CreateJob';
import DeleteJobDialog from './components/DeleteJob';
import DownloadJobDialog from './components/DownloadJob';
import { jobData, setJobDataToDefault } from './jobData';
import { VdkOption } from './vdkOptions/vdk_options';
import DeployJobDialog from './components/DeployJob';

var runningVdkOperation = false;

export function updateVDKMenu(commands: CommandRegistry) {
  commands.addCommand('jp-vdk:menu-run', {
    label: 'Run',
    caption: 'Execute VDK Run Command',
    execute: async () => {
      try {
        if (!runningVdkOperation) {
          runningVdkOperation = true;
          const result = await showDialog({
            title: 'Run Job',
            body: (
              <RunJobDialog
                jobPath={sessionStorage.getItem('current-path')!}
              ></RunJobDialog>
            ),
            buttons: [Dialog.okButton(), Dialog.cancelButton()]
          });
          const resultButtonClicked = !result.value && result.button.accept;
          if (resultButtonClicked) {
            let response = await jobRunRequest();
            if(response[1]){
              alert(response[0]);
            }
          }
          setJobDataToDefault();
          runningVdkOperation = false;
        } else {
          showErrorMessage(
            'Another VDK operation is currently running!',
            'Please wait until the operation ends!',
            [Dialog.okButton()]
          );
        }
      } catch (error) {
        await showErrorMessage(
          'Encountered an error when trying to run the job. Error:',
          error,
          [Dialog.okButton()]
        );
      }
    }
  });

  commands.addCommand('jp-vdk:menu-create', {
    label: 'Create',
    caption: 'Execute VDK Create Command',
    execute: async () => {
      let defaultJobName = sessionStorage
        .getItem('current-path')!
        .substring(sessionStorage.getItem('current-path')!.lastIndexOf('/'));
      try {
        if (!runningVdkOperation) {
          runningVdkOperation = true;
          const result = await showDialog({
            title: 'Create Job',
            body: (
              <CreateJobDialog
                jobPath={sessionStorage.getItem('current-path')!}
                jobName={defaultJobName}
              ></CreateJobDialog>
            ),
            buttons: [Dialog.okButton(), Dialog.cancelButton()]
          });
          const resultButtonClicked = !result.value && result.button.accept;
          if (resultButtonClicked) {
            await createJobRequest();
          }
          setJobDataToDefault();
          runningVdkOperation = false;
        } else {
          showErrorMessage(
            'Another VDK operation is currently running!',
            'Please wait until the operation ends!',
            [Dialog.okButton()]
          );
        }
      } catch (error) {
        await showErrorMessage(
          'Encountered an error when running the job. Error:',
          error,
          [Dialog.okButton()]
        );
      }
    }
  });

  commands.addCommand('jp-vdk:menu-delete', {
    label: 'Delete',
    caption: 'Execute VDK Delete Command',
    execute: async () => {
      try {
        if (!runningVdkOperation) {
          runningVdkOperation = true;
          const result = await showDialog({
            title: 'Delete Job',
            body: (
              <DeleteJobDialog
                jobName="job-to-delete"
                jobTeam="default-team"
              ></DeleteJobDialog>
            ),
            buttons: [Dialog.okButton(), Dialog.cancelButton()]
          });
          if (result.button.accept) {
            let bodyMessage =
              'Do you really want to delete the job with name ' +
              jobData.get(VdkOption.NAME) +
              ' from ' +
              jobData.get(VdkOption.REST_API_URL) +
              '?';
            try {
              const finalResult = await showDialog({
                title: 'Delete a data job',
                body: bodyMessage,
                buttons: [
                  Dialog.cancelButton({ label: 'Cancel' }),
                  Dialog.okButton({ label: 'Yes' })
                ]
              });
              if (finalResult.button.accept) {
                await deleteJobRequest();
              }
            } catch (error) {
              await showErrorMessage(
                'Encountered an error when deleting the job. Error:',
                error,
                [Dialog.okButton()]
              );
            }
          }
          setJobDataToDefault();
          runningVdkOperation = false;
        } else {
          showErrorMessage(
            'Another VDK operation is currently running!',
            'Please wait until the operation ends!',
            [Dialog.okButton()]
          );
        }
      } catch (error) {
        await showErrorMessage(
          'Encountered an error when deleting the job. Error:',
          error,
          [Dialog.okButton()]
        );
      }
    }
  });

  commands.addCommand('jp-vdk:menu-download', {
    label: 'Download',
    caption: 'Execute VDK Download Command',
    execute: async () => {
      try {
        if (!runningVdkOperation) {
          runningVdkOperation = true;
        const result = await showDialog({
          title: 'Download Job',
          body: (
            <DownloadJobDialog
              parentPath={sessionStorage.getItem('current-path')!}
            ></DownloadJobDialog>
          ),
          buttons: [Dialog.okButton(), Dialog.cancelButton()]
        });
        const resultButtonClicked = !result.value && result.button.accept;
        if (resultButtonClicked) {
          await downloadJobRequest();
        }
        setJobDataToDefault();
        runningVdkOperation = false;
      } else {
        showErrorMessage(
          'Another VDK operation is currently running!',
          'Please wait until the operation ends!',
          [Dialog.okButton()]
        );
      }
      } catch (error) {
        await showErrorMessage(
          'Encountered an error when trying to download the job. Error:',
          error,
          [Dialog.okButton()]
        );
      }
    }
  });

  commands.addCommand('jp-vdk:menu-create-deployment', {
    label: 'Deploy',
    caption: 'Create deployment of a VDK job',
    execute: async () => {
      try {
        if (!runningVdkOperation) {
          runningVdkOperation = true;
        const result = await showDialog({
          title: 'Create Deployment',
          body: (
            <DeployJobDialog jobName='job-to-deploy' jobPath={sessionStorage.getItem('current-path')!} jobTeam='my-team' vdkVersion='0.11'></DeployJobDialog>
          ),
          buttons: [Dialog.okButton(), Dialog.cancelButton()]
        });
        const resultButtonClicked = !result.value && result.button.accept;
        if (resultButtonClicked) {
          try {
            const runConfirmationResult = await showDialog({
              title: 'Create deployment',
              body: "The job will be executed once before deployment.\n Check the result and decide whether you will continue with the deployment, please!",
              buttons: [
                Dialog.cancelButton({ label: 'Cancel' }),
                Dialog.okButton({ label: 'Continue' })
              ]
            });
            if (runConfirmationResult.button.accept) {
              let success = await jobRunRequest();
              let bodyMessage = "We encauntered some errors while trying to run the job! To see more please check the vdk_logs.txt file!\n Do you want to continue with deployment?"
              if(success[1]){
                bodyMessage = success[0] + " Do you want to continue with the deployment?"
              }
              const finalResult = await showDialog({
                title: 'Create deployment',
                body: bodyMessage,
                buttons: [
                  Dialog.cancelButton({ label: 'Cancel' }),
                  Dialog.okButton({ label: 'Yes' })
                ]
              });
              if (finalResult.button.accept) {
                // add server request
              }
            }
          } catch (error) {
            await showErrorMessage(
              'Encountered an error when deploying the job. Error:',
              error,
              [Dialog.okButton()]
            );
          }
        }
        setJobDataToDefault();
        runningVdkOperation = false;
      } else {
        showErrorMessage(
          'Another VDK operation is currently running!',
          'Please wait until the operation ends!',
          [Dialog.okButton()]
        );
      }
      } catch (error) {
        await showErrorMessage(
          'Encountered an error when trying to deploy the job. Error:',
          error,
          [Dialog.okButton()]
        );
      }
    }
  });
}
