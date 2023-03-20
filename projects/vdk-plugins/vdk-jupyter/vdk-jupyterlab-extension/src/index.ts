/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { updateVDKMenu } from './commandsAndMenu';

import { FileBrowserModel, IFileBrowserFactory } from '@jupyterlab/filebrowser';
import { IChangedArgs } from '@jupyterlab/coreutils';
import { jobData } from './jobData';
import { VdkOption } from './vdkOptions/vdk_options';
import { jobdDataRequest } from './serverRequests';

/**
 * Initialization data for the vdk-jupyterlab-extension extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'vdk-jupyterlab-extension:plugin',
  autoStart: true,
  optional: [ISettingRegistry, IFileBrowserFactory],
  activate: async (
    app: JupyterFrontEnd,
    settingRegistry: ISettingRegistry | null,
    factory: IFileBrowserFactory
  ) => {
    const { commands } = app;

    updateVDKMenu(commands);

    const fileBrowser = factory.defaultBrowser;
    fileBrowser.model.pathChanged.connect(onPathChanged);
  }
};

export default plugin;

const onPathChanged = async (
  model: FileBrowserModel,
  change: IChangedArgs<string>
) => {
  jobData.set(VdkOption.PATH, change.newValue);
  await jobdDataRequest();
};
