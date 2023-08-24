import { CommandRegistry } from '@lumino/commands';
import { showRunJobDialog } from './components/RunJob';
import { jobData, setJobDataToDefault } from './jobData';
import { showCreateDeploymentDialog } from './components/DeployJob';
import { showCreateJobDialog } from './components/CreateJob';
import { showDownloadJobDialog } from './components/DownloadJob';
import { showConvertJobToNotebookDialog } from './components/ConvertJobToNotebook';
import { jobdDataRequest } from './serverRequests';
import { VdkOption } from './vdkOptions/vdk_options';
import { workingDirectory } from '.';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { FileBrowser } from '@jupyterlab/filebrowser';
import { INotebookTracker } from '@jupyterlab/notebook';
import { StatusButton } from './components/StatusButton';
import {  ERROR_LABEL  } from './utils';
import { showErrorDialog } from './components/props';
import {showLogin2Dialog} from "./components/Login2";

export var runningVdkOperation = '';

export function updateVDKMenu(
  commands: CommandRegistry,
  docManager: IDocumentManager,
  fileBrowser: FileBrowser,
  notebookTracker: INotebookTracker,
  statusButton: StatusButton
) {

  commands.addCommand('jp-vdk:menu-login', {
    label: 'Login',
    caption: 'Execute VDK Login Command',
    execute: showLogin2Dialog });

  // Add Run job command
  add_command(
    commands,
    'jp-vdk:menu-run',
    'Run',
    'Execute VDK Run Command',
    showRunJobDialog,
    statusButton,
    docManager
  );

  // Add Create job command
  add_command(
    commands,
    'jp-vdk:menu-create',
    'Create',
    'Execute VDK Create Command',
    showCreateJobDialog,
    statusButton
  );

  // Add Download job command
  add_command(
    commands,
    'jp-vdk:menu-download',
    'Download',
    'Execute VDK Download Command',
    showDownloadJobDialog,
    statusButton
  );

  // Add Convert Job To Notebook command
  add_command(
    commands,
    'jp-vdk:menu-convert-job-to-notebook',
    'Convert Job To Notebook',
    'Convert Data Job To Jupyter Notebook',
    showConvertJobToNotebookDialog,
    statusButton,
    undefined,
    fileBrowser,
    notebookTracker
  );

  // Add Create Deployment command
  add_command(
    commands,
    'jp-vdk:menu-create-deployment',
    'Deploy',
    'Create deployment of a VDK job',
    showCreateDeploymentDialog,
    statusButton
  );
}

/**
 *@param schemaNaming - string representing the command in the schema in schema/plugin.json
 *@param label - the label that will be added in the Menu
 *@param caption - the caption for the command.
 *@param getOperationDialog - function that will load the dialog for the command
 */
function add_command(
  commands: CommandRegistry,
  schemaNaming: string,
  label: string,
  caption: string,
  getOperationDialog: Function,
  statusButton: StatusButton,
  docManager?: IDocumentManager,
  fileBrowser?: FileBrowser,
  notebookTracker?: INotebookTracker
) {
  commands.addCommand(schemaNaming, {
    label: label,
    caption: caption,
    execute: async () => {
      try {
        if (!runningVdkOperation) {
          runningVdkOperation = schemaNaming;
          jobData.set(VdkOption.PATH, workingDirectory);
          await jobdDataRequest();
          if (label === 'Convert Job To Notebook') {
            await getOperationDialog(
              commands,
              fileBrowser,
              notebookTracker,
              statusButton
            );
          } else if (docManager) {
            await getOperationDialog(docManager, statusButton);
          } else {
            await getOperationDialog(statusButton);
          }
          statusButton.hide();
          setJobDataToDefault();
          runningVdkOperation = '';
        } else {
          await showErrorDialog({
            title: ERROR_LABEL,
            messages: [
              'Another VDK operation is currently running!',
              'Please wait until the operation ends!'
            ]
          });
        }
      } catch (error) {
        await showErrorDialog({
          title: ERROR_LABEL,
          messages: [
            'Encountered an error when trying to open the dialog. Error:'
          ],
          error: error
        });
      }
    }
  });
}
