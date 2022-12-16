import { CommandRegistry } from "@lumino/commands";
import { Dialog, showDialog } from "@jupyterlab/apputils";
import React from "react";
import RunJobDialong from "./components/RunJob";
import { jobRunRequest } from "./serverRequests";

export function updateVDKMenu(commands: CommandRegistry) {
    commands.addCommand("jp-vdk:menu-run", {
        label: "Run",
        caption: 'Execute VDK Run Command',
        execute: async () => {
            showDialog({
                title: "Run Job",
                body: <RunJobDialong jobPath={sessionStorage.getItem("current-path")!} ></RunJobDialong>,
                buttons: [Dialog.okButton(), Dialog.cancelButton()],
            }).then(result => {
                if (!result.value) {
                    jobRunRequest();
                }
            }).catch((e) => console.log(e));
        },
    });
}