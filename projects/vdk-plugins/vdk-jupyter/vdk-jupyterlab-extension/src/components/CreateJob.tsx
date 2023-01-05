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
   * Returns a React component for rendering a run menu.
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
                    <input type="checkbox" name="Local" id="Local" className='jp-createJob-checkbox' onClick={this._onLocalClick} />
                    <label className="checkboxLabel" htmlFor="Local">Local</label>
                    <input type="checkbox" name="Cloud" id="Cloud" className='jp-createJob-checkbox' onClick={this._onCloudClick} />
                    <label className="checkboxLabel" htmlFor="Local">Cloud</label>
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
                    <label className='jp-vdk-label' htmlFor="jobRestApiUrl">Path to parent directory:</label>
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
            localStorage.setItem("local", "1");
            const pathInput = document.getElementById("jobPath")
            pathInput?.classList.remove("hidden")
        }
    }
     /**
   * Callback invoked upon choosing cloud checkbox
   */
    private _onCloudClick() {
        return (event: React.MouseEvent) => {
            localStorage.setItem("cloud", "1");
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
        sessionStorage.setItem("job-name", value)
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
        sessionStorage.setItem("team-name", value)
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
        sessionStorage.setItem("job-path", value)
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
        sessionStorage.setItem("job-rest-api-url", value)
    };

}
