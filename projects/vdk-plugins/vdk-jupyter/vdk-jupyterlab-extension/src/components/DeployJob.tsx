import React, { Component } from 'react';
import { jobData } from '../jobData';
import { VdkOption } from '../vdkOptions/vdk_options';
import VDKTextInput from './VdkTextInput';
import { Dialog, showDialog, showErrorMessage } from '@jupyterlab/apputils';
import { jobRequest, jobRunRequest } from '../serverRequests';
import { IJobFullProps } from './props';


export default class DeployJobDialog extends Component<(IJobFullProps)> {
  /**
   * Returns a React component for rendering a Deploy menu.
   *
   * @param props - component properties
   * @returns React component
   */
  constructor(props: IJobFullProps) {
    super(props);
  }
  /**
   * Renders a dialog for creating a new deployment of a Data Job.
   *
   * @returns React element
   */
  render(): React.ReactElement {
    return (
      <>
        <VDKTextInput
          option={VdkOption.NAME}
          value={this.props.jobName}
          label="Job Name:"
        ></VDKTextInput>
        <VDKTextInput
          option={VdkOption.TEAM}
          value={this.props.jobTeam}
          label="Job Team:"
        ></VDKTextInput>
        <VDKTextInput
          option={VdkOption.REST_API_URL}
          value="http://my_vdk_instance"
          label="Rest API URL:"
        ></VDKTextInput>
        <VDKTextInput
          option={VdkOption.PATH}
          value={this.props.jobPath}
          label="Path to job directory:"
        ></VDKTextInput>
        <VDKTextInput
          option={VdkOption.DEPLOYMENT_REASON}
          value="reason"
          label="Deployment reason:"
        ></VDKTextInput>
        <div>
          <input
            type="checkbox"
            name="enable"
            id="enable"
            className="jp-vdk-checkbox"
            onClick={this.onEnableClick()}
          />
          <label className="checkboxLabel" htmlFor="enable">
            Enable
          </label>
        </div>
      </>
    );
  }
  /**
   * Callback invoked upon choosing Enable checkbox
   */
  private onEnableClick() {
    return (event: React.MouseEvent) => {
      let checkbox = document.getElementById('enable');
      if (checkbox?.classList.contains('checked')) {
        checkbox.classList.remove('checked');
        jobData.set(VdkOption.DEPLOY_ENABLE, '');
      } else {
        checkbox?.classList.add('checked');
        jobData.set(VdkOption.DEPLOY_ENABLE, '1');
      }
    };
  }
}

export async function showCreateDeploymentDialog() {
  const result = await showDialog({
    title: 'Create Deployment',
    body: (
      <DeployJobDialog
        jobName={jobData.get(VdkOption.NAME)!}
        jobPath={jobData.get(VdkOption.PATH)!}
        jobTeam={jobData.get(VdkOption.TEAM)!}
      ></DeployJobDialog>
    ),
    buttons: [Dialog.okButton(), Dialog.cancelButton()]
  });
  const resultButtonClicked = !result.value && result.button.accept;
  if (resultButtonClicked) {
    try {
      const runConfirmationResult = await showDialog({
        title: 'Create deployment',
        body: 'The job will be executed once before deployment.',
        buttons: [
          Dialog.cancelButton({ label: 'Cancel' }),
          Dialog.okButton({ label: 'Continue' })
        ]
      });
      if (runConfirmationResult.button.accept) {
        let { message, status } = await jobRunRequest();
        if (status) {
          jobRequest("deploy");
        } else {
          showErrorMessage(
            'Encauntered an error while running the job!',
            message,
            [Dialog.okButton()]
          );
        }
      }
    } catch (error) {
      await showErrorMessage(
        'Encountered an error when deploying the job. Error:',
        error,
        [Dialog.okButton()]
      );
    }
  }
}
