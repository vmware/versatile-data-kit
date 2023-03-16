import React, { Component } from 'react';
import { VdkOption } from '../vdkOptions/vdk_options';
import VDKTextInput from './VdkTextInput';
import { Dialog, showDialog, showErrorMessage } from '@jupyterlab/apputils';
import { jobData } from '../jobData';
import { jobRequest } from '../serverRequests';

export interface IDeleteJobDialogProps {
  /**
   * Current Job name
   */
  jobName: string;
  /**
   * Current Team name
   */
  jobTeam: string;
}

export default class DeleteJobDialog extends Component<IDeleteJobDialogProps> {
  /**
   * Returns a React component for rendering a delete menu.
   *
   * @param props - component properties
   * @returns React component
   */
  constructor(props: IDeleteJobDialogProps) {
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
          value="default-name"
          label="Job Name:"
        ></VDKTextInput>
        <VDKTextInput
          option={VdkOption.TEAM}
          value="default-team"
          label="Job Team:"
        ></VDKTextInput>
        <VDKTextInput
          option={VdkOption.REST_API_URL}
          value="http://my_vdk_instance"
          label="Rest API URL:"
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
        jobName="job-to-delete"
        jobTeam="default-team"
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
          ' from ' +
          jobData.get(VdkOption.REST_API_URL) +
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
