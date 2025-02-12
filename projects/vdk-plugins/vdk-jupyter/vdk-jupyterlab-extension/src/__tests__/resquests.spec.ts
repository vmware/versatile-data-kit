/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

import { requestAPI } from '../handler';
import { VdkOption } from '../vdkOptions/vdk_options';
import { getJobDataJsonObject, jobData, setJobDataToDefault } from '../jobData';
import {
  getNotebookInfo,
  getVdkCellIndices,
  jobdDataRequest,
  jobRequest,
  jobRunRequest
} from '../serverRequests';
import { Dialog, showErrorMessage } from '@jupyterlab/apputils';

jest.mock('../handler', () => {
  return {
    requestAPI: jest.fn()
  };
});

jest.mock('@jupyterlab/apputils', () => ({
  showErrorMessage: jest.fn(),
  Dialog: {
    okButton: jest.fn()
  }
}));

describe('jobdDataRequest', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should call requestAPI with the correct arguments', async () => {
    const mockData = {
      [VdkOption.NAME]: 'Test Job',
      [VdkOption.TEAM]: 'Test Team',
      [VdkOption.PATH]: '/test/job/path'
    };

    jobData.set(VdkOption.NAME, mockData[VdkOption.NAME]);
    jobData.set(VdkOption.TEAM, mockData[VdkOption.TEAM]);
    jobData.set(VdkOption.PATH, mockData[VdkOption.PATH]);

    (requestAPI as jest.Mock).mockResolvedValue(mockData);

    await jobdDataRequest();

    expect(requestAPI).toHaveBeenCalledTimes(1);
    expect(requestAPI).toHaveBeenCalledWith('job', {
      body: JSON.stringify(JSON.stringify(getJobDataJsonObject())),
      method: 'POST'
    });
    setJobDataToDefault();
  });

  it('should set jobData if requestAPI returns data', async () => {
    const mockData = {
      [VdkOption.NAME]: 'Test Job',
      [VdkOption.TEAM]: 'Test Team',
      [VdkOption.PATH]: '/test/job/path'
    };

    (requestAPI as jest.Mock).mockResolvedValue(mockData);

    await jobdDataRequest();

    expect(jobData.get(VdkOption.NAME)).toBe('Test Job');
    expect(jobData.get(VdkOption.TEAM)).toBe('Test Team');
    expect(jobData.get(VdkOption.PATH)).toBe('/test/job/path');
  });
});

describe('jobRunRequest()', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should call requestAPI to start a task and then poll for its completion, returning a successful result', async () => {
    const mockData = {
      [VdkOption.PATH]: '/test/job/path'
    };
    jobData.set(VdkOption.PATH, mockData[VdkOption.PATH]);

    const taskId = 'RUN-6266cd99-908c-480b-9a3e-8a30564736a4';
    const taskInitiationResponse = {
      error: '',
      message: `Task ${taskId} started`
    };
    const taskCompletionResponse = {
      task_id: taskId,
      status: 'completed',
      message: 'Operation completed successfully',
      error: null
    };

    (requestAPI as jest.Mock)
      .mockResolvedValueOnce(taskInitiationResponse)
      .mockResolvedValue(taskCompletionResponse);

    const result = await jobRunRequest();

    expect(requestAPI).toHaveBeenCalledWith('run', {
      body: JSON.stringify(getJobDataJsonObject()),
      method: 'POST'
    });
    expect(requestAPI).toHaveBeenCalledWith(`taskStatus?taskId=${taskId}`, {
      method: 'GET'
    });
    expect(result).toEqual({
      message: taskCompletionResponse.message,
      isSuccessful: true
    });
  });

  it('should call requestAPI with correct arguments and return unsuccessful result', async () => {
    const mockData = {
      [VdkOption.PATH]: '/test/job/path'
    };
    jobData.set(VdkOption.PATH, mockData[VdkOption.PATH]);

    const taskId = 'RUN-6266cd99-908c-480b-9a3e-8a30564736a4';
    const taskInitiationResponse = {
      error: '1',
      message: `Task ${taskId} started`
    };
    (requestAPI as jest.Mock).mockResolvedValueOnce(taskInitiationResponse);

    const result = await jobRunRequest();

    expect(requestAPI).toHaveBeenCalledWith('run', {
      body: JSON.stringify(getJobDataJsonObject()),
      method: 'POST'
    });
    expect(result).toEqual({
      message: taskInitiationResponse.message,
      isSuccessful: false
    });
  });
});

describe('jobRequest()', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should call requestAPI with the correct arguments', async () => {
    const mockData = {
      [VdkOption.NAME]: 'Test Job',
      [VdkOption.TEAM]: 'Test Team'
    };

    jobData.set(VdkOption.NAME, mockData[VdkOption.NAME]);
    jobData.set(VdkOption.TEAM, mockData[VdkOption.TEAM]);

    const endpoint = 'CREATE';
    const taskId = endpoint + '-6266cd99-908c-480b-9a3e-8a30564736a4';
    const taskInitiationResponse = {
      error: '',
      message: `Task ${taskId} started`
    };
    const taskCompletionResponse = {
      task_id: taskId,
      status: 'completed',
      message: 'Task completed successfully',
      error: null
    };

    (requestAPI as jest.Mock)
      .mockResolvedValueOnce(taskInitiationResponse)
      .mockResolvedValue(taskCompletionResponse);

    const result = await jobRequest(endpoint);

    // Verify the call for initiating the task
    expect(requestAPI).toHaveBeenCalledWith(endpoint, {
      body: JSON.stringify(getJobDataJsonObject()),
      method: 'POST'
    });

    // Verify the polling for task status
    expect(requestAPI).toHaveBeenCalledWith(`taskStatus?taskId=${taskId}`, {
      method: 'GET'
    });

    // Verify the final result
    expect(result).toEqual({
      message: taskCompletionResponse.message,
      isSuccessful: true
    });
  });

  it('should show an error message if requestAPI returns a serverVdkOperationResult with error', async () => {
    const mockData = {
      [VdkOption.NAME]: 'Test Job',
      [VdkOption.TEAM]: 'Test Team'
    };

    jobData.set(VdkOption.NAME, mockData[VdkOption.NAME]);
    jobData.set(VdkOption.TEAM, mockData[VdkOption.TEAM]);

    const endpoint = 'DEPLOY';
    const serverVdkOperationResultMock = {
      error: '1',
      message: `${endpoint} task failed`
    };
    (requestAPI as jest.Mock).mockResolvedValueOnce(
      serverVdkOperationResultMock
    );

    const result = await jobRequest(endpoint);

    expect(requestAPI).toHaveBeenCalledWith(endpoint, {
      body: JSON.stringify(getJobDataJsonObject()),
      method: 'POST'
    });
    expect(result).toEqual({
      message: serverVdkOperationResultMock.message,
      isSuccessful: false
    });
  });

  it('should show an error message if a task fails', async () => {
    const mockData = {
      [VdkOption.NAME]: 'Test Job',
      [VdkOption.TEAM]: 'Test Team'
    };

    jobData.set(VdkOption.NAME, mockData[VdkOption.NAME]);
    jobData.set(VdkOption.TEAM, mockData[VdkOption.TEAM]);

    const endpoint = 'DEPLOY';
    const taskId = endpoint + '-6266cd99-908c-480b-9a3e-8a30564736a4';
    const taskInitiationResponse = {
      error: '',
      message: `Task ${taskId} started`
    };
    const taskCompletionResponse = {
      task_id: taskId,
      status: 'failed',
      message: '',
      error: 'An error occurred'
    };

    (requestAPI as jest.Mock)
      .mockResolvedValueOnce(taskInitiationResponse)
      .mockResolvedValue(taskCompletionResponse);

    const result = await jobRequest(endpoint);

    // Verify the call for initiating the task
    expect(requestAPI).toHaveBeenCalledWith(endpoint, {
      body: JSON.stringify(getJobDataJsonObject()),
      method: 'POST'
    });

    // Verify the polling for task status
    expect(requestAPI).toHaveBeenCalledWith(`taskStatus?taskId=${taskId}`, {
      method: 'GET'
    });

    expect(showErrorMessage).toHaveBeenCalledWith(
      'Encountered an error while trying to connect the server. Error:',
      taskCompletionResponse.error,
      [Dialog.okButton()]
    );

    // Verify the final result
    expect(result).toEqual({
      message: taskCompletionResponse.error,
      isSuccessful: false
    });
  });
});

describe('getFailingNotebookInfo', () => {
  const mockFailingCellId = 'failing-cell-id';

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should return notebook info if requestAPI returns data', async () => {
    const expectedData = {
      path: '/path/to/notebook.ipynb',
      cellIndex: '2'
    };
    const expectedRequestBody = {
      cellId: mockFailingCellId,
      jobPath: '/test/job/path'
    };
    (requestAPI as jest.Mock).mockResolvedValue(expectedData);
    const result = await getNotebookInfo(mockFailingCellId);

    expect(result).toEqual(expectedData);
    expect(requestAPI).toHaveBeenCalledWith('notebook', {
      body: JSON.stringify(expectedRequestBody),
      method: 'POST'
    });
  });
});

describe('getVdkCellIndices', () => {
  const nbPath = '/path/to/notebook.ipynb';

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should call requestAPI with correct arguments', async () => {
    await getVdkCellIndices(nbPath);

    expect(requestAPI).toHaveBeenCalledWith('vdkCellIndices', {
      body: JSON.stringify({
        nbPath: nbPath
      }),
      method: 'POST'
    });
  });

  it('should return an array of numbers if the request is successful', async () => {
    (requestAPI as jest.Mock).mockResolvedValue([1, 2, 3]);
    const result = await getVdkCellIndices(nbPath);
    expect(result).toEqual([1, 2, 3]);
  });
});
