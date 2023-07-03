/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { INotebookTracker } from '@jupyterlab/notebook';

export function initVDKCell(notebookTracker: INotebookTracker) {
  notebookTracker.activeCellChanged.connect((sender, args) => {
    const notebookPanel = notebookTracker.currentWidget;
    if (notebookPanel) {
      const initCell =
        notebookPanel.content.model?.contentFactory?.createCodeCell({
          cell: {
            cell_type: 'code',
            source: [
              `"""\n`,
              `vdk_ipython extension introduces a magic command for Jupyter.\n`,
              `The command enables the user to load VDK for the current notebook.\n`,
              `VDK provides the job_input API, which has methods for:\n`,
              `    * executing queries to an OLAP database;\n`,
              `    * ingesting data into a database;\n`,
              `    * processing data into a database.\n`,
              `See the IJobInput documentation for more details.\n`,
              `Please refrain from tagging this cell with VDK as it is not an actual part of the data job\n`,
              `and is only used for development purposes.\n`,
              `"""\n`,
              `%reload_ext vdk_ipython\n`,
              `%reload_VDK\n`,
              `job_input = VDK.get_initialized_job_input()`
            ],
            metadata: {}
          }
        });
      const cells = notebookTracker.currentWidget?.content.model?.cells;
      console.log('Cell count: ', cells?.length);
      const cellContent = cells?.get(0).value.text;
      if (cells && initCell && cells.length == 1 && cellContent == '') {
        cells.insert(0, initCell);
        cells.remove(1);
      }
    }
  });
}
