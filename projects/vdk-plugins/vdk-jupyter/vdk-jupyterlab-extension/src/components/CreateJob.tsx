import React, { Component } from 'react';

export interface ICreateJobDialogProps {
    /**
     * Current Job path
     */
    jobPath: string;
    /**
     * Current Job name
     */
    jobName: string;
}


export default class CreateJobDialog extends Component<ICreateJobDialogProps> {
    /**
   * Returns a React component for rendering a create menu.
   *
   * @param props - component properties
   * @returns React component
   */
    constructor(props: ICreateJobDialogProps) {
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
                <div className='jp-vdk-create-options-wrapper'>
                    <div>
                        <input type="checkbox" name="Local" id="Local" className='jp-create-job-checkbox' onClick={this._onLocalClick()} />
                        <label className="checkboxLabel" htmlFor="Local">Local</label>
                    </div>
                    <div>
                        <input type="checkbox" name="Cloud" id="Cloud" className='jp-create-job-checkbox' onClick={this._onCloudClick()} />
                        <label className="checkboxLabel" htmlFor="Local">Cloud</label>
                    </div>
                </div>
                <div className='jp-vdk-input-wrapper'>
                    <label className='jp-vdk-label' htmlFor="jobName">Job Name:</label>
                    <input type="text" id="jobName" className='jp-vdk-input' placeholder={this.props.jobName} onChange={this._onNameChange} />
                </div>
                <div className='jp-vdk-input-wrapper'>
                    <label className='jp-vdk-label' htmlFor="jobTeam">Job Team:</label>
                    <input type="text" id="jobTeam" className='jp-vdk-input' placeholder="jobs" onChange={this._onTeamChange} />
                </div>
                <div className='jp-vdk-input-wrapper hidden'>
                    <label className='jp-vdk-label' htmlFor="jobPath">Path to parent directory:</label>
                    <input type="text" id="jobPath" className='jp-vdk-input' placeholder={this.props.jobPath} onChange={this._onPathChange} />
                </div>
                <div className='jp-vdk-input-wrapper hidden'>
                    <label className='jp-vdk-label' htmlFor="jobRestApiUrl">Rest Api URL:</label>
                    <input type="text" id="jobRestApiUrl" className='jp-vdk-input' placeholder="rest-api-url" onChange={this._onRestApiUrlChange} />
                </div>
            </>
        );
    }
    /**
   * Callback invoked upon choosing local checkbox
   */
    private _onLocalClick() {
        return (event: React.MouseEvent) => {
            this._handleCheckboxEvent("Local", "jobPath", "local")
        }
    }
    /**
  * Callback invoked upon choosing cloud checkbox
  */
    private _onCloudClick() {
        return (event: React.MouseEvent) => {
            this._handleCheckboxEvent("Cloud", "jobRestApiUrl", "cloud")
        }
    }
    /**
    * Helper method for checkbox click events which include removing/adding visibility of input element to the dialog
    */
   private _handleCheckboxEvent(checkboxId: string, inputId: string, createJobType: string){
    let checkbox = document.getElementById(checkboxId);
    let input = document.getElementById(inputId);
    if (checkbox?.classList.contains("checked")) {
        checkbox.classList.remove("checked");
        input?.parentElement?.classList.add("hidden");
        sessionStorage.removeItem(createJobType);
    }
    else {
        checkbox?.classList.add("checked");
        sessionStorage.setItem(createJobType, "1");
        input?.parentElement?.classList.remove("hidden");
    }
   }
    /**
   * Callback invoked upon changing the job name input.
   *
   * @param event - event object
   */
    private _onNameChange = (event: any): void => {
        const nameInput = event.currentTarget as HTMLInputElement;
        let value = nameInput.value;
        if (!value) {
            value = this.props.jobPath;
        }
        sessionStorage.setItem("create-job-name", value);
    };
    /**
   * Callback invoked upon changing the job team input.
   *
   * @param event - event object
   */
    private _onTeamChange = (event: any): void => {
        const teamInput = event.currentTarget as HTMLInputElement;
        let value = teamInput.value;
        if (!value) {
            value = "default-team";
        }
        sessionStorage.setItem("create-job-team", value);
    };
    /**
   * Callback invoked upon changing the job path input.
   *
   * @param event - event object
   */
    private _onPathChange = (event: any): void => {
        const pathInput = event.currentTarget as HTMLInputElement;
        let value = pathInput.value;
        if (!value) {
            value = this.props.jobPath;
        }
        sessionStorage.setItem("create-job-path", value);
    };
    /**
   * Callback invoked upon changing the job rest-api-url input.
   *
   * @param event - event object
   */
    private _onRestApiUrlChange = (event: any): void => {
        const urlInput = event.currentTarget as HTMLInputElement;
        let value = urlInput.value;
        if (!value) {
            value = "default-url";
        }
        sessionStorage.setItem("create-job-rest-api-url", value);
    };

}
