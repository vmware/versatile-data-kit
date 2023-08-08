import React, { Component } from 'react';
import { VdkOption } from '../vdkOptions/vdk_options';
import VDKTextInput from './VdkTextInput';
import { Dialog, showDialog } from '@jupyterlab/apputils';
import { jobRequest } from '../serverRequests';
import { IJobPathProp } from './props';
import { jobData } from '../jobData';
import { DOWNLOAD_KEY_BUTTON_LABEL, getParentDirectory } from '../utils';

export default class DownloadKeyDialog extends Component<IJobPathProp> {
  /**
   * Returns a React component for rendering a download menu.
   *
   * @param props - component properties
   * @returns React component
   */
  constructor(props: IJobPathProp) {
    super(props);
  }
  /**
   * Renders a dialog for downloading a data job key.
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
          option={VdkOption.PATH}
          value={getParentDirectory(this.props.jobPath)}
          label="Destination path to data job key directory:"
        ></VDKTextInput>
      </>
    );
  }
}

export async function showDownloadKeyDialog() {
  const defaultPath = jobData.get(VdkOption.PATH)!;
  const result = await showDialog({
    title: DOWNLOAD_KEY_BUTTON_LABEL,
    body: (
      <DownloadKeyDialog
        jobPath={jobData.get(VdkOption.PATH)!}
      ></DownloadKeyDialog>
    ),
    buttons: [Dialog.okButton(), Dialog.cancelButton()]
  });
  if (result.button.accept) {
    if (jobData.get(VdkOption.PATH) === defaultPath) {
      jobData.set(VdkOption.PATH, getParentDirectory(defaultPath));
    }
    await jobRequest('downloadKey');
  }
}
