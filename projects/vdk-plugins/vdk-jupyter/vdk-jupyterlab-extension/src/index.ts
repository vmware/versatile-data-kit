/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { runningVdkOperation, updateVDKMenu } from './commandsAndMenu';

import { FileBrowserModel, IFileBrowserFactory } from '@jupyterlab/filebrowser';
import { IChangedArgs } from '@jupyterlab/coreutils';
import { INotebookTracker } from '@jupyterlab/notebook';
import { trackVdkTags } from './vdkTags';
import { IThemeManager } from '@jupyterlab/apputils';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { initVDKConfigCell } from './initVDKConfigCell';
import { populateNotebook } from './components/ConvertJobToNotebook';
import {
  createStatusButton,
  createStatusMenu
} from './components/StatusButton';

/**
 * Current working directory in Jupyter
 * The variable can be accessed anywhere in the JupyterFrontEndPlugin
 */
export let workingDirectory: string = '';

/**
 * Initialization data for the vdk-jupyterlab-extension extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'vdk-jupyterlab-extension:plugin',
  autoStart: true,
  optional: [
    ISettingRegistry,
    IFileBrowserFactory,
    INotebookTracker,
    IThemeManager,
    IDocumentManager
  ],
  activate: async (
    app: JupyterFrontEnd,
    settingRegistry: ISettingRegistry | null,
    factory: IFileBrowserFactory,
    notebookTracker: INotebookTracker,
    themeManager: IThemeManager,
    docManager: IDocumentManager
  ) => {
    const { commands } = app;

    notebookTracker.activeCellChanged.connect((sender, args) => {
      if (runningVdkOperation !== 'jp-vdk:menu-convert-job-to-notebook') {
        initVDKConfigCell(notebookTracker);
      } else {
        //  * Populates notebook with provided content for convert job operation
        //  * Check src/components/ConvertJobToNotebook.tsx for more
        populateNotebook(notebookTracker);
      }
    });

    createStatusMenu(commands);
    const statusButton = createStatusButton(commands);

    const fileBrowser = factory.defaultBrowser;

    app.restored.then(() => {
      const topPanel = document.querySelector('#jp-top-panel');
      if (topPanel) {
        topPanel.appendChild(statusButton.element);
      }
    });

    updateVDKMenu(
      commands,
      docManager,
      fileBrowser,
      notebookTracker,
      statusButton
    );

    fileBrowser.model.pathChanged.connect(onPathChanged);
    trackVdkTags(notebookTracker, themeManager);
  }
};

export default plugin;

const onPathChanged = async (
  model: FileBrowserModel,
  change: IChangedArgs<string>
) => {
  workingDirectory = change.newValue;
};
