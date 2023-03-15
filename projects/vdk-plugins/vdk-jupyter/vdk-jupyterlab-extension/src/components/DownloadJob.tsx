import React, { Component } from 'react';
import { VdkOption } from '../vdkOptions/vdk_options';
import VDKTextInput from './VdkTextInput';
import { Dialog, showDialog } from '@jupyterlab/apputils';
import { downloadJobRequest } from '../serverRequests';

export interface IDownloadJobDialogProps {
  /**
   * Current Path
   */
  parentPath: string;
}

export default class DownloadJobDialog extends Component<IDownloadJobDialogProps> {
  /**
   * Returns a React component for rendering a download menu.
   *
   * @param props - component properties
   * @returns React component
   */
  constructor(props: IDownloadJobDialogProps) {
    super(props);
  }
  /**
   * Renders a dialog for downloading a data job.
   *
   * @returns React element
   */
  render(): React.ReactElement {
    return (
      <>
        <VDKTextInput
          option={VdkOption.NAME}
          value="default-name"
          label="Job Name:"
        ></VDKTextInput>
        <VDKTextInput
          option={VdkOption.TEAM}
          value="default-team"
          label="Job Team:"
        ></VDKTextInput>
        <VDKTextInput
          option={VdkOption.REST_API_URL}
          value="http://my_vdk_instance"
          label="Rest API URL:"
        ></VDKTextInput>
        <VDKTextInput
          option={VdkOption.PATH}
          value={this.props.parentPath}
          label="Path to job directory:"
        ></VDKTextInput>
      </>
    );
  }
}

export async function showDownloadJobDialog() {
  const result = await showDialog({
    title: 'Download Job',
    body: (
      <DownloadJobDialog
        parentPath={sessionStorage.getItem('current-path')!}
      ></DownloadJobDialog>
    ),
    buttons: [Dialog.okButton(), Dialog.cancelButton()]
  });
  if (result.button.accept) {
    await downloadJobRequest();
  }
}
