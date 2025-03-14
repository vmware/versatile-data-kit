/*
 * Copyright 2023-2025 Broadcom
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

const showError = async (error: any) => {
  await showErrorMessage(
    'Encountered an error while trying to connect the server. Error:',
    error,
    [Dialog.okButton()]
  );
};

interface IJobConvertToNotebookMessage {
  code_structure: string[];
  removed_files: string[];
}

type jobConvertToNotebookRequestResult = {
  /**
   * Result message of the operation, containing code_structure and removed_files or an informative string.
   */
  message: IJobConvertToNotebookMessage | string;
  /**
   * Status of the operation
   */
  isSuccessful: boolean;
};

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

type jobRequestResult = {
  /**
   * Result message of the operation
   */
  message: string;
  /**
   * Status of the operation
   */
  isSuccessful: boolean;
};

type TaskStatusResult = {
  /**
   * Unique task ID
   */
  task_id: string;
  /**
   * Status of the task
   */
  status: string;
  /**
   * Result message of the task if no errors occurred
   */
  message: string | IJobConvertToNotebookMessage;
  /**
   * Error message
   */
  error: string;
};

/**
 * Extracts the task id from the initial message returned by the server.
 * @param message
 */
function extractTaskIdFromMessage(message: string): string {
  // The messages is in the format "Task {task_id} started"
  return message.substring(5, message.length - 8);
}

const pollForTaskCompletion = async (
  taskId: string,
  // The default values of maxAttempts and interval are based on the limit of 12 hours for a job run.
  // Polling every 10 seconds for 12 hours results in a total of 4320 polls.
  maxAttempts = 4320,
  interval = 10000 // 10 seconds
): Promise<TaskStatusResult> => {
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const result = await requestAPI<TaskStatusResult>(
        `taskStatus?taskId=${taskId}`,
        { method: 'GET' }
      );
      if (result.task_id === taskId) {
        if (result.status !== 'running') {
          if (result.status === 'failed') {
            showError(result.error);
          }
          return result;
        }
      }
    } catch (error) {
      showError(error);
      return {
        task_id: taskId,
        status: 'failed',
        message: '',
        error: `An error occurred while polling for task status. Error: ${error}`
      };
    }
    await new Promise(resolve => setTimeout(resolve, interval));
  }
  return {
    task_id: taskId,
    status: 'failed',
    message: '',
    error: `Task ${taskId} timed out`
  };
};

/**
 * Sent a POST request to the server to run a data job.
 * The information about the data job is retrieved from jobData object and sent as JSON.
 * Returns a pair of boolean (representing whether the vdk run was run) and a string (representing the result of vdk run)
 */
export async function jobRunRequest(): Promise<jobRequestResult> {
  if (await checkIfVdkOptionDataIsDefined(VdkOption.PATH)) {
    try {
      const initialResponse = await requestAPI<serverVdkOperationResult>(
        'run',
        {
          body: JSON.stringify(getJobDataJsonObject()),
          method: 'POST'
        }
      );
      if (initialResponse.error) {
        showError(initialResponse.error);
        return { message: initialResponse.message, isSuccessful: false };
      }

      const taskId = extractTaskIdFromMessage(initialResponse.message);
      const finalResult = await pollForTaskCompletion(taskId);
      if (finalResult.error) {
        return { message: finalResult.error, isSuccessful: false };
      } else {
        return {
          message: finalResult.message as string,
          isSuccessful: true
        };
      }
    } catch (error) {
      showError(error);
      return { message: '', isSuccessful: false };
    }
  } else {
    return { message: '', isSuccessful: false };
  }
}

/**
 * Sent a POST request to the server to execute a VDK operation a data job.
 * The information about the data job is retrieved from jobData object and sent as JSON.
 * Returns a pair of boolean (representing whether the vdk operation was successful)
 *                                     and a string (representing the result message)
 * Currently, the result message of a fail is empty string since the error is handled in the current operation
 */
export async function jobRequest(endPoint: string): Promise<jobRequestResult> {
  if (
    (await checkIfVdkOptionDataIsDefined(VdkOption.NAME)) &&
    (await checkIfVdkOptionDataIsDefined(VdkOption.TEAM))
  ) {
    try {
      const initialResponse = await requestAPI<serverVdkOperationResult>(
        endPoint,
        {
          body: JSON.stringify(getJobDataJsonObject()),
          method: 'POST'
        }
      );
      if (initialResponse.error) {
        showError(initialResponse.error);
        return { message: initialResponse.message, isSuccessful: false };
      }

      const taskId = extractTaskIdFromMessage(initialResponse.message);
      const finalResult = await pollForTaskCompletion(taskId);
      if (finalResult.error) {
        return { message: finalResult.error, isSuccessful: false };
      } else {
        return {
          message: finalResult.message as string,
          isSuccessful: true
        };
      }
    } catch (error) {
      showError(error);
      return { message: '', isSuccessful: false };
    }
  }
  return { message: '', isSuccessful: false };
}

/**
 * Sends a POST request to the server to perform a 'transform job to notebook' operation.
 * This function prepares the job data and makes the request.
 *
 * Upon success, the server returns an object containing:
 * - message: A string that includes the 'codeStructure' and 'filenames' os the steps of the transformed job.
 * - isSuccessful: A boolean indicating the operation's success. It's '' when no errors occurred during the operation.
 *
 * Upon failure (either server-side or client-side), the function returns an object
 * with an error message and 'false' status.
 * Any error that occurred during the operation is also shown to the user.
 *
 * @returns A Promise that resolves to an object containing the message from the server and the status of the operation.
 */
export async function jobConvertToNotebookRequest(): Promise<jobConvertToNotebookRequestResult> {
  if (await checkIfVdkOptionDataIsDefined(VdkOption.PATH)) {
    try {
      const initialResponse = await requestAPI<serverVdkOperationResult>(
        'convertJobToNotebook',
        {
          body: JSON.stringify(getJobDataJsonObject()),
          method: 'POST'
        }
      );
      if (initialResponse.error) {
        showError(initialResponse.error);
        return { message: initialResponse.message, isSuccessful: false };
      }

      const taskId = extractTaskIdFromMessage(initialResponse.message);
      const finalResult = await pollForTaskCompletion(taskId);
      if (finalResult.error) {
        return { message: finalResult.error, isSuccessful: false };
      } else {
        return {
          message: finalResult.message as IJobConvertToNotebookMessage,
          isSuccessful: true
        };
      }
    } catch (error) {
      showError(error);
      return { message: '', isSuccessful: false };
    }
  } else {
    return {
      message:
        'The job path is not defined. Please define it before attempting to convert the job to a notebook.',
      isSuccessful: false
    };
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
    showError(error);
  }
}

/**
 * Sent a POST request to the server to get more information about the notebook that includes a cell with the given id
 * Returns the path to the notebook file and the index of the cell with the spicific id
 * If no such notebook in the current directory or no notebook with a cell with such an id is found return empty strings
 */
export async function getNotebookInfo(cellId: string): Promise<{
  path: string;
  cellIndex: string;
}> {
  type getNotebookInfoResult = {
    path: string;
    cellIndex: string;
  };
  const dataToSend = {
    cellId: cellId,
    jobPath: jobData.get(VdkOption.PATH)
  };
  if (await checkIfVdkOptionDataIsDefined(VdkOption.PATH)) {
    try {
      const data = await requestAPI<getNotebookInfoResult>('notebook', {
        body: JSON.stringify(dataToSend),
        method: 'POST'
      });
      return {
        path: data['path'],
        cellIndex: data['cellIndex']
      };
    } catch (error) {
      return {
        path: '',
        cellIndex: ''
      };
    }
  } else {
    return {
      path: '',
      cellIndex: ''
    };
  }
}

/**
 * Sent a POST request to the server to indices of the vdk cells of a notebook
 * Returns an Array with indices if vdk cells are found and empty array if not
 */
export async function getVdkCellIndices(
  nbPath: string
): Promise<Array<Number>> {
  try {
    const dataToSend = {
      nbPath: nbPath
    };
    const data = await requestAPI<Array<Number>>('vdkCellIndices', {
      body: JSON.stringify(dataToSend),
      method: 'POST'
    });
    return data;
  } catch (error) {
    showError(error);
  }
  return [];
}

export async function getServerDirRequest(): Promise<string> {
  const data = await requestAPI<any>('serverPath', {
    method: 'GET'
  });
  if (data) {
    return data;
  } else {
    await showErrorMessage(
      "Encountered an error while trying to connect the server. Error: \
      the server's location cannot be identified!",
      [Dialog.okButton()]
    );
    return '';
  }
}
