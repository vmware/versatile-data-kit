/**
 * Dataclass for run job operation inputs
 */
 export default class RunJobData {
    constructor(public jobPath: String, public jobArguments: String) {}

    setToDefault(){
        this.jobPath = "";
        this.jobArguments = "";
    }
}
