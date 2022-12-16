import { requestAPI } from "./handler";


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
