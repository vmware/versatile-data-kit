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
  private operation: string | undefined;
  private jobPath: string | undefined;
  private timerId: number | undefined;
  private counter: number;

  constructor(commands: CommandRegistry) {
    this.buttonElement = document.createElement('button');
    this.buttonElement.innerHTML = CHECK_STATUS_BUTTON_LABEL + ' 00:00:00';
    this.buttonElement.id = CHECK_STATUS_BUTTON_ID;
    this.buttonElement.className = CHECK_STATUS_BUTTON_CLASS;

    this.buttonElement.onclick = () => {
      commands.execute(CHECK_STATUS_BUTTON_COMMAND_ID, {
        operation: this.operation,
        path: this.jobPath
      });
    };

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
  }

  hide(): void {
    this.buttonElement.style.display = 'none';
    this.stopTimer();
  }

  private startTimer() {
    this.counter = 0;
    this.timerId = window.setInterval(() => {
      this.counter++;
      this.buttonElement.innerHTML = `${CHECK_STATUS_BUTTON_LABEL} ${this.formatTime(
        this.counter
      )}`;
    }, 1000);
  }

  private stopTimer() {
    if (this.timerId) {
      clearInterval(this.timerId);
      this.timerId = undefined;
    }
    this.buttonElement.innerHTML = CHECK_STATUS_BUTTON_LABEL + ' 00:00:00';
  }

  private formatTime(seconds: number): string {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h.toString().padStart(2, '0')}:${m
      .toString()
      .padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  }
}

export function createStatusButton(commands: CommandRegistry): StatusButton {
  return new StatusButton(commands);
}

export function createStatusMenu(commands: CommandRegistry) {
  commands.addCommand(CHECK_STATUS_BUTTON_COMMAND_ID, {
    label: CHECK_STATUS_BUTTON_LABEL,
    icon: checkIcon,
    execute: async args => {
      const operation = args.operation || 'UNKNOWN';
      const path = args.path || 'UNKNOWN';
      await showDialog({
        title: CHECK_STATUS_BUTTON_LABEL,
        body: (
          <div className="vdk-status-dialog-message-container">
            <p className="vdk-status-dialog-message">
              {operation} operation is currently running for job with path:{' '}
              {path}!
            </p>
          </div>
        ),
        buttons: [Dialog.okButton()]
      });
    }
  });
}
