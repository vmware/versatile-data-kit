/*import RunJobDialog, { showRunJobDialog } from '../components/RunJob';
import { Dialog, showDialog } from '@jupyterlab/apputils';
import { jobData } from '../jobData';
import React from 'react';
import { VdkOption } from '../vdkOptions/vdk_options';
import { jobRequest, jobRunRequest } from '../serverRequests';
import DownloadJobDialog, {
  showDownloadJobDialog
} from '../components/DownloadJob';
import DeployJobDialog, {
  showCreateDeploymentDialog
} from '../components/DeployJob';
import CreateJobDialog, { showCreateJobDialog } from '../components/CreateJob';
import DeleteJobDialog, { showDeleteJobDialog } from '../components/DeleteJob';

// Mock the showDialog function
jest.mock('@jupyterlab/apputils', () => ({
  showDialog: jest.fn(),
  Dialog: {
    okButton: jest.fn(),
    cancelButton: jest.fn()
  }
}));
jest.mock('../serverRequests', () => ({
  jobRunRequest: jest.fn(),
  jobRequest: jest.fn()
}));

describe('showRunJobDialog', () => {
  beforeEach(() => {
    jobData.set(VdkOption.PATH, 'test/path');
    // Mock the result of the showDialog function
    const mockResult = { button: { accept: true } };
    (showDialog as jest.Mock).mockResolvedValueOnce(mockResult);
    // Mock the jobRunRequest function
    (jobRunRequest as jest.Mock).mockResolvedValueOnce({
      message: 'Job completed successfully!',
      status: true
    });
  });

  it('should show a dialog with the Run Job title and a RunJobDialog component as its body', async () => {
    await showRunJobDialog();

    // Expect the showDialog function to have been called with the correct parameters
    expect(showDialog).toHaveBeenCalledWith({
      title: 'Run Job',
      body: <RunJobDialog jobPath={jobData.get(VdkOption.PATH)!} />,
      buttons: [Dialog.okButton(), Dialog.cancelButton()]
    });
  });

  it('should call the jobRunRequest function if the user clicks the accept button', async () => {
    // Call the function
    await showRunJobDialog();

    // Expect the jobRunRequest function to have been called
    expect(jobRunRequest).toHaveBeenCalled();
    expect(showDialog).toHaveBeenCalledWith(
      {
        title: 'Run Job',
            body: <div className='vdk-run-dialog-message-container'>
            <p className='vdk-run-dialog-message'>Success!</p>
            <span className='vdk-tick-element'>✔</span>
          </div>,
            buttons: [Dialog.okButton()]
      }
    );
  });
});

describe('showDownloadJobDialog', () => {
  beforeEach(() => {
    jobData.set(VdkOption.PATH, 'test/path');
    // Mock the result of the showDialog function
    const mockResult = { button: { accept: true } };
    (showDialog as jest.Mock).mockResolvedValueOnce(mockResult);
  });

  it('should show a dialog with the Download Job title and a DownloadJobDialog component as its body', async () => {
    // Call the function
    await showDownloadJobDialog();

    // Expect the showDialog function to have been called with the correct parameters
    expect(showDialog).toHaveBeenCalledWith({
      title: 'Download Job',
      body: <DownloadJobDialog jobPath={jobData.get(VdkOption.PATH)!} />,
      buttons: [Dialog.okButton(), Dialog.cancelButton()]
    });
  });

  it('should call the jobRequest function with "download" as the argument if the user clicks the accept button', async () => {
    // Call the function
    await showDownloadJobDialog();

    // Expect the jobRequest function to have been called with the correct arguments
    expect(jobRequest).toHaveBeenCalledWith('download');
  });
});

describe('showCreateDeploymentDialog', () => {
  beforeEach(() => {
    jobData.set(VdkOption.PATH, 'test/path');
    jobData.set(VdkOption.NAME, 'test-name');
    jobData.set(VdkOption.TEAM, 'test-team');
    // Mock the result of the showDialog function
    const mockResult = { button: { accept: true }, value: true };
    (showDialog as jest.Mock).mockResolvedValueOnce(mockResult);
    // Mock the jobRunRequest function
    (jobRunRequest as jest.Mock).mockResolvedValueOnce({
      message: 'Job completed successfully!',
      status: true
    });
  });

  it('should show a dialog with the Create Deployment title and a DeployJobDialog component as its body', async () => {
    // Call the function
    await showCreateDeploymentDialog();

    // Expect the first showDialog function to have been called with the correct parameters
    expect(showDialog).toHaveBeenCalledWith({
      title: 'Create Deployment',
      body: (
        <DeployJobDialog
          jobName={jobData.get(VdkOption.NAME)!}
          jobPath={jobData.get(VdkOption.PATH)!}
          jobTeam={jobData.get(VdkOption.TEAM)!}
        />
      ),
      buttons: [Dialog.okButton(), Dialog.cancelButton()]
    });
  });
});

describe('showCreateJobDialog', () => {
  beforeEach(() => {
    jobData.set(VdkOption.PATH, 'test/path');
    jobData.set(VdkOption.NAME, 'test-name');
    jobData.set(VdkOption.TEAM, 'test-team');
    // Mock the result of the showDialog function
    const mockResult = { button: { accept: true }, value: true };
    (showDialog as jest.Mock).mockResolvedValueOnce(mockResult);
  });

  it('should call showDialog with correct arguments', async () => {
    await showCreateJobDialog();

    expect(showDialog).toHaveBeenCalledWith({
      title: 'Create Job',
      body:<CreateJobDialog
      jobPath={jobData.get(VdkOption.PATH)!}
      jobName={jobData.get(VdkOption.NAME)!}
      jobTeam={jobData.get(VdkOption.TEAM)!}
    ></CreateJobDialog>,
      buttons: [Dialog.okButton(), Dialog.cancelButton()]
    });
  });

  it('should call jobRequest function with "create" argument when user accepts dialog', async () => {
    await showCreateJobDialog();

    expect(jobRequest).toHaveBeenCalledWith('create');
  });
});

describe('showDeleteJobDialog', () => {
  jobData.set(VdkOption.PATH, 'my-job');
  jobData.set(VdkOption.NAME, 'my-team');
  jobData.set(VdkOption.REST_API_URL, 'https://example.com');

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should delete the job when the user confirms', async () => {
    const showDialogMock = showDialog as jest.MockedFunction<typeof showDialog>;
    const jobRequestMock = jobRequest as jest.MockedFunction<typeof jobRequest>;
    const acceptResult = { button: { accept: true } };
    const confirmResult = { button: { accept: true } };

    // Mock the first dialog
    (showDialogMock as jest.Mock).mockResolvedValueOnce(acceptResult);

    // Mock the second dialog
    (showDialogMock as jest.Mock).mockResolvedValueOnce(confirmResult);

    // Call the function
    await showDeleteJobDialog();

    // Check the results
    expect(showDialogMock).toHaveBeenCalledWith({
      title: 'Delete Job',
      body: (
        <DeleteJobDialog
          jobName={jobData.get(VdkOption.NAME)!}
          jobTeam={jobData.get(VdkOption.TEAM)!}
        ></DeleteJobDialog>
      ),
      buttons: [Dialog.okButton(), Dialog.cancelButton()]
    });
    expect(jobRequestMock).toHaveBeenCalledWith('delete');
  });

  it('should not delete the job when the user does not confirm', async () => {
    const showDialogMock = showDialog as jest.MockedFunction<typeof showDialog>;
    const jobRequestMock = jobRequest as jest.MockedFunction<typeof jobRequest>;
    const refuseResult = { button: { accept: false } };

    // Mock the first dialog
    (showDialogMock as jest.Mock).mockResolvedValueOnce(refuseResult);

    // Call the function
    await showDeleteJobDialog();

    // Check the results
    expect(showDialogMock).toHaveBeenCalledWith({
      title: 'Delete Job',
      body: (
        <DeleteJobDialog
          jobName={jobData.get(VdkOption.NAME)!}
          jobTeam={jobData.get(VdkOption.TEAM)!}
        ></DeleteJobDialog>
      ),
      buttons: [Dialog.okButton(), Dialog.cancelButton()]
    });
    expect(jobRequestMock).toHaveBeenCalledTimes(0);
  });
});
*/
