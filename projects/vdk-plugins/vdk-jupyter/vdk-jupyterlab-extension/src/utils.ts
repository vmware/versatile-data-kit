
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


/**
 * Dataclass for run job operation inputs
 */
export class RunJobData {
    constructor(public jobPath: String, public jobArguments: String) {}

    setToDefault(){
        this.jobPath = "";
        this.jobArguments = "";
    }
}

/**
 * Dataclass for create job operation inputs
 */
export class CreateJobData {
    constructor(public jobName: String, public jobTeam: String, public restApiUrl: String, public jobPath: String,public local: String, public cloud: String, ) {}

    setToDefault(){
        this.jobName = "";
        this.jobTeam = "";
        this.restApiUrl = "";
        this.jobPath = "";
        this.cloud = "";
        this.local = "";
    }
}