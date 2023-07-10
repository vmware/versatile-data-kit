import React, { Component } from 'react';
import { jobData } from '../jobData';
import { VdkOption } from '../vdkOptions/vdk_options';
import VDKTextInput from './VdkTextInput';
import { Dialog, showDialog, showErrorMessage } from '@jupyterlab/apputils';
import { getServerDirRequest, jobConvertToNotebookRequest } from '../serverRequests';
import { IJobPathProp } from './props';
import { VdkErrorMessage } from './VdkErrorMessage';
import { CONVERT_JOB_TO_NOTEBOOK_BUTTON_LABEL } from '../utils';
import { CommandRegistry } from '@lumino/commands';
import { FileBrowser } from '@jupyterlab/filebrowser';
import { INotebookTracker } from '@jupyterlab/notebook';
import { JupyterCellProps } from './props';

export default class ConvertJobToNotebookDialog extends Component<IJobPathProp> {
  /**
   * Returns a React component for rendering a convert menu.
   *
   * @param props - component properties
   * @returns React component
   */
  constructor(props: IJobPathProp) {
    super(props);
  }
  /**
   * Renders a dialog for converting a data job.
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
      </>
    );
  }
}

export async function showConvertJobToNotebookDialog(commands: CommandRegistry, fileBrowser: FileBrowser , notebookTracker: INotebookTracker) {
  const result = await showDialog({
    title: CONVERT_JOB_TO_NOTEBOOK_BUTTON_LABEL,
    body: (
      <ConvertJobToNotebookDialog
        jobPath={jobData.get(VdkOption.PATH)!}
      ></ConvertJobToNotebookDialog>
    ),
    buttons: [Dialog.okButton(), Dialog.cancelButton()]
  });
  if (result.button.accept) {
    const confirmation = await showDialog({
      title: CONVERT_JOB_TO_NOTEBOOK_BUTTON_LABEL,
      body: (
        <p>
          Are you sure you want to convert the Data Job with path:{' '}
          <i>{jobData.get(VdkOption.PATH)}</i> to notebook?
        </p>
      ),
      buttons: [Dialog.okButton(), Dialog.cancelButton()]
    });
    if (confirmation.button.accept) {
      let { message, status } = await jobConvertToNotebookRequest();
      if (status) {
        const transformjobResult = JSON.parse(message);
        const notebookContent = initializeNotebookContent(transformjobResult["code_structure"], transformjobResult["removed_files"])
        createTranformedNotebook(notebookContent, commands, fileBrowser, notebookTracker);
        await showDialog({
          title: CONVERT_JOB_TO_NOTEBOOK_BUTTON_LABEL,
          body: (
            <div className="vdk-convert-to-notebook-dialog-message-container">
              <p className="vdk-convert-to-notebook-dialog-message">
                The Data Job with path <i>{jobData.get(VdkOption.PATH)}</i> was
                converted to notebook successfully!
              </p>
            </div>
          ),
          buttons: [Dialog.okButton()]
        });
      } else {
        message = 'ERROR : ' + message;
        const errorMessage = new VdkErrorMessage(message);
        await showDialog({
          title: CONVERT_JOB_TO_NOTEBOOK_BUTTON_LABEL,
          body: (
            <div className="vdk-convert-to-notebook-error-message ">
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


const createTranformedNotebook = async (notebookContent: JupyterCellProps[], commands: CommandRegistry, fileBrowser: FileBrowser, notebookTracker: INotebookTracker) => {
  try {
    const baseDir = await getServerDirRequest();
    await fileBrowser.model.cd(jobData.get(VdkOption.PATH)!.substring(baseDir.length));  // relative path for Jupyter
    commands.execute('notebook:create-new');
    populateNotebook(notebookContent, notebookTracker)
  }
  catch (error) {
    await showErrorMessage(
      'Something went wrong while trying to create the new transformed notebook. Error:',
      error,
      [Dialog.okButton()]
    );
  }
}

const initializeNotebookContent = (codeStructure: string[], fileNames: string[]): JupyterCellProps[] => {
  let notebookContent: JupyterCellProps[] = [];

  for(let i = 0; i < codeStructure.length; i++) {
      notebookContent.push({
          source: "#### " + fileNames[i], // make names bolder
          type: 'markdown'
      });
      notebookContent.push({
          source: codeStructure[i],
          type: 'code'
      });
      if(codeStructure[i].includes('def run(job_input: IJobInput)')){
        notebookContent.push({
          source: 'run(job_input)',
          type: 'code'
      });
      }
  }
  return notebookContent;
}

const populateNotebook = async (notebookContent: JupyterCellProps[], notebookTracker: INotebookTracker) => {
  notebookTracker.activeCellChanged.connect((sender, args) => {
    const notebookPanel = notebookTracker.currentWidget;
    if (notebookPanel) {
      const cells = notebookPanel.content.model?.cells;

      // check if the notebook has only 1 empty cell, which is how we judge if it is a new notebook or not
      const cellContent = cells?.get(0).value.text;
      if (cells && cells.length === 1 && cellContent === '') {
        cells.clear(); // clear the initial empty cell

        const ipythonConfigCell =
        notebookPanel.content.model?.contentFactory?.createCodeCell({
          cell: {
            cell_type: 'code',
            source: [
              `"""\n`,
              `vdk_ipython extension introduces a magic command for Jupyter.\n`,
              `The command enables the user to load VDK for the current notebook.\n`,
              `VDK provides the job_input API, which has methods for:\n`,
              `    * executing queries to an OLAP database;\n`,
              `    * ingesting data into a database;\n`,
              `    * processing data into a database.\n`,
              `See the IJobInput documentation for more details.\n`,
              `https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/api/job_input.py\n`,
              `Please refrain from tagging this cell with VDK as it is not an actual part of the data job\n`,
              `and is only used for development purposes.\n`,
              `"""\n`,
              `%reload_ext vdk_ipython\n`,
              `%reload_VDK\n`,
              `job_input = VDK.get_initialized_job_input()`
            ],
            metadata: {}
          }
        });

        if(ipythonConfigCell) cells.push(ipythonConfigCell);

        for (let cellProps of notebookContent) {
          let newCell;

          if (cellProps.type === 'markdown') {
            newCell = notebookPanel.content.model?.contentFactory?.createMarkdownCell({
              cell: {
                cell_type: 'markdown',
                source: cellProps.source,
                metadata: {}
              }
            });
          } else if (cellProps.type === 'code') {
            newCell = notebookPanel.content.model?.contentFactory?.createCodeCell({
              cell: {
                cell_type: 'code',
                source: cellProps.source,
                metadata: {
                  "tags": [
                    "vdk"
                   ]
                }
              }
            });
          }

          if (newCell) {
            cells.push(newCell);
          }
        }
      }
    }
  });
}
