import React, { Component } from 'react';
import { jobData } from '../jobData';
import { VdkOption } from '../vdkOptions/vdk_options';

export interface IVdkTextInputProps {
    /**
     * VdkOption to which the input is for
     */
    option: VdkOption;
    /**
     * Value corresponding to the VdkOption
     */
    value: string;
    /**
     * Label message for the input
     */
     label: string;
}


export default class VDKTextInput extends Component<IVdkTextInputProps> {
    /**
   * Returns a React component for rendering a download menu.
   *
   * @param props - component properties
   * @returns React component
   */
    constructor(props: IVdkTextInputProps) {
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
                    <label className='jp-vdk-label' htmlFor={this.props.option}>{this.props.label}</label>
                    <input type="text" id={this.props.option} className='jp-vdk-input' placeholder={this.props.value} onChange={this.onInputChange} />
                </div>
            </>
        );
    }
     /**
   * Callback invoked upon changing the input.
   *
   * @param event - event object
   */
      private onInputChange = (event: any): void => {
        const nameInput = event.currentTarget as HTMLInputElement;
        let value = nameInput.value;
        if(!value) value = this.props.value
        jobData.set(this.props.option, value);
    };
}
