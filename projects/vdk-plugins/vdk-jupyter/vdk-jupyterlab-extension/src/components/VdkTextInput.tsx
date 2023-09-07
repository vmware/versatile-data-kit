import React, { Component, RefObject } from 'react';
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

    /**
     * Callback for when the width of the input is computed
     */
    onWidthComputed?: (width: number) => void;
}

export default class VDKTextInput extends Component<IVdkTextInputProps> {
    private inputRef: RefObject<HTMLInputElement> = React.createRef();

    /**
     * Initializes a new instance of the VDKTextInput component.
     *
     * @param props - component properties
     */
    constructor(props: IVdkTextInputProps) {
        super(props);
    }

    /**
     * Lifecycle method called after the component has mounted.
     */
    componentDidMount() {
        this.adjustInputWidth();
    }

    /**
     * Lifecycle method called after the component has updated.
     *
     * @param prevProps - previous component properties
     */
    componentDidUpdate(prevProps: IVdkTextInputProps): void {
        if (prevProps.value !== this.props.value) {
            this.adjustInputWidth();
        }
    }

    /**
     * Adjusts the input width based on its placeholder value.
     */
     adjustInputWidth(): void {
         const currentInput = this.inputRef.current;
         if (!currentInput) return;

         let maxWidth = 250;

         jobData.forEach((value) => {
             const tempSpan = document.createElement('span');
             tempSpan.innerHTML = value;

             const styles = ['fontFamily', 'fontSize', 'fontWeight', 'fontStyle', 'letterSpacing', 'textTransform'];
             styles.forEach(style => {
                 const computedStyle = currentInput ? window.getComputedStyle(currentInput).getPropertyValue(style) : '';
                 tempSpan.style[style as any] = computedStyle;
             });

             document.body.appendChild(tempSpan);
             const spanWidth = tempSpan.getBoundingClientRect().width;
             document.body.removeChild(tempSpan);
             const PADDING_WIDTH: number = 100;
             maxWidth = Math.max(maxWidth, spanWidth + PADDING_WIDTH);
         });

         currentInput.style.width = `${maxWidth}px`;
         this.props.onWidthComputed && this.props.onWidthComputed(maxWidth);
     }

    /**
     * Renders a div with input and value for VDK Option.
     *
     * @returns React element
     */
    render(): React.ReactElement {
        return (
            <div className="jp-vdk-input-wrapper">
                <label className="jp-vdk-label" htmlFor={this.props.option}>
                    {this.props.label}
                </label>
                <input
                    ref={this.inputRef}
                    type="text"
                    id={this.props.option}
                    className="jp-vdk-input"
                    placeholder={this.props.value}
                    onChange={this.onInputChange}
                />
            </div>
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
