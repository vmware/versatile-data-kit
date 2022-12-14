import React, { Component } from 'react';

export interface IVariables {
    /**
     * Variables label
     */
    label: string;
}


export default class VariablesDialong extends Component<IVariables> {
    /**
   * Returns a React component for rendering a variables menu.
   *
   * @param props - component properties
   * @returns React component
   */
    constructor(props: IVariables) {
        super(props);
    }
    /**
    * Renders a dialog asking for variables
    *
    * @returns React element
    */
    render(): React.ReactElement {
        return (
            <>
                <div className='jp-vdk-input-wrapper'>
                    <label className='jp-vdk-label' htmlFor="jobPath">Enter the needed {this.props.label} variables for the job:</label>
                    <input type="text" id="variablesInput" className='jp-vdk-input' onLoad={this._loadCurrentVariables} />
                    <button id="addVariable" onClick={this._addVariable}>Add</button>
                    <button id="seeVariables" onClick={this._loadCurrentVariables}>Show variables</button>
                </div>
                <ul id="vdkVariables" className='hidden'></ul>
            </>
        );
    }
     /**
   * Callback invoked upon clicking  Show variables
   *
   * @param event - event object
   */
      private _loadCurrentVariables = (event: any): void => {
        if (localStorage.getItem("env_variables")) {
            const str = localStorage.getItem("env_variables");
            let variablesArray = JSON.parse(str!);
            variablesArray.forEach((variable: string) => {
                this._appendElementToVariableList(variable);
            });
            document.getElementById("vdkVariables")?.classList.remove("hidden");
        }
        else{
            alert("No variables are set from Jupyter!");
        }
      }
    /**
   * Callback invoked upon clicking add 
   *
   * @param event - event object
   */
    private _addVariable = (event: any): void => {
        const inputEl = document.getElementById("variablesInput") as HTMLInputElement;
        this._appendElementToVariableList(inputEl.value);
        let variablesArray = [];
        if (localStorage.getItem("env_variables")) {
            variablesArray = JSON.parse(localStorage.getItem("env_variables")!);
        }
        variablesArray.push(inputEl.value);
        localStorage.setItem("env_variables", JSON.stringify(variablesArray));
        inputEl.value = "";
    };
    /**
    * Callback invoked upon pressing delete
    *
    * @param event - event object
    */
    private _removeVariable = (event: any): void => {
        let currButton = (event.currentTarget as HTMLInputElement);
        let innerText = currButton.parentElement?.getElementsByTagName("p") as any as Array<HTMLElement>;
        let variable = innerText[0].innerHTML;
        let variablesArray = JSON.parse(localStorage.getItem("env_variables")!);
        const index = variablesArray.indexOf(variable);
        if (index > -1) {
            variablesArray.splice(index, 1);
        }
        currButton.parentElement?.remove();
        localStorage.setItem("env_variables", JSON.stringify(variablesArray));
        console.log(variablesArray);
    }

    private _appendElementToVariableList(value: string) {
        let variablesUl = document.getElementById("vdkVariables");
        let item = document.createElement("li");
        item.classList.add("jp-vdk-variables-list-item");
        console.log("here");
        let variable = document.createElement("p");
        variable.innerHTML = value;

        let deleteButton = document.createElement("button");
        deleteButton.innerHTML = "X";
        deleteButton.classList.add("vdk-delete-variable-btn");
        deleteButton.onclick = this._removeVariable;

        item.appendChild(variable);
        item.appendChild(deleteButton);
        variablesUl?.appendChild(item);
        console.log(variablesUl);
    }
}