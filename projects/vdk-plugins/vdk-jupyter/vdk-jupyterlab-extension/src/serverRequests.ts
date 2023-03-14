/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { requestAPI } from './handler';
import { Dialog, showErrorMessage } from '@jupyterlab/apputils';
import { checkDefinedValue, getJobDataJsonObject } from './jobData';
import { VdkOption } from './vdkOptions/vdk_options';
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
 * The information about the data job is retrieved from jobData object and sent as JSON.
 * Returns a pair of boolean (representing whether the vdk run was run) and a string (representing the result of vdk run)
 */
export async function jobRunRequest(): Promise<[String, boolean]> {
  if (await checkDefinedValue(VdkOption.PATH)) {
    try {
      const data = await requestAPI<any>('run', {
        body: JSON.stringify(getJobDataJsonObject()),
        method: 'POST'
      });
      const message =
        'Job execution has finished with status ' +
        data['message'] +
        ' \n See vdk_logs.txt file for more!';
      return [message, true];
    } catch (error) {
      await showErrorMessage(
        'Encountered an error when trying to run the job. Error:',
        error,
        [Dialog.okButton()]
      );
      return ['', false];
    }
  } else {
    return ['', false];
  }
}

/**
 * Sent a POST request to the server to delete a data job.
 * The information about the data job is retrieved from jobData object and sent as JSON.
 */
export async function deleteJobRequest() {
  if (
    (await checkDefinedValue(VdkOption.NAME)) &&
    (await checkDefinedValue(VdkOption.TEAM))
  ) {
    try {
      const data = await requestAPI<any>('delete', {
        body: JSON.stringify(getJobDataJsonObject()),
        method: 'POST'
      });
      if (!data['error']) alert(data['message']);
      else {
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
  }
}

/**
 * Sent a POST request to the server to download a data job.
 * The information about the data job is retrieved from jobData object and sent as JSON.
 */
export async function downloadJobRequest() {
  if (
    (await checkDefinedValue(VdkOption.NAME)) &&
    (await checkDefinedValue(VdkOption.TEAM))
  ) {
    try {
      let data = await requestAPI<any>('download', {
        body: JSON.stringify(getJobDataJsonObject()),
        method: 'POST'
      });
      if (!data['error']) alert(data['message']);
      else {
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
  }
}

/**
 * Sent a POST request to the server to create a data job.
 * The information about the data job is retrieved from jobData object and sent as JSON.
 */
export async function createJobRequest() {
  if (
    (await checkDefinedValue(VdkOption.NAME)) &&
    (await checkDefinedValue(VdkOption.TEAM))
  ) {
    try {
      const data = await requestAPI<any>('create', {
        body: JSON.stringify(getJobDataJsonObject()),
        method: 'POST'
      });
      if (!data['error']) alert(data['message']);
      else {
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
  }
}
