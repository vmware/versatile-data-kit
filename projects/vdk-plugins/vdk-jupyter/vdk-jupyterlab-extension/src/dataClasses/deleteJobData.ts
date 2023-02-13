/**
 * Dataclass for delete job operation inputs
 */
 export default class DeleteJobData {
    constructor(public jobName: String, public jobTeam: String, public restApiUrl: String) {}

    setToDefault(){
        this.jobName = "";
        this.jobTeam = "";
        this.restApiUrl = "";
    }
}