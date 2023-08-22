/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * This enum is automatically generated from the enum from  ../vdk-jupyterlab-extension/vdk_options/vdk_options_.py
 * Using https://github.com/Syndallic/py-to-ts-interfaces#example
 * The enum shall not be modified directly
 */
import { VdkOption } from './vdkOptions/vdk_options';
import { Dialog, showErrorMessage } from '@jupyterlab/apputils';

/*
 * A global variable which holds the information about the current job.
 * This variable acts like session storage that holds information about the data job for the currently running Jupyter instance
 * The values of its properties are meant to be changed during a VDK operation and after the operation ends they need to be set to default.
 */

export var jobData = new Map<string, string>([]);

/*
 * Function responsible for reverting all vdkOption values of jobData to default
 */
export function setJobDataToDefault() {
  for (const option of Object.values(VdkOption)) {
    jobData.set(option as VdkOption, '');
  }
}

/*
 * Sets default VdkOption values to jobData when the extension is firstly loaded
 */
setJobDataToDefault();

/*
 * Function that return the JSON object of jobData
 * TODO: find a better wat to parse the Map into JSON object
 */
export function getJobDataJsonObject() {
  const jsObj = {
    jobName: jobData.get(VdkOption.NAME),
    jobTeam: jobData.get(VdkOption.TEAM),
    jobPath: jobData.get(VdkOption.PATH),
    jobArguments: jobData.get(VdkOption.ARGUMENTS),
    deploymentReason: jobData.get(VdkOption.DEPLOYMENT_REASON)
  };
  return jsObj;
}

/*
 * Function that checks whether a value is defined in jobData
 * Shows dialog that operation cannot be performed because of undefined value
 */
export async function checkIfVdkOptionDataIsDefined(
  option: VdkOption
): Promise<boolean> {
  if (jobData.get(option)) return true;
  else {
    await showErrorMessage(
      'Encountered an error while trying to execute operation. Error:',
      'The ' + option + ' should be defined!',
      [Dialog.okButton()]
    );
    return false;
  }
}
