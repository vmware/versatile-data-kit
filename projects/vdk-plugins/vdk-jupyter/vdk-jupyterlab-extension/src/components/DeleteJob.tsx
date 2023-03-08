import React, { Component } from 'react';
import { VdkOption } from '../vdkOptions/vdk_options';
import VDKTextInput from './VdkTextInput';

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
                <VDKTextInput option={VdkOption.NAME} value="default-name" label="Job Name:"></VDKTextInput>
                <VDKTextInput option={VdkOption.TEAM} value="default-team" label="Job Team:"></VDKTextInput>
                <VDKTextInput option={VdkOption.REST_API_URL} value="http://my_vdk_instance" label="Rest API URL:"></VDKTextInput>
            </>
        );
    }
}
