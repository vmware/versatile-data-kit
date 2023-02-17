import { requestAPI } from './handler';
import { Dialog, showErrorMessage } from '@jupyterlab/apputils';
import { jobData } from './dataClasses/jobData';
/**
 * Utility functions that are called by the dialogs.
 * They are called when a request to the server is needed to be sent.
 */

/**
 * Sent a GET request to the server to get current working directory
 */
export async function getCurrentPathRequest() {
  try {
    const data = await requestAPI<any>('run', {
      method: 'GET'
    });
    sessionStorage.setItem('current-path', data['path']);
  } catch (error) {
    throw error;
  }
}

/**
 * Sent a POST request to the server to run a data job.
 * The information about the data job is retrieved from sessionStorage and sent as JSON.
 */
export async function jobRunRequest() {
  if (jobData.jobPath) {
    try {
      const data = await requestAPI<any>('run', {
        body: JSON.stringify(jobData),
        method: 'POST'
      });
      const message =
        'Job execution has finished with status ' +
        data['message'] +
        ' \n See vdk_logs.txt file for more!';
      alert(message);
    } catch (error) {
      await showErrorMessage(
        'Encountered an error when trying to run the job. Error:',
        error,
        [Dialog.okButton()]
      );
    }
  } else {
    await showErrorMessage(
      'Encountered an error when trying to run the job. Error:',
      'The path should be defined!',
      [Dialog.okButton()]
    );
  }
}

/**
 * Sent a POST request to the server to delete a data job.
 * The information about the data job is retrieved from sessionStorage and sent as JSON.
 */
export async function deleteJobRequest() {
  if (jobData.jobName && jobData.jobTeam) {
    try {
      const data = await requestAPI<any>('delete', {
        body: JSON.stringify(jobData),
        method: 'POST'
      });
      if (!data['error']) {
        alert(data['message']);
      } else {
        await showErrorMessage(
          'Encountered an error when deleting the job. Error:',
          data['message'],
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
  } else {
    await showErrorMessage(
      'Encountered an error when deleting the job. Error:',
      'The name and the team of the job should be defined!',
      [Dialog.okButton()]
    );
  }
}

/**
 * Sent a POST request to the server to download a data job.
 * The information about the data job is retrieved from sessionStorage and sent as JSON.
 */
export async function downloadJobRequest() {
  if (jobData.jobName && jobData.jobTeam) {
    try {
      let data = await requestAPI<any>('download', {
        body: JSON.stringify(jobData),
        method: 'POST'
      });
      if (!data['error']) {
        alert(data['message']);
      } else {
        await showErrorMessage(
          'Encountered an error when trying to download the job. Error:',
          data['message'],
          [Dialog.okButton()]
        );
      }
    } catch (reason) {
      await showErrorMessage(
        'Encountered an error when trying to download the job. Error:',
        reason,
        [Dialog.okButton()]
      );
    }
  } else {
    await showErrorMessage(
      'Encountered an error when trying to download the job. Error:',
      'The name and the team of the job should be defined!',
      [Dialog.okButton()]
    );
  }
}

/**
 * Sent a POST request to the server to create a data job.
 * The information about the data job is retrieved from sessionStorage and sent as JSON.
 */
 export async function createJobRequest() {
  if (jobData.jobName && jobData.jobTeam) {
    try {
      const data = await requestAPI<any>('create', {
        body: JSON.stringify(jobData),
        method: 'POST'
      });
      if (!data['error']) {
        alert(data['message']);
      } else {
        await showErrorMessage(
          'Encountered an error when creating the job. Error:',
          data['message'],
          [Dialog.okButton()]
        );
      }
    } catch (error) {
      await showErrorMessage(
        'Encountered an error when creating the job. Error:',
        error,
        [Dialog.okButton()]
      );
    }
  } else {
    await showErrorMessage(
      'Encountered an error when creating the job. Error:',
      'The name and the team of the job should be defined!',
      [Dialog.okButton()]
    );
  }
}
