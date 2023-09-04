import React, { Component } from 'react';
import { jobData } from '../jobData';
import { VdkOption } from '../vdkOptions/vdk_options';
import VDKTextInput from './VdkTextInput';
import { Dialog, showDialog } from '@jupyterlab/apputils';
import { jobRequest } from '../serverRequests';
import { IJobFullProps } from './props';
import { CREATE_JOB_BUTTON_LABEL } from '../utils';
import {StatusButton} from "./StatusButton";

export default class CreateJobDialog extends Component<IJobFullProps> {
  /**
   * Returns a React component for rendering a create menu.
   *
   * @param props - component properties
   * @returns React component
   */
  constructor(props: IJobFullProps) {
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
      </>
    );
  }
}

export async function showCreateJobDialog(statusButton: StatusButton) {
  const result = await showDialog({
    title: CREATE_JOB_BUTTON_LABEL,
    body: (
      <CreateJobDialog
        jobPath={jobData.get(VdkOption.PATH)!}
        jobName={jobData.get(VdkOption.NAME)!}
        jobTeam={jobData.get(VdkOption.TEAM)!}
      ></CreateJobDialog>
    ),
    buttons: [Dialog.okButton(), Dialog.cancelButton()]
  });
  if (result.button.accept) {
    statusButton.show('Create', jobData.get(VdkOption.PATH)!);
    // We only handle the successful deployment scenario.
    // The failing scenario is handled in the request itself.
    const creation = await jobRequest('create');
    if (creation.isSuccessful && creation.message) {
      alert(creation.message);
    }
  }
}
