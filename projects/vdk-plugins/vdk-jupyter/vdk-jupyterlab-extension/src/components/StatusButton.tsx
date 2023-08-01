import { CommandRegistry } from '@lumino/commands';
import {
  CHECK_STATUS_BUTTON_COMMAND_ID,
  CHECK_STATUS_BUTTON_ID,
  CHECK_STATUS_BUTTON_CLASS,
  CHECK_STATUS_BUTTON_LABEL
} from '../utils';
import { Dialog, showDialog } from '@jupyterlab/apputils';
import React from 'react';
import { checkIcon } from '@jupyterlab/ui-components';

export class StatusButton {
  private readonly buttonElement: HTMLButtonElement;

  constructor(commands: CommandRegistry) {
    this.buttonElement = document.createElement('button');
    this.buttonElement.innerHTML = CHECK_STATUS_BUTTON_LABEL;
    this.buttonElement.id = CHECK_STATUS_BUTTON_ID;
    this.buttonElement.className = CHECK_STATUS_BUTTON_CLASS;

    this.buttonElement.onclick = () => {
      commands.execute(CHECK_STATUS_BUTTON_COMMAND_ID);
    };

    this.buttonElement.style.display = 'none';
  }

  get element(): HTMLButtonElement {
    return this.buttonElement;
  }

  show(): void {
    this.buttonElement.style.display = '';
  }

  hide(): void {
    this.buttonElement.style.display = 'none';
  }
}

export function createStatusButton(commands: CommandRegistry): StatusButton {
  return new StatusButton(commands);
}

export function createStatusMenu(commands: CommandRegistry) {
  commands.addCommand(CHECK_STATUS_BUTTON_COMMAND_ID, {
    label: CHECK_STATUS_BUTTON_LABEL,
    icon: checkIcon,
    execute: async () => {
      await showDialog({
        title: CHECK_STATUS_BUTTON_LABEL,
        body: (
          <div className="vdk-run-dialog-message-container">
            <p className="vdk-run-dialog-message">
              Operation is currently running!
            </p>
          </div>
        ),
        buttons: [Dialog.okButton()]
      });
    }
  });
}
