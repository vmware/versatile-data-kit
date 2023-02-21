/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * This enum is automatically generated from the enum from  ../vdk-jupyterlab-extension/ui_job_properties.py
 * Using https://github.com/Syndallic/py-to-ts-interfaces#example
 */
export enum JobProperties {
  name = 'jobName',
  team = 'jobTeam',
  restApiUrl = 'restApiUrl',
  path = 'jobPath',
  cloud = 'cloud',
  local = 'local',
  arguments = 'jobArguments'
}

/*
 * In the front-end extension a global variable is introduces (jobData) which holds the information about the current job.
 * The values of its properties are meant to be changed during a VDK operation and after the operation ends they need to be set to default.
 */
export var jobData = new Map<string, string>([
  [JobProperties.name, ''],
  [JobProperties.team, ''],
  [JobProperties.restApiUrl, ''],
  [JobProperties.path, ''],
  [JobProperties.cloud, ''],
  [JobProperties.local, ''],
  [JobProperties.arguments, '']
]);

/*
 * Function responsible for reverting all property values of jobData to default
 */
export function revertJobDataToDefault() {
    jobData.set(JobProperties.name, '');
    jobData.set(JobProperties.team, '');
    jobData.set(JobProperties.restApiUrl, '');
    jobData.set(JobProperties.path, '');
    jobData.set(JobProperties.cloud, '');
    jobData.set(JobProperties.local, '');
    jobData.set(JobProperties.arguments, '');
}


/*
 * Function taht return the JSON object of jobData
 */
export function getJobDataJsonObject() {
    const jsObj = {
        'jobName': jobData.get(JobProperties.name),
        'jobTeam': jobData.get(JobProperties.team),
        'restApiUrl': jobData.get(JobProperties.restApiUrl),
        'jobPath': jobData.get(JobProperties.path),
        'cloud': jobData.get(JobProperties.cloud),
        'local': jobData.get(JobProperties.local),
        'jobArguments': jobData.get(JobProperties.arguments)
    };
    return jsObj;
}
