/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { INotebookTracker } from '@jupyterlab/notebook';

/**
 * This func adds a cell with the necessary commands to enable VDK for a Jupyter notebook
 */
export function initVDKConfigCell(notebookTracker: INotebookTracker) {
  const notebookPanel = notebookTracker.currentWidget;
  if (notebookPanel) {
    const initCell =
      notebookPanel.content.model?.contentFactory?.createCodeCell({
        cell: {
          cell_type: 'code',
          source: [
            `"""\n`,
            `This cell must be executed to load VDK job_input variable .\n\n`,
            `vdk.plugin.ipython extension introduces a magic command for Jupyter.\n`,
            `The command enables the user to load VDK for the current notebook.\n`,
            `VDK provides the job_input API, which has methods for:\n`,
            `    * executing queries to an OLAP database;\n`,
            `    * ingesting data into a database;\n`,
            `    * processing data into a database.\n`,
            `Type help(job_input) to see its documentation.\n`,
            `"""\n`,
            `%reload_ext vdk.plugin.ipython\n`,
            `%reload_VDK\n`,
            `job_input = VDK.get_initialized_job_input()`
          ],
          metadata: { editable: false }
        }
      });
    const cells = notebookTracker.currentWidget?.content.model?.cells;
    const cellContent = cells?.get(0).value.text;
    // check if the notebook has only 1 empty cell, which is how we judge if it is a new notebook or not
    if (cells && initCell && cells.length <= 1 && cellContent == '') {
      cells.insert(0, initCell);
      cells.remove(1);
    }
  }
}
