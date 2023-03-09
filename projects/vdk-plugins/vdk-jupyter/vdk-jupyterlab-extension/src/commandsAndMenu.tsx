import { CommandRegistry } from '@lumino/commands';
import { Dialog, showErrorMessage } from '@jupyterlab/apputils';
import { showRunJobDialog } from './components/RunJob';
import { setJobDataToDefault } from './jobData';
import { showCreateDeploymentDialog } from './components/DeployJob';
import { showCreateJobDialog } from './components/CreateJob';
import { showDownloadJobDialog } from './components/DownloadJob';
import { showDeleteJobDialog } from './components/DeleteJob';

var runningVdkOperation = false;

export function updateVDKMenu(commands: CommandRegistry) {
  // Add Run job command
  add_command(commands, 'jp-vdk:menu-run','Run','Execute VDK Run Command', showRunJobDialog);


  // Add Create job command
  add_command(commands, 'jp-vdk:menu-create','Create','Execute VDK Create Command', showCreateJobDialog);


  // Add Delete job command
  add_command(commands, 'jp-vdk:menu-delete','Delete','Execute VDK Delete Command', showDeleteJobDialog);
  

  // Add Download job command
  add_command(commands, 'jp-vdk:menu-download','Download','Execute VDK Download Command', showDownloadJobDialog);

  // Add Create Deployment command
  add_command(commands, 'jp-vdk:menu-create-deployment','Deploy','Create deployment of a VDK job', showCreateDeploymentDialog);
}


function add_command(commands: CommandRegistry, schemaNaming: string, label: string, caption: string, getOperationDialog: Function){
  commands.addCommand(schemaNaming, {
    label: label,
    caption: caption,
    execute: async () => {
      try {
        if (!runningVdkOperation) {
          runningVdkOperation = true;
          await getOperationDialog();
          setJobDataToDefault();
          runningVdkOperation = false;
        } else {
          showErrorMessage(
            'Another VDK operation is currently running!',
            'Please wait until the operation ends!',
            [Dialog.okButton()]
          );
        }
      } catch (error) {
        await showErrorMessage(
          'Encountered an error when trying to open the dialog. Error:',
          error,
          [Dialog.okButton()]
        );
      }
    }
  });
}