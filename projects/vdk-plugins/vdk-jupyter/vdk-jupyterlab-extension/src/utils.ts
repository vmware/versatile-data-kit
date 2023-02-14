

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

export function removeCreateJobDataFromSessionStorage(){
    sessionStorage.removeItem('create-job-name');
    sessionStorage.removeItem('create-job-team');
    sessionStorage.removeItem('create-job-rest-api-url');
    sessionStorage.removeItem('create-job-path');
    sessionStorage.removeItem('local');
    sessionStorage.removeItem('cloud');
}

export function removeRunJobDataFromSessionStorage(){
    sessionStorage.removeItem('job-path');
    sessionStorage.removeItem('job-args');
}

export function removeDeleteJobDataFromSessionStorage(){
    sessionStorage.removeItem('delete-job-name');
    sessionStorage.removeItem('delete-job-team');
    sessionStorage.removeItem('delete-job-rest-api-url');
}

export function removeDownloadJobDataFromSessionStorage(){
    sessionStorage.removeItem('download-job-name');
    sessionStorage.removeItem('download-job-team');
    sessionStorage.removeItem('download-job-rest-api-url');
    sessionStorage.removeItem('download-job-path');
}
