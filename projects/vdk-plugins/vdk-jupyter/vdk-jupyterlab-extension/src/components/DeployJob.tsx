import React, { Component } from 'react';
import { checkIfVdkOptionDataIsDefined, jobData } from '../jobData';
import { VdkOption } from '../vdkOptions/vdk_options';
import VDKTextInput from './VdkTextInput';
import { Dialog, showDialog, showErrorMessage } from '@jupyterlab/apputils';
import { jobRequest, jobRunRequest } from '../serverRequests';
import { IJobFullProps } from './props';
import { CREATE_DEP_BUTTON_LABEL } from '../utils';
import { StatusButton } from './StatusButton';

export default class DeployJobDialog extends Component<IJobFullProps> {
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
          option={VdkOption.PATH}
          value={this.props.jobPath}
          label="Path to job directory:"
        ></VDKTextInput>
        <VDKTextInput
          option={VdkOption.DEPLOYMENT_REASON}
          value="reason"
          label="Deployment reason:"
        ></VDKTextInput>
      </>
    );
  }
}

export async function showCreateDeploymentDialog(statusButton?: StatusButton) {
  const result = await showDialog({
    title: CREATE_DEP_BUTTON_LABEL,
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
        title: CREATE_DEP_BUTTON_LABEL,
        body: 'The job will be executed once before deployment.',
        buttons: [
          Dialog.cancelButton({ label: 'Cancel' }),
          Dialog.okButton({ label: 'Continue' })
        ]
      });
      if (runConfirmationResult.button.accept) {
        statusButton?.show('Deploy', jobData.get(VdkOption.PATH)!);
        const { message, status } = await jobRunRequest();
        if (status) {
          if (
            await checkIfVdkOptionDataIsDefined(VdkOption.DEPLOYMENT_REASON)
          ) {
            await jobRequest('deploy');
          }
        } else {
          await showErrorMessage(
            'Encоuntered an error while running the job!',
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
