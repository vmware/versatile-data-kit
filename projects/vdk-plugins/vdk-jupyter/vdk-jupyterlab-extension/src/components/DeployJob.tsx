import React, { Component } from 'react';
import { checkIfVdkOptionDataIsDefined, jobData } from '../jobData';
import { VdkOption } from '../vdkOptions/vdk_options';
import VDKTextInput from './VdkTextInput';
import { Dialog, showDialog, showErrorMessage } from '@jupyterlab/apputils';
import { jobRequest, jobRunRequest } from '../serverRequests';
import { IJobFullProps } from './props';
import { CREATE_DEP_BUTTON_LABEL, RUN_JOB_BUTTON_LABEL } from '../utils';
import { VdkErrorMessage } from './VdkErrorMessage';
import { VDKCheckbox } from './VdkCheckbox';
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
          value=""
          label="Deployment reason:"
        ></VDKTextInput>
      </>
    );
  }
}

export async function showCreateDeploymentDialog(statusButton: StatusButton) {
  let runBeforeDeploy = true;

  const result = await showDialog({
    title: CREATE_DEP_BUTTON_LABEL,
    body: (
      <>
        <DeployJobDialog
          jobName={jobData.get(VdkOption.NAME) || ''}
          jobPath={jobData.get(VdkOption.PATH) || ''}
          jobTeam={jobData.get(VdkOption.TEAM) || ''}
        />
        <VDKCheckbox
          checked={true}
          onChange={checked => (runBeforeDeploy = checked)}
          label="Run data job before deployment"
          id="deployRun"
        />
      </>
    ),
    buttons: [Dialog.okButton(), Dialog.cancelButton()]
  });

  const resultButtonClicked = !result.value && result.button.accept;
  if (
    resultButtonClicked &&
    (await checkIfVdkOptionDataIsDefined(VdkOption.DEPLOYMENT_REASON))
  ) {
    try {
      statusButton.show('Deploy', jobData.get(VdkOption.PATH)!);
      if (runBeforeDeploy) {
        const run = await jobRunRequest();
        if (run.isSuccessful) {
          const deployment = await jobRequest('deploy');
          // We only handle the successful deployment scenario.
          // The failing scenario is handled in the request itself.
          if (deployment.isSuccessful && deployment.message) {
            alert(
              'The test job run completed successfully! \n' + deployment.message
            );
          }
        } else {
          const errorMessage = new VdkErrorMessage('ERROR : ' + run.message);
          showDialog({
            title: RUN_JOB_BUTTON_LABEL,
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
          });
        }
      } else {
        const deployment = await jobRequest('deploy');
        if (deployment.isSuccessful && deployment.message) {
          alert(deployment.message);
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
