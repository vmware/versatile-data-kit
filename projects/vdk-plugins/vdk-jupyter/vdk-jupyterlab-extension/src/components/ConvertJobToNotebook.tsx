import React, { Component } from 'react';
import { jobData } from '../jobData';
import { VdkOption } from '../vdkOptions/vdk_options';
import VDKTextInput from './VdkTextInput';
import { Dialog, showDialog } from '@jupyterlab/apputils';
import { jobConvertToNotebookRequest } from '../serverRequests';
import { IJobPathProp } from './props';
import { VdkErrorMessage } from './VdkErrorMessage';
import { CONVERT_JOB_TO_NOTEBOOK_BUTTON_LABEL } from '../utils';

export default class ConvertJobToNotebookDialog extends Component<IJobPathProp> {
  /**
   * Returns a React component for rendering a convert menu.
   *
   * @param props - component properties
   * @returns React component
   */
  constructor(props: IJobPathProp) {
    super(props);
  }
  /**
   * Renders a dialog for converting a data job.
   *
   * @returns React element
   */
  render(): React.ReactElement {
    return (
      <>
        <VDKTextInput
          option={VdkOption.PATH}
          value={this.props.jobPath}
          label="Path to job directory:"
        ></VDKTextInput>
      </>
    );
  }
}

export async function showConvertJobToNotebookDialog() {
  const result = await showDialog({
    title: CONVERT_JOB_TO_NOTEBOOK_BUTTON_LABEL,
    body: (
      <ConvertJobToNotebookDialog
        jobPath={jobData.get(VdkOption.PATH)!}
      ></ConvertJobToNotebookDialog>
    ),
    buttons: [Dialog.okButton(), Dialog.cancelButton()]
  });
  if (result.button.accept) {
    const confirmation = await showDialog({
      title: CONVERT_JOB_TO_NOTEBOOK_BUTTON_LABEL,
      body: (
        <p>
          Are you sure you want to convert the Data Job with path:{' '}
          <i>{jobData.get(VdkOption.PATH)}</i> to notebook?
        </p>
      ),
      buttons: [Dialog.okButton(), Dialog.cancelButton()]
    });
    if (confirmation.button.accept) {
      let { message, status } = await jobConvertToNotebookRequest();
      if (status) {
        await showDialog({
          title: CONVERT_JOB_TO_NOTEBOOK_BUTTON_LABEL,
          body: (
            <div className="vdk-convert-to-notebook-dialog-message-container">
              <p className="vdk-convert-to-notebook-dialog-message">
                The Data Job with path <i>{jobData.get(VdkOption.PATH)}</i> was
                converted to notebook successfully!
              </p>
            </div>
          ),
          buttons: [Dialog.okButton()]
        });
      } else {
        message = 'ERROR : ' + message;
        const errorMessage = new VdkErrorMessage(message);
        await showDialog({
          title: CONVERT_JOB_TO_NOTEBOOK_BUTTON_LABEL,
          body: (
            <div className="vdk-convert-to-notebook-error-message ">
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
    }
  }
}
