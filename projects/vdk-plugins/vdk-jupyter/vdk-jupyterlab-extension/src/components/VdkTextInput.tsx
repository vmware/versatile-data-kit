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


/**
   * This function is used to be sure that placeholder text is not overflowing in case of long path
   * if the string that is given is not path it will return the same string
   * if it is a path it will return the last directory
   */
const  getLastPartOfPath = (path: string): string => {
  const pathParts = path.split(/(?=[/\\])/); // Lookahead assertion to keep delimiter
  return pathParts[pathParts.length - 1];
}

export default class VDKTextInput extends Component<IVdkTextInputProps> {
  /**
   * Returns a React component for rendering a div with input and value  for VDK Option.
   *
   * @param props - component properties
   * @returns React component
   */
  constructor(props: IVdkTextInputProps) {
    super(props);
  }
  /**
   * Renders a div with input and value  for VDK Option.
   *
   * @returns React element
   */
  render(): React.ReactElement {
    return (
      <>
        <div className="jp-vdk-input-wrapper">
          <label className="jp-vdk-label" htmlFor={this.props.option}>
            {this.props.label}
          </label>
          <input
            type="text"
            id={this.props.option}
            className="jp-vdk-input"
            placeholder={getLastPartOfPath(this.props.value)}
            onChange={this.onInputChange}
          />
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
    if (!value) value = this.props.value;
    jobData.set(this.props.option, value);
  };
}
