/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { INotebookTracker } from '@jupyterlab/notebook';
import { IThemeManager } from '@jupyterlab/apputils';
import { getVdkCellIndices } from './serverRequests';

export const addNumberElement = (number: Number, node: Element) => {
  const numberElement = document.createElement('div');
  numberElement.innerText = String(number);
  node.classList.contains('jp-vdk-failing-cell')
    ? numberElement.classList.add('jp-vdk-failing-cell-num')
    : numberElement.classList.add('jp-vdk-cell-num');
  node.appendChild(numberElement);
};

export const addVdkLogo = (node: Element) => {
  const logo = document.createElement('img');
  logo.setAttribute(
    'src',
    'https://raw.githubusercontent.com/vmware/versatile-data-kit/dc15f7489f763a0e0e29370b2e06a714448fc234/support/images/versatile-data-kit-logo.svg'
  );
  logo.setAttribute('width', '20');
  logo.setAttribute('height', '20');

  logo.classList.add('jp-vdk-logo');
  node.appendChild(logo);
};

export const addVdkCellDesign = (
  cells: Element[],
  vdkCellIndices: Array<Number>,
  themeManager: IThemeManager,
  currentCell?: Element
) => {
  // Delete previous numbering in case of untagging elements
  const vdkCellNums = Array.from(
    document.getElementsByClassName('jp-vdk-cell-num')
  );
  vdkCellNums.forEach(element => {
    element.remove();
  });

  // Delete previous fail numbering
  const vdkFailingCellNums = Array.from(
    document.getElementsByClassName('jp-vdk-failing-cell-num')
  );
  vdkFailingCellNums.forEach(element => {
    element.remove();
  });

  // Delete previously added logo in case of untagging elements
  const vdkCellLogo = Array.from(
    document.getElementsByClassName('jp-vdk-logo')
  );
  vdkCellLogo.forEach(element => {
    element.remove();
  });

  let vdkCellCounter = 0;
  for (let i = 0; i < cells.length; i++) {
    if (vdkCellIndices.includes(i)) {
      if (
        themeManager.theme &&
        themeManager.isLight(themeManager.theme.toString())
      ) {
        cells[i].classList.remove('jp-vdk-cell-dark');
        cells[i].classList.add('jp-vdk-cell');
      } else {
        cells[i].classList.add('jp-vdk-cell');
        cells[i].classList.add('jp-vdk-cell-dark');
      }
      // We do not add logo to the active cell since it blocks other UI elements
      if (currentCell && cells[i] != currentCell) {
        addVdkLogo(cells[i]);
      }

      addNumberElement(++vdkCellCounter, cells[i]);
    } else {
      cells[i].classList.remove('jp-vdk-cell');
      cells[i].classList.remove('jp-vdk-cell-dark');
    }
  }
};

export const trackVdkTags = (
  notebookTracker: INotebookTracker,
  themeManager: IThemeManager
): void => {
  const changeCells = async () => {
    if (
      notebookTracker.currentWidget &&
      notebookTracker.currentWidget.model &&
      notebookTracker.currentWidget.model.cells.length !== 0
    ) {
      // Get indices of the vdk cells using cell metadata
      let vdkCellIndices = [];
      let cellIndex = 0;
      while (
        notebookTracker.currentWidget &&
        notebookTracker.currentWidget.model &&
        notebookTracker.currentWidget.model.cells.get(cellIndex)
      ) {
        const currentCellTags = notebookTracker.currentWidget.model.cells
          .get(cellIndex)
          .metadata.get('tags')! as ReadonlyArray<String>;
        if (currentCellTags && currentCellTags.includes('vdk'))
          vdkCellIndices.push(cellIndex);
        cellIndex++;
      }
      // this case covers the use case when the notebook is loaded for the first time
      if (!vdkCellIndices.length) {
        vdkCellIndices = await getVdkCellIndices(
          notebookTracker.currentWidget.context.path
        );
      }
      if (
        vdkCellIndices.length > 0 &&
        notebookTracker.activeCell &&
        notebookTracker.activeCell.parent &&
        notebookTracker.activeCell.parent.node.children
      ) {
        addVdkCellDesign(
          Array.from(notebookTracker.activeCell.parent.node.children!),
          vdkCellIndices,
          themeManager,
          notebookTracker.activeCell.node
        );
      }
    }
  };

  notebookTracker.activeCellChanged.connect(changeCells);
  themeManager.themeChanged.connect(changeCells);
};
