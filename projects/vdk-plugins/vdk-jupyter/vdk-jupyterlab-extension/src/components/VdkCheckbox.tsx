import React, { Component } from "react";

interface CheckboxProps {
    checked: boolean;
    onChange: (checked: boolean) => void;
    label: string;
    id: string;
}

export class VDKCheckbox extends Component<CheckboxProps> {
    render(): React.ReactElement {
        return (
            <div>
                <input
                    type="checkbox"
                    id={this.props.id}
                    className="jp-vdk-checkbox"
                    onChange={(e) => this.props.onChange(e.target.checked)}
                    defaultChecked={this.props.checked}
                />
                <label className="checkboxLabel" htmlFor={this.props.id}>
                    {this.props.label}
                </label>
            </div>
        );
    }
}
