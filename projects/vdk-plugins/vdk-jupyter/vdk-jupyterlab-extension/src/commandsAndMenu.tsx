import { CommandRegistry } from "@lumino/commands";
import { Dialog, showDialog } from "@jupyterlab/apputils";
import React from "react";
import RunJobDialog from "./components/RunJob";
import { jobRunRequest } from "./serverRequests";

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
}
