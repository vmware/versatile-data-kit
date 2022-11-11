import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { requestAPI } from './handler';

/**
 * Initialization data for the vdk-jupyter extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'vdk-jupyter:plugin',
  autoStart: true,
  optional: [ISettingRegistry],
  activate: (app: JupyterFrontEnd, settingRegistry: ISettingRegistry | null) => {
    console.log('JupyterLab extension vdk-jupyter is activated!');

    if (settingRegistry) {
      settingRegistry
        .load(plugin.id)
        .then(settings => {
          console.log('vdk-jupyter settings loaded:', settings.composite);
        })
        .catch(reason => {
          console.error('Failed to load settings for vdk-jupyter.', reason);
        });
    }

    requestAPI<any>('get_example')
      .then(data => {
        console.log(data);
      })
      .catch(reason => {
        console.error(
          `The vdk-jupyter server extension appears to be missing.\n${reason}`
        );
      });
  }
};

export default plugin;
