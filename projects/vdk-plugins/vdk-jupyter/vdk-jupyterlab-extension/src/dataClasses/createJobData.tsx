/**
 * Dataclass for create job operation inputs
 */
 export default class CreateJobData {
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
