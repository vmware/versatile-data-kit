/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

import { INotebookTracker } from '@jupyterlab/notebook';

/**
 * This func adds a cell with the necessary commands to enable VDK for a Jupyter notebook
 */
export function initVDKConfigCell(notebookTracker: INotebookTracker) {
  const notebookPanel = notebookTracker.currentWidget;
  if (notebookPanel) {
    // Create Markdown Cell
    const markdownCell =
      notebookPanel.content.model?.contentFactory?.createMarkdownCell({
        // eslint-disable-next-line prettier/prettier
        cell: {
          cell_type: 'markdown',
          source: [
            'You are running in environment where VDK Jupyter extension is installed.<br/>',
            'If you are not using VDK, you can delete and ignore this and below cell.<br/><br/>',
            'To learn more check out [VDK Notebook Getting Started](https://bit.ly/vdk-notebook).<br/><br/>',
            '**IMPORTANT: Please execute the cell below to load the VDK job_input variable.**'
          ],
          metadata: { editable: false }
        }
      });

    // Create Code Cell
    const codeCell =
      notebookPanel.content.model?.contentFactory?.createCodeCell({
        cell: {
          cell_type: 'code',
          source: [
            '"""\n',
            'vdk.plugin.ipython extension introduces a magic command for Jupyter.\n',
            'The command enables the user to load VDK for the current notebook.\n',
            'VDK provides the job_input API, which has methods for:\n',
            '    * executing queries to an OLAP database;\n',
            '    * ingesting data into a database;\n',
            '    * processing data into a database.\n',
            'Type help(job_input) to see its documentation.\n\n',
            '"""\n',
            '%reload_ext vdk.plugin.ipython\n',
            '%reload_VDK\n',
            'job_input = VDK.get_initialized_job_input()'
          ],
          metadata: { editable: false }
        }
      });

    const emptyCodeCell =
      notebookPanel.content.model?.contentFactory?.createCodeCell({
        cell: {
          cell_type: 'code',
          source: [],
          metadata: { tags: ['vdk'] }
        }
      });

    const cells = notebookPanel.content.model?.cells;
    const cellContent = cells?.get(0).value.text;

    // Check if the notebook has only 1 empty cell
    if (
      cells &&
      markdownCell &&
      codeCell &&
      emptyCodeCell &&
      cells.length <= 1 &&
      cellContent === ''
    ) {
      // Insert Markdown Cell at position 0
      cells.insert(0, markdownCell);

      // Insert Code Cell at position 1
      cells.insert(1, codeCell);

      cells.insert(2, emptyCodeCell);

      // Remove the old empty cell at position 3
      cells.remove(3);
    }
  }
}
