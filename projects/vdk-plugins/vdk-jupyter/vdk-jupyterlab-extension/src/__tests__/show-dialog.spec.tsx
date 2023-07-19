import RunJobDialog, { showRunJobDialog } from '../components/RunJob';
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
import { VdkErrorMessage } from '../components/VdkErrorMessage';

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
  });

  it('should show a dialog with the Run Job title and a RunJobDialog component as its body', async () => {
    (jobRunRequest as jest.Mock).mockResolvedValueOnce({
      message: 'Job completed successfully!',
      status: true
    });

    await showRunJobDialog();

    // Expect the showDialog function to have been called with the correct parameters
    expect(showDialog).toHaveBeenCalledWith({
      title: 'Run Job',
      body: <RunJobDialog jobPath={jobData.get(VdkOption.PATH)!} />,
      buttons: [Dialog.okButton(), Dialog.cancelButton()]
    });
  });

  it('should call the jobRunRequest function if the user clicks the accept button and return success dialog', async () => {
    (jobRunRequest as jest.Mock).mockResolvedValueOnce({
      message: 'Job completed successfully!',
      status: true
    });

    // Call the function
    await showRunJobDialog();

    // Expect the jobRunRequest function to have been called
    expect(jobRunRequest).toHaveBeenCalled();
    expect(showDialog).toHaveBeenCalledWith(
      {
        title: 'Run Job',
        body: (
          <div className="vdk-run-dialog-message-container">
            <p className="vdk-run-dialog-message">
              The job was executed successfully!
            </p>
          </div>
        ),
        buttons: [Dialog.okButton()]
      }
    );
  });

  it('should call the jobRunRequest function if the user clicks the accept button and return failing standard run dialog', async () => {
    (jobRunRequest as jest.Mock).mockResolvedValueOnce({
      message: 'Error message',
      status: false
    });
    const errorMessage = new VdkErrorMessage('ERROR : ' + 'Error message');
    // Call the function
    await showRunJobDialog();

    // Expect the jobRunRequest function to have been called
    expect(jobRunRequest).toHaveBeenCalled();
    expect(showDialog).toHaveBeenCalledWith(
      {
        title: 'Run Job',
          body: (
            <div className="vdk-run-error-message ">
              <p>{errorMessage.exception_message}</p>
              <p>{errorMessage.what_happened}</p>
              <p>{errorMessage.why_it_happened}</p>
              <p>{errorMessage.consequences}</p>
              <p>{errorMessage.countermeasures}</p>
            </div>
          ),
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
