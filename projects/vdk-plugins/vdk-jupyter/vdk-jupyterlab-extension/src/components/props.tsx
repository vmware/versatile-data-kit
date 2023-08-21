import { Dialog, showDialog } from '@jupyterlab/apputils';
import { closeIcon } from '@jupyterlab/ui-components';
import React from 'react';
import IButton = Dialog.IButton;
import { ERROR_DIALOG_CLASS } from '../utils';

export type IJobPathProp = {
  /**
   * Current Job path or the path to job's parent directory
   */
  jobPath: string;
};

export type IJobNameAndTeamProps = {
  /**
   * Current Job name
   */
  jobName: string;
  /**
   * Current Team name
   */
  jobTeam: string;
};

export type IJobFullProps = IJobPathProp & IJobNameAndTeamProps;

export interface JupyterCellProps {
  /**
   * Source code of the cell
   */
  source: string;
  /**
   * Type of the cell
   */
  type: string;
}

export interface IErrorDialogProps {
  title: string;
  messages: String[];
  error?: any;
  buttons?: Array<IButton>;
}

export async function showErrorDialog(props: IErrorDialogProps) {
  const {
    title,
    messages,
    error,
    buttons = [Dialog.okButton({ label: 'OK' })]
  } = props;

  return await showDialog({
    title: title,
    body: (
      <div className={ERROR_DIALOG_CLASS}>
        <closeIcon.react className="vdk-dialog-error-icon" />
        <div>
          {messages.map((msg, index) => (
            <p key={index}>{msg}</p>
          ))}{' '}
          {error && <p>{error}</p>}
        </div>
      </div>
    ),
    buttons: buttons
  });
}
