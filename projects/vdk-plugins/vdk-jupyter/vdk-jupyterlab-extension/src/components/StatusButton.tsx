import { showDialog, Dialog } from '@jupyterlab/apputils'; // Import the necessary showDialog and Dialog
import { checkIcon } from '@jupyterlab/ui-components'; // Import the Jupyter icon
import React from 'react';
import { CHECK_STATUS_BUTTON_LABEL } from '../utils';
import { MainMenu } from '@jupyterlab/mainmenu';
import { CommandRegistry } from '@lumino/commands';

let statusButton: HTMLButtonElement | null = null;

export async function showCheckStatusButton(commands: CommandRegistry) {
  console.log('showCheckStatusButton called');
  if (!statusButton) {
    statusButton = document.createElement('button');
    statusButton.innerHTML = CHECK_STATUS_BUTTON_LABEL;
    statusButton.id = 'check-status-button';
    statusButton.className = 'jp-vdk-check-status-button';
    statusButton.onclick = async () => {
      await showDialog({
        title: CHECK_STATUS_BUTTON_LABEL,
        body: (
          <div className="vdk-run-dialog-message-container">
            <div className="jp-vdk-check-status-icon">{checkIcon}</div>
            <p className="vdk-run-dialog-message">
              Operation is currently running!
            </p>
          </div>
        ),
        buttons: [Dialog.okButton()]
      });
    };
    const menuItem = new MainMenu(commands);
    console.log('menuItem', menuItem);
    menuItem.node.children[0].appendChild(statusButton);
  }
}

export function hideCheckStatusButton() {
  console.log('hideCheckStatusButton called');
  // if (statusButton) {
  //   statusButton.remove();
  //   statusButton = null;
  // }
}
