import data from "./jobDataModel.json";

export var jobData = JSON.parse(JSON.stringify(data));

export function revertJobDataToDefault(){
    jobData = JSON.parse(JSON.stringify(data));
}