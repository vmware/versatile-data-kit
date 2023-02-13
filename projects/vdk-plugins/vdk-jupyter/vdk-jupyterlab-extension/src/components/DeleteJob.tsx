import React, { Component } from 'react';
import DeleteJobData from '../dataClasses/deleteJobData';

export var deleteJobData = new DeleteJobData("", "", "")

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
                 <div className='jp-vdk-input-wrapper'>
                    <label className='jp-vdk-label' htmlFor="jobName">Job Name:</label>
                    <input type="text" id="jobName" className='jp-vdk-input' placeholder={this.props.jobName} onChange={this.onNameChange} />
                </div>
                <div className='jp-vdk-input-wrapper'>
                    <label className='jp-vdk-label' htmlFor="jobTeam">Job Team:</label>
                    <input type="text" id="jobTeam" className='jp-vdk-input' placeholder={this.props.jobTeam} onChange={this.onTeamChange} />
                </div>
                <div className='jp-vdk-input-wrapper'>
                    <label className='jp-vdk-label' htmlFor="jobRestApiUrl">Rest Api URL:</label>
                    <input type="text" id="jobRestApiUrl" className='jp-vdk-input' placeholder="rest-api-url" onChange={this.onRestApiUrlChange} />
                </div>
            </>
        );
    }
     /**
   * Callback invoked upon changing the job name input.
   *
   * @param event - event object
   */
      private onNameChange = (event: any): void => {
        const nameInput = event.currentTarget as HTMLInputElement;
        let value = nameInput.value;
        if (!value) {
            value = this.props.jobName;
        }
        deleteJobData.jobName = value;
    };
    /**
   * Callback invoked upon changing the job team input.
   *
   * @param event - event object
   */
    private onTeamChange = (event: any): void => {
        const teamInput = event.currentTarget as HTMLInputElement;
        let value = teamInput.value;
        if (!value) {
            value = "default-team";
        }
        deleteJobData.jobTeam = value;
    };
    /**
   * Callback invoked upon changing the job rest-api-url input.
   *
   * @param event - event object
   */
    private onRestApiUrlChange = (event: any): void => {
        const urlInput = event.currentTarget as HTMLInputElement;
        let value = urlInput.value;
        if (!value) {
            value = "default-url";
        }
        deleteJobData.restApiUrl = value;
    };
}
