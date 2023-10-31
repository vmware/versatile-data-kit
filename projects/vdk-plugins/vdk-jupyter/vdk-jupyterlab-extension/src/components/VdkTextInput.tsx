import React, { Component, RefObject } from 'react';
import { jobData } from '../jobData';
import { VdkOption } from '../vdkOptions/vdk_options';
import { FaQuestionCircle } from 'react-icons/fa';

export interface IVdkTextInputProps {
  /**
   * Represents the VdkOption for which the input is created.
   */
  option: VdkOption;
  /**
   * The default value corresponding to the VdkOption.
   */
  value: string;
  /**
   * The display label for the input.
   */
  label: string;
  /**
   * Callback function that is invoked when the width of the input is computed.
   */
  onWidthComputed?: (width: number) => void;
  /**
   * Optional tooltip content.
   */
  tooltip?: string;
  /**
   * Custom change handler if provided
   */
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

interface IVdkInputState {
  /**
   * Represents the computed or default width for the input.
   */
  inputWidth: number;
}

/**
 * The default width used for the input field.
 */
const DEFAULT_INPUT_WIDTH = 250;

export default class VDKTextInput extends Component<IVdkTextInputProps> {
  /**
   * Component's state.
   */
  state: IVdkInputState = {
    inputWidth: DEFAULT_INPUT_WIDTH
  };

  /**
   * Reference to the input element.
   */
  private inputRef: RefObject<HTMLInputElement> = React.createRef();

  /**
   * Lifecycle method called after the component has mounted. It adjusts the input width based on the content.
   */
  componentDidMount(): void {
    this.adjustInputWidth();
  }

  /**
   * Lifecycle method called after the component updates. It adjusts the input width if the value prop has changed.
   *
   * @param prevProps - The previous properties before the component updated.
   */
  componentDidUpdate(prevProps: IVdkTextInputProps): void {
    if (prevProps.value !== this.props.value) {
      this.adjustInputWidth();
    }
  }

  /**
   * Adjusts the width of the input field based on the content from jobData.
   *
   * Utilizes a temporary HTML span element, styled like the input, to determine
   * the width required to display each value in jobData without clipping.
   * After iterating through all values, the component state's inputWidth is
   * updated with the computed maximum width.
   */
  adjustInputWidth(): void {
    const currentInput = this.inputRef.current;
    if (!currentInput) {
      return;
    }

    let maxWidth = DEFAULT_INPUT_WIDTH;

    const tempSpan = document.createElement('span');
    const styles = [
      'fontFamily',
      'fontSize',
      'fontWeight',
      'fontStyle',
      'letterSpacing',
      'textTransform'
    ];
    styles.forEach(style => {
      const computedStyle = currentInput
        ? window.getComputedStyle(currentInput).getPropertyValue(style)
        : '';
      tempSpan.style[style as any] = computedStyle;
    });

    const PADDING_WIDTH = 100;
    jobData.forEach(value => {
      tempSpan.innerHTML = value;
      document.body.appendChild(tempSpan);
      const spanWidth = tempSpan.getBoundingClientRect().width + PADDING_WIDTH;
      document.body.removeChild(tempSpan);
      maxWidth = Math.max(maxWidth, spanWidth);
    });

    this.setState({ inputWidth: maxWidth });
  }

  /**
   * Renders a div containing a label and an input field.
   *
   * @returns A React element representing the input component.
   */
  render(): React.ReactElement {
    return (
      <div className="jp-vdk-input-wrapper">
        <label className="jp-vdk-label" htmlFor={this.props.option}>
          {this.props.label}
          {this.props.tooltip && (
            <span className="tooltip">
              <FaQuestionCircle className="icon-tooltip" />
              <span className="tooltiptext">{this.props.tooltip}</span>
            </span>
          )}
        </label>
        <input
          ref={this.inputRef}
          type="text"
          id={this.props.option}
          className="jp-vdk-input"
          placeholder={this.props.value}
          style={{ width: `${this.state.inputWidth}px` }}
          onChange={this.onInputChange}
        />
      </div>
    );
  }

  /**
   * Callback function invoked when the input value changes. It updates the jobData with the new value.
   *
   * @param event - The event object containing details about the change event.
   */
  private onInputChange = (event: any): void => {
    if (this.props.onChange) {
      this.props.onChange(event);
    }

    const nameInput = event.currentTarget as HTMLInputElement;
    let value = nameInput.value;
    if (!value) {
      value = this.props.value;
    }
    jobData.set(this.props.option, value);
  };
}
