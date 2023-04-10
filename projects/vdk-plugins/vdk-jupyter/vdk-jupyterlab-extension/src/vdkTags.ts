/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { INotebookTracker } from '@jupyterlab/notebook';

function addNumberElement(number: Number, node: Element): void {
  const numberElement = document.createElement('div');
  numberElement.innerText = String(number);
  numberElement.classList.add('jp-vdk-cell-num');
  node.appendChild(numberElement);
}

function makeVdkCell(cells: Element[], vdkCellIndices: Array<Number>): void {
  // delete previous numbering in case of untagging elements
  let vdkCellNums = Array.from(
    document.getElementsByClassName('jp-vdk-cell-num')
  );
  vdkCellNums.forEach(element => {
    element.remove();
  });
  let vdkCellCounter = 0;
  for (let i = 0; i < cells.length; i++) {
    if (vdkCellIndices.includes(i)) {
      cells[i].classList.add('jp-vdk-cell');
      addNumberElement(vdkCellCounter++, cells[i]);
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
        makeVdkCell(
          Array.from(notebookTracker.activeCell?.parent?.node.children!),
          vdkCellIndices
        );
      }
    }
  };

  notebookTracker.activeCellChanged.connect(handleActiveCellChanged);
}
