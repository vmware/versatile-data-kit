import React, { Component } from 'react';
import { jobData } from '../jobData';
import { VdkOption } from '../vdkOptions/vdk_options';
import VDKTextInput from './VdkTextInput';
import { Dialog, showDialog } from '@jupyterlab/apputils';
import { jobTransformRequest } from '../serverRequests';
import { IJobPathProp } from './props';
import { VdkErrorMessage } from './VdkErrorMessage';

export default class TransformJobDialog extends Component<IJobPathProp> {
  /**
   * Returns a React component for rendering a transform menu.
   *
   * @param props - component properties
   * @returns React component
   */
  constructor(props: IJobPathProp) {
    super(props);
  }
  /**
   * Renders a dialog for transforming a data job.
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

export async function showTransformJobDialog() {
  const result = await showDialog({
    title: 'Transform Job',
    body: (
      <TransformJobDialog
        jobPath={jobData.get(VdkOption.PATH)!}
      ></TransformJobDialog>
    ),
    buttons: [Dialog.okButton(), Dialog.cancelButton()]
  });
  if (result.button.accept) {
    const confirmation = await showDialog({
      title: 'Transform Job',
      body: (
        <p>
          Are you sure you want to transform the Data Job with path:{' '}
          <i>{jobData.get(VdkOption.PATH)}</i>?
        </p>
      ),
      buttons: [Dialog.okButton(), Dialog.cancelButton()]
    });
    if (confirmation.button.accept) {
      let { message, status } = await jobTransformRequest();
      if (status) {
        showDialog({
          title: 'Transform Job',
          body: (
            <div className="vdk-transform-dialog-message-container">
              <p className="vdk-transform-dialog-message">
                The job was transformed successfully!
              </p>
            </div>
          ),
          buttons: [Dialog.okButton()]
        });
      } else {
        message = 'ERROR : ' + message;
        const errorMessage = new VdkErrorMessage(message);
        showDialog({
          title: 'Transform Job',
          body: (
            <div className="vdk-transform-error-message ">
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
