import React, { Component } from 'react';
import { jobData } from '../jobData';
import { VdkOption } from '../vdkOptions/vdk_options';

export interface IDeployJobDialogProps {
    /**
     * Current Job name
     */
    jobName: string;
    /**
     * Current Team name
     */
    jobTeam: string;
    /**
    * Current Job path
    */
    jobPath: string;
}


export default class DeployJobDialog extends Component<IDeployJobDialogProps> {
    /**
   * Returns a React component for rendering a Deploy menu.
   *
   * @param props - component properties
   * @returns React component
   */
    constructor(props: IDeployJobDialogProps) {
        super(props);
    }
    /**
    * Renders a dialog for creating a new deployment of a Data Job.
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
                    <label className='jp-vdk-label' htmlFor="jobPath">Job Path:</label>
                    <input type="text" id="jobPath" className='jp-vdk-input' placeholder={this.props.jobPath} onChange={this.onPathChange} />
                </div>
                <div className='jp-vdk-input-wrapper'>
                    <label className='jp-vdk-label' htmlFor="jobRestApiUrl">Rest Api URL:</label>
                    <input type="text" id="jobRestApiUrl" className='jp-vdk-input' placeholder="rest-api-url" onChange={this.onRestApiUrlChange} />
                </div>
                <div className='jp-vdk-input-wrapper'>
                    <label className='jp-vdk-label' htmlFor="deploymentReason">Deployment reason:</label>
                    <input type="text" id="deploymentReason" className='jp-vdk-input' placeholder="reason" onChange={this.onDeploymentReasonChange} />
                </div>
                <div>
                    <input type="checkbox" name="enable" id="enable" className='jp-vdk-checkbox' onClick={this.onEnableClick()} />
                    <label className="checkboxLabel" htmlFor="enable">Enable</label>
                </div>
            </>
        );
    }
    /**
   * Callback invoked upon choosing Enable checkbox
   */
    private onEnableClick() {
        return (event: React.MouseEvent) => {
            let checkbox = document.getElementById("enable");
            if (checkbox?.classList.contains("checked")) {
                checkbox.classList.remove("checked");
                jobData.set(VdkOption.DEPLOY_ENABLE, "");
            }
            else {
                checkbox?.classList.add("checked");
                jobData.set(VdkOption.DEPLOY_ENABLE, "1");
            }
        }
    }
    /**
  * Callback invoked upon changing the job name input.
  *
  * @param event - event object
  */
    private onNameChange = (event: any): void => {
        this.populateJobData(VdkOption.NAME, event.currentTarget as HTMLInputElement);
    };
    /**
   * Callback invoked upon changing the job team input.
   *
   * @param event - event object
   */
    private onTeamChange = (event: any): void => {
        this.populateJobData(VdkOption.TEAM, event.currentTarget as HTMLInputElement);
    };
    /**
   * Callback invoked upon changing the job rest-api-url input.
   *
   * @param event - event object
   */
    private onRestApiUrlChange = (event: any): void => {
        this.populateJobData(VdkOption.REST_API_URL, event.currentTarget as HTMLInputElement);
    };
    /**
   * Callback invoked upon changing the job path input.
   *
   * @param event - event object
   */
    private onPathChange = (event: any): void => {
        this.populateJobData(VdkOption.PATH, event.currentTarget as HTMLInputElement);
    };
    /**
  * Callback invoked upon changing the deployent reason input.
  *
  * @param event - event object
  */
    private onDeploymentReasonChange = (event: any): void => {
        this.populateJobData(VdkOption.DEPLOYMENT_REASON, event.currentTarget as HTMLInputElement);
    };
    /**
  *  Helper function for populating jobData
  */
    private populateJobData(option: VdkOption, input: HTMLInputElement) {
        let value = input.value;
        if (!value) value = "";
        jobData.set(option, value);
    }
}
