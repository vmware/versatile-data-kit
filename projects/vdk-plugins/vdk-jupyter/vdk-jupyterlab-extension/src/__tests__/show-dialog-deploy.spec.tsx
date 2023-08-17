import { Dialog, showDialog, showErrorMessage } from '@jupyterlab/apputils';
import { jobData } from '../jobData';
import React from 'react';
import { VdkOption } from '../vdkOptions/vdk_options';
import { jobRunRequest } from '../serverRequests';
import DeployJobDialog, {
  showCreateDeploymentDialog
} from '../components/DeployJob';
import { VDKCheckbox } from '../components/VdkCheckbox';


jest.mock('@jupyterlab/apputils', () => ({
  showDialog: jest.fn(),
  showErrorMessage: jest.fn(),
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

      const mockResult = { button: { accept: true }, value: true };
      (showDialog as jest.Mock).mockResolvedValueOnce(mockResult);

      (jobRunRequest as jest.Mock).mockResolvedValueOnce({
        message: 'Job completed successfully!',
        status: true
      });
    });

    it('should show a dialog with the Create Deployment title and \
        a DeployJobDialog component as its body', async () => {

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
            <VDKCheckbox
              checked={true}
              onChange={expect.any(Function)}
              label="Run data job before deployment"
              id="deployRun"
            />
          </>
        ),
        buttons: [Dialog.okButton(), Dialog.cancelButton()]
      });
    });

    it('should not call jobRunRequest when checkbox is unchecked', async () => {
      const mockResult = { button: { accept: true }, value: false };
      (showDialog as jest.Mock).mockResolvedValueOnce(mockResult);

      await showCreateDeploymentDialog();
      expect(jobRunRequest).not.toHaveBeenCalled();
    });

    it('should handle failures in jobRunRequest', async () => {
      (jobRunRequest as jest.Mock).mockRejectedValueOnce(new Error('Failed to run job'));

      await showCreateDeploymentDialog();

      expect(showErrorMessage).toHaveBeenCalledTimes(1);
    });
  });
