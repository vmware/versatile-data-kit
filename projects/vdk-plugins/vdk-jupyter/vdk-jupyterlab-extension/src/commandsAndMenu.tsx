import { CommandRegistry } from "@lumino/commands";
import { Dialog, showDialog } from "@jupyterlab/apputils";
import React from "react";
import RunJobDialog from "./components/RunJob";
import { deleteJobRequest, jobRunRequest } from "./serverRequests";
import CreateJobDialog from "./components/CreateJob";
import DeleteJobDialog from "./components/DeleteJob";

export function updateVDKMenu(commands: CommandRegistry) {
    commands.addCommand("jp-vdk:menu-run", {
        label: "Run",
        caption: 'Execute VDK Run Command',
        execute: async () => {
            showDialog({
                title: "Run Job",
                body: <RunJobDialog jobPath={sessionStorage.getItem("current-path")!} ></RunJobDialog>,
                buttons: [Dialog.okButton(), Dialog.cancelButton()],
            }).then(result => {
                if (!result.value) {
                    jobRunRequest();
                }
            }).catch((e) => console.log(e));
        },
    });

    commands.addCommand("jp-vdk:menu-create", {
        label: "Create",
        caption: 'Execute VDK Create Command',
        execute: async () => {
            let defaultJobName = sessionStorage.getItem("current-path")!.substring(sessionStorage.getItem("current-path")!.lastIndexOf("/"));
            showDialog({
                title: "Create Job",
                body: <CreateJobDialog jobPath={sessionStorage.getItem("current-path")!} jobName={defaultJobName}></CreateJobDialog>,
                buttons: [Dialog.okButton(), Dialog.cancelButton()],
            }).then(result => {
                if (!result.value) {
                    // TODO: add server requests
                }
            }).catch((e) => console.log(e));
        },
    });

    commands.addCommand("jp-vdk:menu-delete", {
        label: "Delete",
        caption: 'Execute VDK Delete Command',
        execute: async () => {
            let defaultJobName = sessionStorage.getItem("current-path")!.substring(sessionStorage.getItem("current-path")!.lastIndexOf("/"));
            showDialog({
                title: "Create Job",
                body: <DeleteJobDialog jobName={defaultJobName}></DeleteJobDialog>,
                buttons: [Dialog.okButton(), Dialog.cancelButton()],
            }).then(async result => {
                if (!result.value) {
                    const actualResult = await showDialog({
                        title: "Delete a data job",
                        body: ('Do you really want to delete the job?'),
                        buttons: [
                          Dialog.cancelButton({ label: 'Cancel' }),
                          Dialog.warnButton({ label: 'Yes' })
                        ]
                      });
                    if (actualResult.button.accept) {  
                        try {
                            await deleteJobRequest();
                          } catch (error) {
                            console.error(
                                'Encountered an error when deleting the job. Error: ',
                                error
                            );
                        }
                    }
                }
            }).catch((e) => console.log(e));
        },
    });
}
