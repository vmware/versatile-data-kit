import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { requestAPI } from './handler';

/**
 * Initialization data for the vdk-jupyterlab-extension extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'vdk-jupyterlab-extension:plugin',
  autoStart: true,
  optional: [ISettingRegistry],
  activate: (app: JupyterFrontEnd, settingRegistry: ISettingRegistry | null) => {
    console.log('JupyterLab extension vdk-jupyterlab-extension is activated!');

    if (settingRegistry) {
      settingRegistry
        .load(plugin.id)
        .then(settings => {
          console.log('vdk-jupyterlab-extension settings loaded:', settings.composite);
        })
        .catch(reason => {
          console.error('Failed to load settings for vdk-jupyterlab-extension.', reason);
        });
    }

    requestAPI<any>('get_example')
      .then(data => {
        console.log(data);
      })
      .catch(reason => {
        console.error(
          `The vdk-jupyterlab-extension server extension appears to be missing.\n${reason}`
        );
      });
  }
};

export default plugin;
