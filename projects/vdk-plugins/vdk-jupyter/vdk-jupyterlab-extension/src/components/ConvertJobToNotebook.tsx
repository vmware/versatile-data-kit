import React, { Component } from 'react';
import { jobData } from '../jobData';
import { VdkOption } from '../vdkOptions/vdk_options';
import VDKTextInput from './VdkTextInput';
import { Dialog, showDialog } from '@jupyterlab/apputils';
import {
  getServerDirRequest,
  jobConvertToNotebookRequest
} from '../serverRequests';
import { VdkErrorMessage } from './VdkErrorMessage';
import { CONVERT_JOB_TO_NOTEBOOK_BUTTON_LABEL } from '../utils';
import { CommandRegistry } from '@lumino/commands';
import { FileBrowser } from '@jupyterlab/filebrowser';
import { INotebookTracker } from '@jupyterlab/notebook';
import { IJobPathProp, JupyterCellProps, showErrorDialog } from './props';
import { StatusButton } from './StatusButton';
import { checkIcon } from '@jupyterlab/ui-components';

export var notebookContent: JupyterCellProps[];

/**
 * A class responsible for the Transform Job operation
 * for more information check:
 * https://github.com/vmware/versatile-data-kit/wiki/VDK-Jupyter-Integration-Convert-Job-Operation
 */
export default class ConvertJobToNotebookDialog extends Component<
  IJobPathProp
> {
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

export async function showConvertJobToNotebookDialog(
  commands: CommandRegistry,
  fileBrowser: FileBrowser,
  notebookTracker: INotebookTracker,
  statusButton?: StatusButton
): Promise<void> {
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
      statusButton?.show('Convert', jobData.get(VdkOption.PATH)!);
      let { message, status } = await jobConvertToNotebookRequest();
      if (status) {
        const transformjobResult = JSON.parse(message);
        notebookContent = initializeNotebookContent(
          transformjobResult['code_structure'],
          transformjobResult['removed_files']
        );
        await createTranformedNotebook(commands, fileBrowser, notebookTracker);
        await showDialog({
          title: CONVERT_JOB_TO_NOTEBOOK_BUTTON_LABEL,
          body: (
            <div className="vdk-convert-to-notebook-dialog-message-container">
              <checkIcon.react className="vdk-dialog-check-icon" />
              <p className="vdk-convert-to-notebook-dialog-message">
                The Data Job with path <i>{jobData.get(VdkOption.PATH)}</i> was
                converted to notebook successfully!
              </p>
            </div>
          ),
          buttons: [Dialog.okButton()]
        });
      } else {
        if (message) {
          message = 'ERROR : ' + message;
          const errorMessage = new VdkErrorMessage(message);
          await showErrorDialog({
            title: CONVERT_JOB_TO_NOTEBOOK_BUTTON_LABEL,
            messages: [
              errorMessage.exception_message,
              errorMessage.what_happened,
              errorMessage.why_it_happened,
              errorMessage.consequences,
              errorMessage.countermeasures
            ]
          });
        }
      }
    }
  }
}

/**
 * Create a notebook for a transformed job.
 *
 * The function navigates to the job directory and creates a new notebook
 * file. The notebook is then populated with the content provided as parameter.
 *
 * @param {JupyterCellProps[]} notebookContent - The content to populate the notebook with.
 * @param {CommandRegistry} commands - The command registry to execute Jupyter commands.
 * @param {FileBrowser} fileBrowser - The file browser to navigate the file system.
 * @param {INotebookTracker} notebookTracker - The notebook tracker to track changes to the notebook.
 */
export const createTranformedNotebook = async (
  commands: CommandRegistry,
  fileBrowser: FileBrowser,
  notebookTracker: INotebookTracker
) => {
  try {
    const baseDir = await getServerDirRequest();
    jobData.set(
      VdkOption.NAME,
      jobData.get(VdkOption.PATH)!.split(/[\\/]/).pop() || ''
    ); //get the name of the job using the directory
    await fileBrowser.model.cd(
      jobData.get(VdkOption.PATH)!.substring(baseDir.length)
    ); // relative path for Jupyter
    commands.execute('notebook:create-new');
  } catch (error) {
    await showErrorDialog({
      title: CONVERT_JOB_TO_NOTEBOOK_BUTTON_LABEL,
      messages: [
        'Something went wrong while trying to create the new transformed notebook. Error:'
      ],
      error: error
    });
  }
};

/**
 * Initializes notebook content.
 *
 * The function takes code and filenames as parameters and generates a structured notebook content.
 * The code blocks are turned into notebook cells.
 *
 * @param {string[]} codeStructure - The code blocks to turn into notebook cells.
 * @param {string[]} fileNames - The names of the files to turn into titles.
 * @return {JupyterCellProps[]} - The structured content ready to be used to populate a notebook.
 */
export const initializeNotebookContent = (
  codeStructure: string[],
  fileNames: string[]
): JupyterCellProps[] => {
  const notebookContent: JupyterCellProps[] = [];

  for (let i = 0; i < codeStructure.length; i++) {
    notebookContent.push({
      source: '#### ' + fileNames[i], // make names bolder
      type: 'markdown'
    });
    notebookContent.push({
      source: codeStructure[i],
      type: 'code'
    });
    if (codeStructure[i].includes('def run(job_input: IJobInput)')) {
      notebookContent.push({
        source: 'run(job_input)',
        type: 'code'
      });
    }
  }
  return notebookContent;
};

/**
 * Populates notebook with provided content.
 *
 * The function takes notebook content and a notebook tracker as parameters.
 * When a new notebook becomes active, it is populated with the provided content.
 * @param {INotebookTracker} notebookTracker - The notebook tracker to track changes to the notebook.
 */
export const populateNotebook = async (notebookTracker: INotebookTracker) => {
  const notebookPanel = notebookTracker.currentWidget;
  if (notebookPanel) {
    const cells = notebookTracker.currentWidget?.content.model?.cells;
    const cellContent = cells?.get(0).value.text;
    // check if the notebook has only 1 empty cell, which is how we judge if it is a new notebook or not
    if (cells && cells.length <= 1 && cellContent == '') {
      cells.remove(1);

      const addMarkdownCell = (source: string[]) => {
        const markdownCell = notebookPanel.content.model?.contentFactory?.createMarkdownCell(
          {
            cell: {
              cell_type: 'markdown',
              source: source,
              metadata: {}
            }
          }
        );
        if (markdownCell) {
          cells.push(markdownCell);
        }
      };

      const addCodeCell = (source: string[], metadata: {}) => {
        const codeCell = notebookPanel.content.model?.contentFactory?.createCodeCell(
          {
            cell: {
              cell_type: 'code',
              source: source,
              metadata: metadata
            }
          }
        );
        if (codeCell) {
          cells.push(codeCell);
        }
      };
      addMarkdownCell(['# ' + jobData.get(VdkOption.NAME)]);

      addMarkdownCell([
        '### Please go through this guide before continuing with the data job run and development.'
      ]);

      addMarkdownCell([
        '#### Introduction and Preparations\n',
        '*  *This is a notebook transformed from a directory style data job located in ' +
          jobData.get(VdkOption.PATH) +
          '.*\n',
        '*  *If you are not familiar with notebook data jobs make sure to check the **Getting Started**(TODO: add link) page.*\n',
        '*  *You can find an archive of the **original job** at ' +
          jobData.get(VdkOption.PATH)!.split(/[/\\]/).slice(0, -1).join('/') +
          '.*'
      ]);

      addMarkdownCell([
        '#### What happened to my Data Job?\n',
        '\n',
        "<p> The Data Job's cells are automatically generated corresponding to VDK steps in the original files </p>\n",
        '\n',
        '<i>\n',
        '<details><summary>Click to learn more</summary> \n',
        '    <ul>\n',
        '        <li> The below cells are automatically generated corresponding to a step (.sql file or .py file with VDK run(job_input) function) in your original job.</li>\n',
        '        <li> When you see a title saying <b>"Step generated from: sample.py"</b> before some blocks of code, \n',
        '        it means that the code below that title was created from the "sample.py" file.</li>\n',
        '        <li> Similarly, if you come across code cells that have the format <b>"job_input.execute_query(query_string)"</b> ,\n',
        '        it means that those cells contain code generated from ".sql" files.</li>\n',
        '        <li> On the other hand, code cells originating from ".py" files remain unchanged.\n',
        '        However, an additional cell is included that calls the "run" function using the command <b>"run(job_input)"</b> . \n',
        '            This cell executes the "run" function from the code generated from the ".py" file.</li>\n',
        '        <li> ".py" files that are not considered a step - without VDK run(job_input) function - remain as files unchanged.</li>\n',
        '    </ul>\n',
        '</details>\n',
        '</i>'
      ]);

      addMarkdownCell([
        '#### What are those numbers with VDK Logo next to them?\n',
        '\n',
        '<p>They identify a <b>VDK cell</b>.<br/> <b>VDK cells</b> would be executed, in the specified order, when the data job is either deployed and subsequently executed with <b>VDK run</b>, or locally executed with <b>VDK run</b>.</p>\n',
        '<i>\n',
        '<details><summary>Click to learn more</summary>\n',
        '    <ul>\n',
        '        <li>You will notice that some cells are coloured and include the VDK logo and a numbering. \n',
        '            These are the "vdk" tagged cells. They have special meaning when using VDK run command.</li>\n',
        '        <li>You can mark a cell as <b>VDK cell</b> by setting the "vdk" tag on the cell. And removing it as a vdk cell step by removing the "vdk" tag.\n',
        '        <li>Only these cells are executed during VDK run command and all the others are ignored (for example the current cell). </li>\n',
        '        <li>The cells in the notebook will be executed according to the numbering when running the notebook data job with VDK Run. This means that the steps in the job are organized from the top to the bottom, starting with the first step.</li>\n',
        '        <li>You can delete the cells that are not tagged with "vdk" as they are not essential to the data job\'s execution.\n',
        '            However, removing tagged cells will result in a different data job run.</li>\n',
        '    </ul> \n',
        '</details>\n',
        '</i>\n',
        '<br/>'
      ]);

      addCodeCell(
        [
          '"""\n',
          'vdk.plugin.ipython extension introduces a magic command for Jupyter.\n',
          'The command enables the user to load VDK for the current notebook.\n',
          'VDK provides the job_input API, which has methods for:\n',
          '    * executing queries to an OLAP database;\n',
          '    * ingesting data into a database;\n',
          '    * processing data into a database.\n',
          'See the IJobInput documentation for more details.\n',
          'https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/api/job_input.py\n',
          'Please refrain from tagging this cell with VDK as it is not an actual part of the data job\n',
          'and is only used for development purposes.\n',
          '"""\n',
          '%reload_ext vdk.plugin.ipython\n',
          '%reload_VDK\n',
          'job_input = VDK.get_initialized_job_input()'
        ],
        {}
      );

      // add code that came from the previous version of the job and the names of the files where they came from
      for (const cellProps of notebookContent) {
        if (cellProps.type === 'markdown') {
          addMarkdownCell([cellProps.source]);
        } else if (cellProps.type === 'code') {
          addCodeCell([cellProps.source], {
            tags: ['vdk']
          });
        }
      }

      notebookContent = [];
    }
  }
};
