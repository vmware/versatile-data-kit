/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { requestAPI } from './handler';
import { Dialog, showErrorMessage } from '@jupyterlab/apputils';
import {
  checkIfVdkOptionDataIsDefined,
  getJobDataJsonObject,
  jobData
} from './jobData';
import { VdkOption } from './vdkOptions/vdk_options';

/**
 * Utility functions that are called by the dialogs.
 * They are called when a request to the server is needed to be sent.
 */

type serverVdkOperationResult = {
  /**
   * Error message
   */
  error: string;
  /**
   * Result message if no errors occured
   */
  message: string;
};

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
      const data = await requestAPI<serverVdkOperationResult>('run', {
        body: JSON.stringify(getJobDataJsonObject()),
        method: 'POST'
      });
      return { message: data['message'], status: data['message'] == '0' };
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
export async function jobRequest(endPoint: string): Promise<void> {
  if (
    (await checkIfVdkOptionDataIsDefined(VdkOption.NAME)) &&
    (await checkIfVdkOptionDataIsDefined(VdkOption.TEAM))
  ) {
    try {
      const data = await requestAPI<serverVdkOperationResult>(endPoint, {
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

/**
 * Sent a POST request to the server to get information about the data job of current directory
 */
export async function jobdDataRequest(): Promise<void> {
  try {
    const data = await requestAPI<any>('job', {
      body: JSON.stringify(JSON.stringify(getJobDataJsonObject())),
      method: 'POST'
    });
    if (data) {
      jobData.set(VdkOption.NAME, data[VdkOption.NAME]);
      jobData.set(VdkOption.TEAM, data[VdkOption.TEAM]);
      jobData.set(VdkOption.PATH, data[VdkOption.PATH]);
    }
  } catch (error) {
    await showErrorMessage(
      'Encountered an error while trying to connect the server. Error:',
      error,
      [Dialog.okButton()]
    );
  }
}

export async function getFailingNotebookInfo(failingCellId: string): Promise<{
  path: string;
  failingCellIndex: string;
}> {
  type getFailingNotebookInfoResult = {
    path: string;
    failingCellIndex: string;
  };
  const dataToSend = {
    failingCellId: failingCellId,
    jobPath: jobData.get(VdkOption.PATH)
  };
  if (await checkIfVdkOptionDataIsDefined(VdkOption.PATH)) {
    try {
      const data = await requestAPI<getFailingNotebookInfoResult>(
        'failingNotebook',
        {
          body: JSON.stringify(dataToSend),
          method: 'POST'
        }
      );
      return {
        path: data['path'],
        failingCellIndex: data['failingCellIndex']
      };
    } catch (error) {
      await showErrorMessage('Encountered an error. Error:', error, [
        Dialog.okButton()
      ]);
      return {
        path: '',
        failingCellIndex: ''
      };
    }
  } else {
    return {
      path: '',
      failingCellIndex: ''
    };
  }
}

export async function getVdkCellIndices(
  nbPath: string
): Promise<Array<Number>> {
  const dataToSend = {
    nbPath: nbPath
  };
  const data = await requestAPI<Array<Number>>('vdkIndices', {
    body: JSON.stringify(dataToSend),
    method: 'POST'
  });
  return data;
}
