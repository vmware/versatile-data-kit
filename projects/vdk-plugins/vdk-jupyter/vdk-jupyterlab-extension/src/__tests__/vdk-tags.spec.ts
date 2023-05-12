/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { addNumberElement, addVdkCellDesign, addVdkLogo } from '../vdkTags';
import { IThemeManager } from '@jupyterlab/apputils';

describe('addNumberElement', () => {
  let node: HTMLElement;

  beforeEach(() => {
    node = document.createElement('div');
  });

  it('should add a cell number element to the node', () => {
    const number = 1;

    addNumberElement(number, node);

    const numberElement = node.querySelector('.jp-vdk-cell-num') as HTMLElement;
    expect(numberElement).toBeTruthy();
    expect(numberElement.innerText).toEqual(`${number}`);
  });

  it('should add a failing cell number element to the node', () => {
    const number = 2;
    node.classList.add('jp-vdk-failing-cell');

    addNumberElement(number, node);

    const numberElement = node.querySelector(
      '.jp-vdk-failing-cell-num'
    ) as HTMLElement;
    expect(numberElement).toBeTruthy();
    expect(numberElement.innerText).toEqual(`${number}`);
  });
});

describe('addVdkLogo', () => {
  let node: Element;

  beforeEach(() => {
    // Create a new div element for each test case
    node = document.createElement('div');
  });

  it('should add the VDK logo to the node', () => {
    // Call the function with the test node
    addVdkLogo(node);

    // Check that the node now contains the VDK logo
    const logo = node.querySelector('img');
    expect(logo).not.toBeNull();
    expect(logo?.getAttribute('src')).toEqual(
      'https://raw.githubusercontent.com/vmware/versatile-data-kit/dc15f7489f763a0e0e29370b2e06a714448fc234/support/images/versatile-data-kit-logo.svg'
    );
    expect(logo?.getAttribute('width')).toEqual('20');
    expect(logo?.getAttribute('height')).toEqual('20');
    expect(logo?.classList.contains('jp-vdk-logo')).toBe(true);
  });
});

const mockThemeManager: Partial<IThemeManager> = {
  theme: '',
  isLight: jest.fn()
};

describe('addVdkCellDesign', () => {
  let cells: Element[];
  let vdkCellIndices: Array<Number>;
  let currentCell: Element;

  beforeEach(() => {
    cells = [
      document.createElement('div'),
      document.createElement('div'),
      document.createElement('div')
    ];
    vdkCellIndices = [0, 2];
    currentCell = document.createElement('div');
  });

  // the tests do not check the theme so both the themes are added

  it('should add vdk cell design to specified cells', () => {
    addVdkCellDesign(
      cells,
      vdkCellIndices,
      mockThemeManager as IThemeManager,
      currentCell
    );

    cells.forEach((cell, i) => {
      if (vdkCellIndices.includes(i)) {
        expect(cell.classList).toContain('jp-vdk-cell');
        expect(cell.classList).toContain('jp-vdk-cell-dark');
      } else {
        expect(cell.classList).not.toContain('jp-vdk-cell');
        expect(cell.classList).not.toContain('jp-vdk-cell-dark');
      }
    });
  });

  it('should remove previous numbering and logo when untagging elements', () => {
    const mockVdkCellNums = [
      document.createElement('div'),
      document.createElement('div'),
      document.createElement('div'),
      document.createElement('div')
    ];
    mockVdkCellNums.forEach(element => {
      element.classList.add('jp-vdk-cell-num');
      document.body.appendChild(element);
    });

    const mockVdkCellLogo = [
      document.createElement('div'),
      document.createElement('div'),
      document.createElement('div'),
      document.createElement('div')
    ];
    mockVdkCellLogo.forEach(element => {
      element.classList.add('jp-vdk-logo');
      document.body.appendChild(element);
    });

    addVdkCellDesign(cells, [], mockThemeManager as IThemeManager, currentCell);

    expect(document.getElementsByClassName('jp-vdk-cell-num').length).toEqual(
      0
    );
    expect(document.getElementsByClassName('jp-vdk-logo').length).toEqual(0);
  });
});
