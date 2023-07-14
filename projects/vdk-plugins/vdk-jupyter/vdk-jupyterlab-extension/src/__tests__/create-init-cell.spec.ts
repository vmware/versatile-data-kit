/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { INotebookTracker, NotebookTracker } from '@jupyterlab/notebook';
import { NBTestUtils } from '@jupyterlab/testutils';
import { initNotebookContext } from '@jupyterlab/testutils';
import { initVDKCell } from '../initVDKCell';

const createNotebookTracker = async () => {
  let notebookTracker = new NotebookTracker({ namespace: 'notebook' });
  let context = await initNotebookContext();

  await notebookTracker.add(NBTestUtils.createNotebookPanel(context));

  return notebookTracker;
};

describe('initVDKCell', () => {
  it('should create an init cell for an empty notebook', async () => {
    const mockNotebookTracker = await createNotebookTracker();

    initVDKCell(mockNotebookTracker as INotebookTracker);
    let cells = mockNotebookTracker.currentWidget?.content.model?.cells;
    let firstCellContent = cells?.get(0).value.text;

    expect(mockNotebookTracker.currentWidget).toEqual('');

    // expect(cells).toEqual([])

    if (cells) {
      expect(cells.length).toEqual(1);

      expect(firstCellContent).toEqual(
        `"""\n` +
          `vdk_ipython extension introduces a magic command for Jupyter.\n` +
          `The command enables the user to load VDK for the current notebook.\n` +
          `VDK provides the job_input API, which has methods for:\n` +
          `    * executing queries to an OLAP database;\n` +
          `    * ingesting data into a database;\n` +
          `    * processing data into a database.\n` +
          `See the IJobInput documentation for more details.\n` +
          `https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/api/job_input.py\n` +
          `Please refrain from tagging this cell with VDK as it is not an actual part of the data job\n` +
          `and is only used for development purposes.\n` +
          `"""\n` +
          `%reload_ext vdk_ipython\n` +
          `%reload_VDK\n` +
          `job_input = VDK.get_initialized_job_input()`
      );
    }
  });

  /*
    it("should not create an init cell for a notebook which has it already", async() => {
        initVDKCell(mockNotebookTracker as INotebookTracker);

        let cells = mockNotebookTracker.currentWidget?.content.model?.cells;

        expect(cells?.length).toEqual(1);
    });*/
});
