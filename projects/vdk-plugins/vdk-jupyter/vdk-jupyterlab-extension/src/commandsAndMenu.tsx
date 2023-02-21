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
import { jobData, JobProperties, revertJobDataToDefault } from './jobData';

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
            await jobRunRequest();
          }
          revertJobDataToDefault();
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
          revertJobDataToDefault();
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
              jobData.get(JobProperties.name) +
              ' from ' +
              jobData.get(JobProperties.restApiUrl) +
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
          revertJobDataToDefault();
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
        revertJobDataToDefault();
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
}
