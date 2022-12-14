import { CommandRegistry } from "@lumino/commands";
import { Dialog, showDialog } from "@jupyterlab/apputils";
import React from "react";
import VariablesDialong from "./components/vdkVariables";

export function updateVDKMenu(commands: CommandRegistry) {
    commands.addCommand("jp-vdk:menu-variables", {
        label: "Set environmental variables",
        caption: 'Set environmental variables',
        execute: () => {
            showDialog({
                title: "Set environmental variables",
                body:<VariablesDialong label="VDK"></VariablesDialong>,
                buttons: [Dialog.okButton()],
            }).then(result => {
                if (!result.value) {
                }
            }).catch((e) => console.log(e));
        },
    });
}
