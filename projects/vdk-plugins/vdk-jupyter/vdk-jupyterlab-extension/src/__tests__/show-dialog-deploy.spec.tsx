import { Dialog, showDialog } from '@jupyterlab/apputils';
import { jobData } from '../jobData';
import React from 'react';
import { VdkOption } from '../vdkOptions/vdk_options';
import {jobRunRequest } from '../serverRequests';
import DeployJobDialog, {
  showCreateDeploymentDialog
} from '../components/DeployJob';

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

    it('should show a dialog with the Create Deployment title and \
        a DeployJobDialog component as its body', async () => {
      // Call the function
      await showCreateDeploymentDialog();

      // Expect the first showDialog function to have been called with the correct parameters
      expect(showDialog).toHaveBeenCalledWith({
        title: 'Create Deployment',
        body: (
            <>
            <DeployJobDialog
              jobName={jobData.get(VdkOption.NAME)!}
              jobPath={jobData.get(VdkOption.PATH)!}
              jobTeam={jobData.get(VdkOption.TEAM)!}
            />
            <div>
              <input
                type="checkbox"
                name="deployRun"
                id="deployRun"
                className="jp-vdk-checkbox"
                onChange={expect.any(Function)}
              />
              <label className="checkboxLabel" htmlFor="deployRun">
                Run before deployment
              </label>
            </div>
          </>
        ),
        buttons: [Dialog.okButton(), Dialog.cancelButton()]
      });
    });
  });
