import React, { Component } from 'react';
import { jobData } from '../jobData';
import { VdkOption } from '../vdkOptions/vdk_options';
import VDKTextInput from './VdkTextInput';
import { Dialog, showDialog } from '@jupyterlab/apputils';
import { jobRequest } from '../serverRequests';
import { IJobNameAndTeamProps, IJobPathProp } from './props';


export default class CreateJobDialog extends Component<(IJobNameAndTeamProps & IJobPathProp)> {
  /**
   * Returns a React component for rendering a create menu.
   *
   * @param props - component properties
   * @returns React component
   */
  constructor(props: (IJobNameAndTeamProps & IJobPathProp)) {
    super(props);
  }
  /**
   * Renders a dialog for creating a data job.
   *
   * @returns React element
   */
  render(): React.ReactElement {
    return (
      <>
        <div className="jp-vdk-checkbox-wrappers">
          <div>
            <input
              type="checkbox"
              name="Local"
              id="Local"
              className="jp-vdk-checkbox"
              onClick={this._onLocalClick()}
            />
            <label className="checkboxLabel" htmlFor="Local">
              Local
            </label>
          </div>
          <div>
            <input
              type="checkbox"
              name="Cloud"
              id="Cloud"
              className="jp-vdk-checkbox"
              onClick={this._onCloudClick()}
            />
            <label className="checkboxLabel" htmlFor="Cloud">
              Cloud
            </label>
          </div>
        </div>
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
      </>
    );
  }
  /**
   * Callback invoked upon choosing local checkbox
   */
  private _onLocalClick() {
    return (event: React.MouseEvent) => {
      this.setJobFlags('Local', 'jobPath');
    };
  }
  /**
   * Callback invoked upon choosing cloud checkbox
   */
  private _onCloudClick() {
    return (event: React.MouseEvent) => {
      this.setJobFlags('Cloud', 'jobRestApiUrl');
    };
  }
  /**
   * Function that sets job's cloud/local flags
   */
  private setJobFlags(flag: string, inputId: string) {
    let checkbox = document.getElementById(flag);
    let input = document.getElementById(inputId);
    if (checkbox?.classList.contains('checked')) {
      checkbox.classList.remove('checked');
      input?.parentElement?.classList.add('hidden');
      if (flag === 'Cloud') {
        jobData.set(VdkOption.CLOUD, '');
      } else {
        jobData.set(VdkOption.LOCAL, '');
      }
    } else {
      checkbox?.classList.add('checked');
      if (flag === 'Cloud') {
        jobData.set(VdkOption.CLOUD, '1');
      } else {
        jobData.set(VdkOption.LOCAL, '1');
      }
      input?.parentElement?.classList.remove('hidden');
    }
  }
}

export async function showCreateJobDialog() {
  const result = await showDialog({
    title: 'Create Job',
    body: (
      <CreateJobDialog
        jobPath={sessionStorage.getItem('current-path')!}
        jobName="default-name"
        jobTeam='default-team'
      ></CreateJobDialog>
    ),
    buttons: [Dialog.okButton(), Dialog.cancelButton()]
  });
  if (result.button.accept) {
    await jobRequest('create');
  }
}
