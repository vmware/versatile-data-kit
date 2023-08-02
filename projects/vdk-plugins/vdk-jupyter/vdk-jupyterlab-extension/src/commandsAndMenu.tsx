import { CommandRegistry } from '@lumino/commands';
import { Dialog, showDialog } from '@jupyterlab/apputils';
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
import React from 'react';
import { closeIcon } from '@jupyterlab/ui-components';

export var runningVdkOperation = '';

export function updateVDKMenu(commands: CommandRegistry, docManager: IDocumentManager, fileBrowser: FileBrowser, notebookTracker: INotebookTracker) {
  // Add Run job command
  add_command(commands, 'jp-vdk:menu-run', 'Run', 'Execute VDK Run Command', showRunJobDialog, docManager);

  // Add Create job command
  add_command(commands, 'jp-vdk:menu-create', 'Create', 'Execute VDK Create Command', showCreateJobDialog);

  // Add Download job command
  add_command(commands, 'jp-vdk:menu-download', 'Download', 'Execute VDK Download Command', showDownloadJobDialog);

  // Add Convert Job To Notebook command
  add_command(commands, 'jp-vdk:menu-convert-job-to-notebook', 'Convert Job To Notebook', 'Convert Data Job To Jupyter Notebook', showConvertJobToNotebookDialog, undefined,
    fileBrowser, notebookTracker);

  // Add Create Deployment command
  add_command(commands, 'jp-vdk:menu-create-deployment', 'Deploy', 'Create deployment of a VDK job', showCreateDeploymentDialog);
}


/**
 *@param schemaNaming - string representing the command in the schema in schema/plugin.json
 *@param label - the label that will be added in the Menu
 *@param caption - the caption for the command.
 *@param getOperationDialog - function that will load the dialog for the command
 */
function add_command(commands: CommandRegistry, schemaNaming: string, label: string, caption: string, getOperationDialog: Function,
  docManager?: IDocumentManager, fileBrowser?: FileBrowser, notebookTracker?: INotebookTracker) {
  commands.addCommand(schemaNaming, {
    label: label,
    caption: caption,
    execute: async () => {
      try {
        if (!runningVdkOperation) {
          runningVdkOperation = schemaNaming;
          jobData.set(VdkOption.PATH, workingDirectory);
          await jobdDataRequest();
          if (label == 'Convert Job To Notebook') await getOperationDialog(commands, fileBrowser, notebookTracker);
          else if (docManager) {
            await getOperationDialog(docManager);
          }
          else await getOperationDialog();
          setJobDataToDefault();
          runningVdkOperation = '';
        } else {
          await showDialog({
            title: 'Error',
            body: (
              <div className="vdk-error-dialog">
                <closeIcon.react className="vdk-error-icon" />
                <div>
                  <p>Another VDK operation is currently running!</p>
                  <p>Please wait until the operation ends!</p>
                </div>
              </div>
            ),
            buttons: [Dialog.okButton({ label: 'OK' })]
          });
        }
      } catch (error) {
        await showDialog({
          title: 'Error',
          body: (
            <div className="vdk-error-dialog">
              <closeIcon.react className="vdk-error-icon" color="red" />
              <div>
                <p>
                  Encountered an error when trying to open the dialog. Error:
                </p>
                <p>{error}</p>
              </div>
            </div>
          ),
          buttons: [Dialog.okButton({ label: 'OK'})]
        });
      }
    }
  });
}
