import React, { Component } from 'react';
import { VdkOption } from '../vdkOptions/vdk_options';
import VDKTextInput from './VdkTextInput';
import { Dialog, showDialog, showErrorMessage } from '@jupyterlab/apputils';
import { jobData } from '../jobData';
import { jobRequest } from '../serverRequests';
import { IJobNameAndTeamProps } from './props';


export default class DeleteJobDialog extends Component<IJobNameAndTeamProps> {
  /**
   * Returns a React component for rendering a delete menu.
   *
   * @param props - component properties
   * @returns React component
   */
  constructor(props: IJobNameAndTeamProps) {
    super(props);
  }
  /**
   * Renders a dialog for deleting data job.
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
      </>
    );
  }
}

export async function showDeleteJobDialog() {
  const result = await showDialog({
    title: 'Delete Job',
    body: (
      <DeleteJobDialog
        jobName={jobData.get(VdkOption.NAME)!}
        jobTeam={jobData.get(VdkOption.TEAM)!}
      ></DeleteJobDialog>
    ),
    buttons: [Dialog.okButton(), Dialog.cancelButton()]
  });
  if (result.button.accept) {
    try {
      const finalResult = await showDialog({
        title: 'Delete a data job',
        body:
          'Do you really want to delete the job with name ' +
          jobData.get(VdkOption.NAME) +
          '?',
        buttons: [
          Dialog.cancelButton({ label: 'Cancel' }),
          Dialog.okButton({ label: 'Yes' })
        ]
      });
      if (finalResult.button.accept) {
        await jobRequest('delete');
      }
    } catch (error) {
      await showErrorMessage(
        'Encountered an error when deleting the job. Error:',
        error,
        [Dialog.okButton()]
      );
    }
  }
}
