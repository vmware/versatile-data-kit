import React, { Component } from 'react';
import { jobData } from '../dataClasses/jobData';

export interface IDownloadJobDialogProps {
    /**
     * Current Path
     */
     parentPath: string;
}

export default class DownloadJobDialog extends Component<IDownloadJobDialogProps> {
    /**
   * Returns a React component for rendering a download menu.
   *
   * @param props - component properties
   * @returns React component
   */
    constructor(props: IDownloadJobDialogProps) {
        super(props);
    }
    /**
    * Renders a dialog for downloading a data job.
    *
    * @returns React element
    */
    render(): React.ReactElement {
        return (
            <>
                 <div className='jp-vdk-input-wrapper'>
                    <label className='jp-vdk-label' htmlFor="jobName">Job Name:</label>
                    <input type="text" id="jobName" className='jp-vdk-input' placeholder="job-to-download" onChange={this.onNameChange} />
                </div>
                <div className='jp-vdk-input-wrapper'>
                    <label className='jp-vdk-label' htmlFor="jobTeam">Job Team:</label>
                    <input type="text" id="jobTeam" className='jp-vdk-input' placeholder="my-team" onChange={this.onTeamChange} />
                </div>
                <div className='jp-vdk-input-wrapper'>
                    <label className='jp-vdk-label' htmlFor="jobRestApiUrl">Rest Api URL:</label>
                    <input type="text" id="jobRestApiUrl" className='jp-vdk-input' placeholder="http://my_vdk_instance" onChange={this.onRestApiUrlChange} />
                </div>
                <div className='jp-vdk-input-wrapper'>
                    <label className='jp-vdk-label' htmlFor="jobPath">Path to parent directory where the job will be saved:</label>
                    <input type="text" id="jobPath" className='jp-vdk-input' placeholder={this.props.parentPath} onChange={this.onPathChange} />
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
            value = "default-job";
        }
        jobData.jobName = value;
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
        jobData.jobTeam = value;
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
        jobData.restApiUrl = value;
    };
     /**
   * Callback invoked upon changing the  job path input.
   *
   * @param event - event object
   */
      private onPathChange = (event: any): void => {
        const element = event.currentTarget as HTMLInputElement;
        let value = element.value;
        if(!value){
            value = this.props.parentPath;
        }
        jobData.jobPath = value;
    };
}
