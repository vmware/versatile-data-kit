import React, { Component } from 'react';
import RunJobData from '../utils';

export var runJobData = new RunJobData("", "");

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
                <div className='jp-vdk-input-wrapper'>
                    <label className='jp-vdk-label' htmlFor="jobPath">Path to parent directory:</label>
                    <input type="text" id="jobPath" className='jp-vdk-input' placeholder={this.props.jobPath} onChange={this._onPathChange} />
                </div>
                <div className='jp-vdk-input-wrapper'>
                    <label className='jp-vdk-label' htmlFor="vdkArguments">Arguments:</label>
                    <input type="text" className='jp-vdk-input' placeholder='{"key": "value"}' onChange={this._onArgsChange} />
                </div>
                <ul id="argumentsUl" className="hidden"></ul>
            </>
        );
    }
    /**
   * Callback invoked upon changing the  job path input.
   *
   * @param event - event object
   */
    private _onPathChange = (event: any): void => {
        const element = event.currentTarget as HTMLInputElement;
        let value = element.value;
        if(!value){
            value = this.props.jobPath;
        }
        runJobData.jobPath = value;
    };
    /**
    * Callback invoked upon  changing the args input
    *
    * @param event - event object
    */
     private _onArgsChange = (event: any): void => {
        const element = event.currentTarget as HTMLInputElement;
        let value = element.value;
        if(value && this._isJSON(value)){
            runJobData.jobArguments = value;
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
