import React, { Component } from 'react';
import { jobData } from '../jobData';
import { VdkOption } from '../vdkOptions/vdk_options';
import VDKTextInput from './VdkTextInput';
import { Dialog, showDialog, showErrorMessage } from '@jupyterlab/apputils';
import { jobRunRequest } from '../serverRequests';

export interface IRunJobDialogProps {
  /**
   * Current Job path
   */
  jobPath: string;
}

export default class RunJobDialog extends Component<IRunJobDialogProps> {
  /**
   * Returns a React component for rendering a run menu.
   *
   * @param props - component properties
   * @returns React component
   */

  constructor(props: IRunJobDialogProps) {
    super(props);
  }
  /**
   * Renders a dialog for running a data job.
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
        <div className="jp-vdk-input-wrapper">
          <label className="jp-vdk-label" htmlFor="arguments">
            Arguments:
          </label>
          <input
            type="text"
            id="arguments"
            className="jp-vdk-input"
            placeholder='{"key": "value"}'
            onChange={this._onArgsChange}
          />
        </div>
        <ul id="argumentsUl" className="hidden"></ul>
      </>
    );
  }
  /**
   * Callback invoked upon  changing the args input
   *
   * @param event - event object
   */
  private _onArgsChange = (event: any): void => {
    const element = event.currentTarget as HTMLInputElement;
    let value = element.value;
    if (value && this._isJSON(value)) {
      jobData.set(VdkOption.ARGUMENTS, value);
    }
  };

  private _isJSON = (str: string) => {
    try {
      JSON.parse(str);
      return true;
    } catch (e) {
      return false;
    }
  };
}

export async function showRunJobDialog() {
  const result = await showDialog({
    title: 'Run Job',
    body: (
      <RunJobDialog
        jobPath={sessionStorage.getItem('current-path')!}
      ></RunJobDialog>
    ),
    buttons: [Dialog.okButton(), Dialog.cancelButton()]
  });
  if (result.button.accept) {
    let { message, status } = await jobRunRequest();
        if (status) {
          alert(message)
        }
        else{
          showErrorMessage(
            'Encauntered an error while running the job!',
            message,
            [Dialog.okButton()]
          );
        }
  }
}
