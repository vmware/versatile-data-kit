import { CommandRegistry } from '@lumino/commands';
import {
  STATUS_BUTTON_COMMAND_ID,
  STATUS_BUTTON_ID,
  STATUS_BUTTON_CLASS,
  STATUS_BUTTON_LABEL
} from '../utils';
import { Dialog, showDialog } from '@jupyterlab/apputils';
import React from 'react';
import { checkIcon } from '@jupyterlab/ui-components';
import { addVdkLogo } from '../vdkTags';

const formatSeconds = (s: number): string =>
  new Date(s * 1000).toISOString().substr(11, 8);

export class StatusButton {
  private readonly buttonElement: HTMLButtonElement;
  private operation: string | undefined;
  private jobPath: string | undefined;
  private timerId: number | undefined;
  private counter: number;
  private commands: CommandRegistry

  constructor(commands: CommandRegistry) {
    this.buttonElement = document.createElement('button');
    this.buttonElement.id = STATUS_BUTTON_ID;
    this.buttonElement.className = STATUS_BUTTON_CLASS;

    const contentContainer = document.createElement('div');
    contentContainer.className = 'jp-vdk-status-button-content';
    addVdkLogo(contentContainer);

    const timeElement = document.createElement('span');
    timeElement.innerHTML = '00:00:00';
    contentContainer.appendChild(timeElement);

    this.buttonElement.appendChild(contentContainer);
    this.commands = commands;

    this.buttonElement.onclick = () => {
      commands.execute(STATUS_BUTTON_COMMAND_ID, {
        operation: this.operation,
        path: this.jobPath
      });
    };

    this.buttonElement.title =
      'VDK operation is in progress. Click here for more info.';
    this.buttonElement.style.display = 'none';
    this.counter = 0;
  }

  get element(): HTMLButtonElement {
    return this.buttonElement;
  }

  show(operation: string, path: string): void {
    this.operation = operation;
    this.jobPath = path;
    this.buttonElement.style.display = '';
    this.startTimer();
    this.commands.execute(STATUS_BUTTON_COMMAND_ID, {
      operation: this.operation,
      path: this.jobPath
    });
  }

  hide(): void {
    this.buttonElement.style.display = 'none';
    this.stopTimer();
  }

  private startTimer() {
    this.counter = 0;
    this.timerId = window.setInterval(() => {
      this.counter++;
      const timeElement = this.buttonElement.querySelector('span');
      if (timeElement) {
        timeElement.innerHTML = `${formatSeconds(this.counter)}`;
      }
    }, 1000);
  }

  private stopTimer() {
    if (this.timerId) {
      clearInterval(this.timerId);
      this.timerId = undefined;
    }
    const timeElement = this.buttonElement.querySelector('span');
    if (timeElement) {
      timeElement.innerHTML = '00:00:00';
    }
  }
}

export function createStatusButton(commands: CommandRegistry): StatusButton {
  return new StatusButton(commands);
}

export function createStatusMenu(commands: CommandRegistry) {
  commands.addCommand(STATUS_BUTTON_COMMAND_ID, {
    label: STATUS_BUTTON_LABEL,
    icon: checkIcon,
    execute: async args => {
      const operation = args.operation || 'UNKNOWN';
      const path = args.path || 'UNKNOWN';
      await showDialog({
        title: STATUS_BUTTON_LABEL,
        body: (
          <div className="vdk-status-dialog-message-container">
            <p className="vdk-status-dialog-message">
              <b>{operation}</b> operation is currently running for job with
              path: <i>{path}</i>!<br />
            </p>
            <p className="vdk-status-dialog-message-little">
              You can close this dialog and follow the operation using the
              status button in the upper right corner.
            </p>
          </div>
        ),
        buttons: [Dialog.okButton()]
      });
    }
  });
}
