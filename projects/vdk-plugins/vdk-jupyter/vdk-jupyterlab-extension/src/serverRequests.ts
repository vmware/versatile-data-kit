import { requestAPI } from "./handler";
 /**
   * Utility functions that are called by the dialogs.
   * They are called when a request to the server is needed to be sent.
   */


 /**
    * Sent a GET request to the server to get current working directory
    */
export function getCurrentPathRequest(){
    requestAPI<any>('run', {
        method: 'GET',
    })
        .then(data => {
            sessionStorage.setItem("current-path", data["path"]);
        })
        .catch(reason => {
            console.error(
                `The jlab_vdk server extension appears to be missing.\n${reason}`
            );
        });
}

 /**
    * Sent a POST request to the server to run a data job.
    * The information about the data job is retrieved from sessionStorage and sent as JSON.
    */
export function jobRunRequest() {
    const dataToSend = {
        jobPath: sessionStorage.getItem("job-path"),
        jobArguments: sessionStorage.getItem("job-args")
    };
    requestAPI<any>('run', {
        body: JSON.stringify(dataToSend),
        method: 'POST',
    })
        .then(data => {
            const message = "Job execution has finished with status " + data["message"] + " \n See vdk_logs.txt file for more!";
            alert(message);
            sessionStorage.removeItem("job-args");
        })
        .catch(reason => {
            console.error(
                `The jlab_vdk server extension appears to be missing.\n${reason}`
            );
        });
}

 /**
    * Sent a POST request to the server to delete a data job.
    * The information about the data job is retrieved from sessionStorage and sent as JSON.
    */
  export function deleteJobRequest() {
    let dataToSend = {
        jobName: sessionStorage.getItem("delete-job-name"),
        jobTeam: sessionStorage.getItem("delete-job-team"),
        restApiUrl: sessionStorage.getItem("delete-job-rest-api-url")
    };
    requestAPI<any>('delete', {
        body: JSON.stringify(dataToSend),
        method: 'POST',
    })
        .then(data => {
            alert(data["message"]);
        })
        .catch(reason => {
            throw(reason)
        });
}


 /**
    * Sent a POST request to the server to download a data job.
    * The information about the data job is retrieved from sessionStorage and sent as JSON.
    */
  export function downloadJobRequest() {
    let dataToSend = {
        jobName: sessionStorage.getItem("download-job-name"),
        jobTeam: sessionStorage.getItem("download-job-team"),
        restApiUrl: sessionStorage.getItem("download-job-rest-api-url"),
        parentPath: sessionStorage.getItem("download-job-path"),
    };
    requestAPI<any>('download', {
        body: JSON.stringify(dataToSend),
        method: 'POST',
    })
        .then(data => {
            alert(data["message"]);
        })
        .catch(reason => {
            throw(reason)
        });
}
