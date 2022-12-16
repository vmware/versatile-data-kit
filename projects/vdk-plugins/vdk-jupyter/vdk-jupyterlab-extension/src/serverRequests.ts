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