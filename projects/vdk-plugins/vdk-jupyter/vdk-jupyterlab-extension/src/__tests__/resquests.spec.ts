import { requestAPI } from '../handler';
import { VdkOption } from '../vdkOptions/vdk_options';
import { getJobDataJsonObject, jobData, setJobDataToDefault } from '../jobData';
import { jobdDataRequest, jobRequest, jobRunRequest } from '../serverRequests';

jest.mock('../handler', () => {
    return {
        requestAPI: jest.fn()
    };
});

window.alert = jest.fn();

describe('jobdDataRequest', () => {
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('should call requestAPI with the correct arguments', async () => {
        jobData.set(VdkOption.NAME, 'Test Job');
        jobData.set(VdkOption.TEAM, 'Test Team');
        jobData.set(VdkOption.PATH, '/test/job/path');

        const mockData = {
            [VdkOption.NAME]: 'Test Job',
            [VdkOption.TEAM]: 'Test Team',
            [VdkOption.PATH]: '/test/job/path'
        };

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
    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('should call requestAPI with correct arguments and return successful result', async () => {
        const expectedMessage =
            'Job execution has finished with status success \n See vdk_logs.txt file for more!';
        const expectedResponse = { message: 'success', status: true };
        (requestAPI as jest.Mock).mockResolvedValue(expectedResponse);

        const result = await jobRunRequest();

        expect(requestAPI).toHaveBeenCalledTimes(1);
        expect(result).toEqual({ message: expectedMessage, status: true });
    });

    it('should call requestAPI with correct arguments and return unsuccessful result', async () => {
        const expectedError = new Error('1');
        (requestAPI as jest.Mock).mockResolvedValue(expectedError);

        const result = await jobRunRequest();

        expect(requestAPI).toHaveBeenCalledTimes(1);
        expect(result).toEqual({
            message:
                'Job execution has finished with status ' +
                '1' +
                ' \n See vdk_logs.txt file for more!',
            status: true
        });
    });
});

describe('jobRequest()', () => {
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

        const alertMock = jest.spyOn(window, 'alert').mockImplementationOnce(() => { });

        await jobRequest(endPoint);

        expect(alertMock as jest.Mock).toHaveBeenCalledWith(serverVdkOperationResultMock['message']);
        expect(requestAPI).toHaveBeenCalledWith(endPoint, {
            body: JSON.stringify(getJobDataJsonObject()),
            method: 'POST'
        });
        (window.alert as jest.Mock).mockClear();
    });
});