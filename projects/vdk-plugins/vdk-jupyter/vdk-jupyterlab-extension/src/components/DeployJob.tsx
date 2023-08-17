import React, { Component } from 'react';
import { checkIfVdkOptionDataIsDefined, jobData } from '../jobData';
import { VdkOption } from '../vdkOptions/vdk_options';
import VDKTextInput from './VdkTextInput';
import { Dialog, showDialog, showErrorMessage } from '@jupyterlab/apputils';
import { jobRequest, jobRunRequest } from '../serverRequests';
import { IJobFullProps } from './props';
import { CREATE_DEP_BUTTON_LABEL, RUN_JOB_BUTTON_LABEL } from '../utils';
import { VdkErrorMessage } from './VdkErrorMessage';

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

export async function showCreateDeploymentDialog() {
  let runBeforeDeploy = true;

  const handleCheckboxChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    runBeforeDeploy = event.target.checked;
  };

  const result = await showDialog({
    title: CREATE_DEP_BUTTON_LABEL,
    body: (
      <>
        <DeployJobDialog
          jobName={jobData.get(VdkOption.NAME) || ''}
          jobPath={jobData.get(VdkOption.PATH) || ''}
          jobTeam={jobData.get(VdkOption.TEAM) || ''}
        />
        <div>
          <input
            type="checkbox"
            name="deployRun"
            id="deployRun"
            className="jp-vdk-checkbox"
            onChange={handleCheckboxChange}
            defaultChecked={true}
          />
          <label className="checkboxLabel" htmlFor="deployRun">
            Run before deployment
          </label>
        </div>
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
      if (runBeforeDeploy) {
        const { message, status } = await jobRunRequest();
        if (status) {
          await jobRequest('deploy');
        } else {
          const errorMessage = new VdkErrorMessage('ERROR : ' + message);
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
        await jobRequest('deploy');
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
