import React, { Component } from 'react';
import { jobData } from '../jobData';
import { VdkOption } from '../vdkOptions/vdk_options';
import VDKTextInput from './VdkTextInput';
import { Dialog, showDialog } from '@jupyterlab/apputils';
import { getNotebookInfo, jobRunRequest } from '../serverRequests';
import { IJobPathProp } from './props';
import { VdkErrorMessage } from './VdkErrorMessage';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { RUN_FAILED_BUTTON_LABEL, RUN_JOB_BUTTON_LABEL } from '../utils';

export default class RunJobDialog extends Component<IJobPathProp> {
  /**
   * Returns a React component for rendering a run menu.
   *
   * @param props - component properties
   * @returns React component
   */

  constructor(props: IJobPathProp) {
    super(props);
  }
  /**
   * Renders a dialog for running a data job.
   *
   * @returns React element
   */
  render(): React.ReactElement {
    return (
      <>
        <VDKTextInput
          option={VdkOption.PATH}
          value={this.props.jobPath}
          label="Path to job directory:"
        ></VDKTextInput>
        <div className="jp-vdk-input-wrapper">
          <label className="jp-vdk-label" htmlFor="arguments">
            Arguments:
          </label>
          <input
            type="text"
            id="arguments"
            className="jp-vdk-input"
            placeholder='{"key": "value"}'
            onChange={this._onArgsChange}
          />
        </div>
        <ul id="argumentsUl" className="hidden"></ul>
      </>
    );
  }
  /**
   * Callback invoked upon  changing the args input
   *
   * @param event - event object
   */
  private _onArgsChange = (event: any): void => {
    const element = event.currentTarget as HTMLInputElement;
    let value = element.value;
    if (value && this._isJSON(value)) {
      jobData.set(VdkOption.ARGUMENTS, value);
    }
  };

  private _isJSON = (str: string) => {
    try {
      JSON.parse(str);
      return true;
    } catch (e) {
      return false;
    }
  };
}

export async function showRunJobDialog(docManager?: IDocumentManager) {
  const result = await showDialog({
    title: RUN_JOB_BUTTON_LABEL,
    body: <RunJobDialog jobPath={jobData.get(VdkOption.PATH)!}></RunJobDialog>,
    buttons: [Dialog.okButton(), Dialog.cancelButton()]
  });
  if (result.button.accept) {
    let { message, status } = await jobRunRequest();
    if (status) {
      showDialog({
        title: RUN_JOB_BUTTON_LABEL,
        body: (
          <div className="vdk-run-dialog-message-container">
            <p className="vdk-run-dialog-message">
              The job was executed successfully!
            </p>
          </div>
        ),
        buttons: [Dialog.okButton()]
      });
    } else {
      message = 'ERROR : ' + message;
      const errorMessage = new VdkErrorMessage(message);
      if (
        !docManager ||
        !(await handleErrorsProducedByNotebookCell(errorMessage, docManager))
      ) {
        showDialog({
          title: RUN_JOB_BUTTON_LABEL,
          body: (
            <div className="vdk-run-error-message ">
              <p>{errorMessage.exception_message}</p>
              <p>{errorMessage.what_happened}</p>
              <p>{errorMessage.why_it_happened}</p>
              <p>{errorMessage.consequences}</p>
              <p>{errorMessage.countermeasures}</p>
            </div>
          ),
          buttons: [Dialog.okButton()]
        });
      }
    }
  }
}

export const findFailingCellId = (message: String): string => {
  const regex = /cell_id:([0-9a-fA-F-]+)/;
  const match = message.match(regex);
  if (match) return match[1];
  return '';
};

/**
 * Returns a Element that is used for numarating cell executions on Jupyter (text with [] if not executed and  with [1], [2] if executed)
 * @param failingCell - parent cell of that element
 * @returns Element or undefined if the element could not be found
 */
export const getCellInputAreaPromp = (
  failinCell: Element
): Element | undefined => {
  const cellInputWrappers = failinCell.getElementsByClassName(
    'jp-Cell-inputWrapper'
  );
  for (let i = 0; i < cellInputWrappers.length; i++) {
    const cellAreas =
      cellInputWrappers[i].getElementsByClassName('jp-Cell-inputArea');
    if (cellAreas.length > 0) {
      const cellInputArea = cellAreas[0];
      const promptElements = cellInputArea.getElementsByClassName(
        'jp-InputArea-prompt'
      );
      if (promptElements.length > 0) {
        return promptElements[0];
      }
    }
  }
};

const switchToFailingCell = (failingCell: Element) => {
  const prompt = getCellInputAreaPromp(failingCell);
  prompt?.classList.add('jp-vdk-failing-cell-prompt');
  failingCell.scrollIntoView();
  failingCell.classList.add('jp-vdk-failing-cell');
  // Delete previous fail numbering
  const vdkFailingCellNums = Array.from(
    document.getElementsByClassName('jp-vdk-failing-cell-num')
  );
  vdkFailingCellNums.forEach(element => {
    element.classList.remove('jp-vdk-failing-cell-num');
    element.classList.add('jp-vdk-cell-num');
  });
};

const unmarkOldFailingCells = (cell: Element) => {
  cell.classList.remove('jp-vdk-failing-cell');
  const cellPropt = getCellInputAreaPromp(cell);
  cellPropt?.classList.remove('jp-vdk-failing-cell-prompt');
};

export const findFailingCellInNotebookCells = async (
  element: Element,
  failingCellIndex: Number,
  nbPath: string
) => {
  const cells = element.children;
  if (failingCellIndex > cells.length) {
    showDialog({
      title: RUN_FAILED_BUTTON_LABEL,
      body: (
        <div>
          <p>
            Sorry, something went wrong while trying to find the failing cell!
          </p>
          <p>
            Please, check the {nbPath} once more and try to run the job while
            the notebook is active!
          </p>
        </div>
      ),
      buttons: [Dialog.cancelButton()]
    });
  } else {
    for (let i = 0; i < cells.length; i++) {
      i === failingCellIndex
        ? switchToFailingCell(cells[i])
        : unmarkOldFailingCells(cells[i]);
    }
  }
};

/**
 * Seperate handling for notebook errors - option for the user to navigate to the failing cell when error is produced
 */
export const handleErrorsProducedByNotebookCell = async (
  message: VdkErrorMessage,
  docManager: IDocumentManager
): Promise<boolean> => {
  const failingCellId = findFailingCellId(message.what_happened);
  if (failingCellId) {
    const { path: nbPath, cellIndex: failingCellIndex } = await getNotebookInfo(
      failingCellId
    );
    if (nbPath) {
      const navigateToFailingCell = async () => {
        const notebook = docManager.openOrReveal(nbPath);
        if (notebook) {
          await notebook.revealed; // wait until the DOM elements are fully loaded
          const children = Array.from(notebook.node.children!);
          if (children) {
            children.forEach(async element => {
              if (element.classList.contains('jp-Notebook')) {
                findFailingCellInNotebookCells(
                  element,
                  Number(failingCellIndex),
                  nbPath
                );
              }
            });
          }
        }
      };

      const result = await showDialog({
        title: RUN_JOB_BUTTON_LABEL,
        body: (
          <div className="vdk-run-error-message ">
            <p>{message.exception_message}</p>
            <p>{message.what_happened}</p>
            <p>{message.why_it_happened}</p>
            <p>{message.consequences}</p>
            <p>{message.countermeasures}</p>
          </div>
        ),
        buttons: [
          Dialog.okButton({ label: 'See failing cell' }),
          Dialog.cancelButton()
        ]
      });

      if (result.button.accept) {
        navigateToFailingCell();
      }

      return true;
    }
  }

  return false;
};
