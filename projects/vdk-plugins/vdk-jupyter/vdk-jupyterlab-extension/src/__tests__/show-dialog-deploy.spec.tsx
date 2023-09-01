import { Dialog, showDialog } from '@jupyterlab/apputils';
import { jobData } from '../jobData';
import React from 'react';
import { VdkOption } from '../vdkOptions/vdk_options';
import { jobRunRequest } from '../serverRequests';
import DeployJobDialog, {
  showCreateDeploymentDialog
} from '../components/DeployJob';
import { VDKCheckbox } from '../components/VdkCheckbox';
import {StatusButton} from "../components/StatusButton";
import {RUN_JOB_BUTTON_LABEL} from "../utils";


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

const mockStatusButton = {
    show: jest.fn()
} as unknown as StatusButton;

describe('showCreateDeploymentDialog', () => {
    beforeEach(() => {
      jobData.set(VdkOption.PATH, 'test/path');
      jobData.set(VdkOption.NAME, 'test-name');
      jobData.set(VdkOption.TEAM, 'test-team');
      jobData.set(VdkOption.DEPLOYMENT_REASON, 'test-reason');
      jest.resetAllMocks()

      const mockResult = { button: { accept: true }, value: false };
      (showDialog as jest.Mock).mockResolvedValueOnce(mockResult);

      (jobRunRequest as jest.Mock).mockResolvedValueOnce({
        message: 'Job completed successfully!',
        status: true
      });
    });

    it('should show a dialog with the Create Deployment title and \
        a DeployJobDialog component as its body', async () => {

      await showCreateDeploymentDialog(mockStatusButton);

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

    it('should not call jobRunRequest when reason is empty', async () => {
      jobData.set(VdkOption.DEPLOYMENT_REASON, '');
      await showCreateDeploymentDialog(mockStatusButton);
      expect(jobRunRequest).not.toHaveBeenCalled();
    });

    it('should handle failures in jobRunRequest', async () => {
      (jobRunRequest as jest.Mock).mockRejectedValueOnce(new Error('Failed to run job'));

      await showCreateDeploymentDialog(mockStatusButton);

      expect(showDialog).toHaveBeenCalledWith(expect.objectContaining({title: RUN_JOB_BUTTON_LABEL} ) );
    });

    it('should show a Status Dialog when operations start', async () => {
        await showCreateDeploymentDialog(mockStatusButton);

        expect(mockStatusButton.show).toHaveBeenCalled();
    });

  });
