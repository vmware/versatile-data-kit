/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { requestAPI } from './handler';
import { Dialog, showErrorMessage } from '@jupyterlab/apputils';
import { checkIfVdkOptionDataIsDefined, getJobDataJsonObject } from './jobData';
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
export async function jobRunRequest(): Promise<{
  message: String;
  status: boolean;
}> {
  if (await checkIfVdkOptionDataIsDefined(VdkOption.PATH)) {
    try {
      const data = await requestAPI<any>('run', {
        body: JSON.stringify(getJobDataJsonObject()),
        method: 'POST'
      });
      const message =
        'Job execution has finished with status ' +
        data['message'] +
        ' \n See vdk_logs.txt file for more!';
      return { message: message, status: true };
    } catch (error) {
      await showErrorMessage(
        'Encountered an error when trying to run the job. Error:',
        error,
        [Dialog.okButton()]
      );
      return { message: '', status: false };
    }
  } else {
    return { message: '', status: false };
  }
}

/**
 * Sent a POST request to the server to execute a VDK operation a data job.
 * The information about the data job is retrieved from jobData object and sent as JSON.
 */
export async function jobRequest(endPoint: string) {
  if (
    (await checkIfVdkOptionDataIsDefined(VdkOption.NAME)) &&
    (await checkIfVdkOptionDataIsDefined(VdkOption.TEAM))
  ) {
    try {
      const data = await requestAPI<any>(endPoint, {
        body: JSON.stringify(getJobDataJsonObject()),
        method: 'POST'
      });
      if (!data['error']) alert(data['message']);
      else {
        await showErrorMessage(
          'Encountered an error while trying the ' +
            endPoint +
            ' operation. Error:',
          data['message'],
          [Dialog.okButton()]
        );
      }
    } catch (error) {
      await showErrorMessage(
        'Encountered an error while trying to run the VDK operation. Error:',
        error,
        [Dialog.okButton()]
      );
    }
  }
}
