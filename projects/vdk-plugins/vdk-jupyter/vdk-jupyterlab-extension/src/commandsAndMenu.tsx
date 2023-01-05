import { CommandRegistry } from "@lumino/commands";
import { Dialog, showDialog } from "@jupyterlab/apputils";
import React from "react";
import RunJobDialog from "./components/RunJob";
import { jobRunRequest } from "./serverRequests";
import CreateJobDialog from "./components/CreateJob";

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
}
