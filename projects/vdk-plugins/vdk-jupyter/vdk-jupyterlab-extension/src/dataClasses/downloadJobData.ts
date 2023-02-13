/**
 * Dataclass for download job operation inputs
 */
 export default class DownloadJobData {
    constructor(public jobName: String, public jobTeam: String, public restApiUrl: String, public jobPath: String) {}

    setToDefault(){
        this.jobName = "";
        this.jobTeam = "";
        this.restApiUrl = "";
        this.jobPath = ""
    }
}