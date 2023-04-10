/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { INotebookTracker } from '@jupyterlab/notebook';

function addVdkClass(cells: Element[], vdkCellIndices: Array<Number>) {
  for (let i = 0; i < cells.length; i++) {
    if (vdkCellIndices.includes(i)) {
      cells[i].classList.add('jp-vdk-cell');
    } else {
      cells[i].classList.remove('jp-vdk-cell');
    }
  }
}

export function trackVdkTags(notebookTracker: INotebookTracker): void {
  const handleActiveCellChanged = () => {
    if (notebookTracker.currentWidget?.model?.cells.get(0)) {
      let vdkCellIndices = [];
      let cellIndex = 0;
      while (notebookTracker.currentWidget?.model?.cells.get(cellIndex)) {
        let currentCellTags = notebookTracker.currentWidget?.model?.cells
          .get(cellIndex)
          .metadata.get('tags')! as ReadonlyArray<String>;
        if (currentCellTags && currentCellTags.includes('vdk')) {
          vdkCellIndices.push(cellIndex);
        }
        cellIndex++;
      }
      if (notebookTracker.activeCell?.parent?.node.children) {
        addVdkClass(
          Array.from(notebookTracker.activeCell?.parent?.node.children!),
          vdkCellIndices
        );
      }
    }
  };

  notebookTracker.activeCellChanged.connect(handleActiveCellChanged);
}
