import React, { Component } from 'react';
import { jobData } from '../jobData';
import { VdkOption } from '../vdkOptions/vdk_options';
import VDKTextInput from './VdkTextInput';

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
                <VDKTextInput option={VdkOption.NAME} value="default-name" label="Job Name:"></VDKTextInput>
                <VDKTextInput option={VdkOption.TEAM} value="default-team" label="Job Team:"></VDKTextInput>
                <VDKTextInput option={VdkOption.REST_API_URL} value="http://my_vdk_instance" label="Rest API URL:"></VDKTextInput>
                <VDKTextInput option={VdkOption.PATH} value={this.props.jobPath} label="Path to job directory:"></VDKTextInput>
                <VDKTextInput option={VdkOption.DEPLOYMENT_REASON} value="reason" label="Deployment reason:"></VDKTextInput>
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
}
