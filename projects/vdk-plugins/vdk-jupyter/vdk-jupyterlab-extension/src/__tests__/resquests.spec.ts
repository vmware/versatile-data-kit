/*
 * Copyright 2023-2023 VMware, Inc.
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

jest.mock('../handler', () => {
  return {
    requestAPI: jest.fn()
  };
});

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

  it('should call requestAPI with correct arguments and return successful result', async () => {
    const expectedMessage = '0';
    const expectedResponse = { message: '0', isSuccessful: true };
    (requestAPI as jest.Mock).mockResolvedValue(expectedResponse);

    const result = await jobRunRequest();

    expect(requestAPI).toHaveBeenCalledTimes(1);
    expect(result).toEqual({ message: expectedMessage, isSuccessful: true });
  });

  it('should call requestAPI with correct arguments and return unsuccessful result', async () => {
    const expectedError = new Error('1');
    (requestAPI as jest.Mock).mockResolvedValue(expectedError);

    const result = await jobRunRequest();

    expect(requestAPI).toHaveBeenCalledTimes(1);
    expect(result).toEqual({
      message: '1',
      isSuccessful: false
    });
  });
});

describe('jobRequest()', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should call requestAPI with the correct arguments', async () => {
    const endPoint = 'your-endpoint-url';
    const expectedRequestBody = JSON.stringify(getJobDataJsonObject());
    const expectedRequestMethod = 'POST';

    await jobRequest(endPoint);

    expect(requestAPI).toHaveBeenCalledWith(endPoint, {
      body: expectedRequestBody,
      method: expectedRequestMethod
    });
  });

  it('should show a success message if requestAPI returns a serverVdkOperationResult without errors', async () => {
    const endPoint = 'your-endpoint-url';
    const serverVdkOperationResultMock = {
      error: '',
      message: 'Operation completed successfully'
    };
    (requestAPI as jest.Mock).mockResolvedValue(serverVdkOperationResultMock);

    await jobRequest(endPoint);

    expect(requestAPI).toHaveBeenCalledWith(endPoint, {
      body: JSON.stringify(getJobDataJsonObject()),
      method: 'POST'
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
