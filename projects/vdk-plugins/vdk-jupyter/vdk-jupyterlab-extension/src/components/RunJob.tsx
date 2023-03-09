import React, { Component } from 'react';
import { jobData } from '../jobData';
import { VdkOption } from '../vdkOptions/vdk_options';
import VDKTextInput from './VdkTextInput';
import { Dialog, showDialog } from '@jupyterlab/apputils';
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
                <VDKTextInput option={VdkOption.PATH} value={this.props.jobPath} label="Path to job directory:"></VDKTextInput>
                <div className='jp-vdk-input-wrapper'>
                    <label className='jp-vdk-label' htmlFor="vdkArguments">Arguments:</label>
                    <input type="text" className='jp-vdk-input' placeholder='{"key": "value"}' onChange={this._onArgsChange} />
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
        if(value && this._isJSON(value)){
            jobData.set(VdkOption.ARGUMENTS, value);
        }
    };

    private _isJSON = (str: string) => {
          try {
            JSON.parse(str)
            return true
          } catch(e){
            return false;
          }
      }
}

export async function showRunJobDialog(){
    const result = await showDialog({
      title: 'Run Job',
      body: (
        <RunJobDialog
          jobPath={sessionStorage.getItem('current-path')!}
        ></RunJobDialog>
      ),
      buttons: [Dialog.okButton(), Dialog.cancelButton()]
    });
    const resultButtonClicked = !result.value && result.button.accept;
    if (resultButtonClicked) {
      let response = await jobRunRequest();
      if(response[1]){
        alert(response[0]);
      }
    }
  }