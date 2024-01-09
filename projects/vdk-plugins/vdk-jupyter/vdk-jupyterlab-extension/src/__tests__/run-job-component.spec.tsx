/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */
import RunJobDialog, { findFailingCellId, getCellInputAreaPrompt, handleErrorsProducedByNotebookCell } from '../components/RunJob';
import { render, fireEvent } from '@testing-library/react';
import { jobData } from '../jobData';
import { VdkOption } from '../vdkOptions/vdk_options';
import { IJobPathProp } from '../components/props';
import { VdkErrorMessage } from '../components/VdkErrorMessage';
import { IDocumentManager } from '@jupyterlab/docmanager';

const defaultProps: IJobPathProp = {
  jobPath: 'test-path'
};

// created with the expectation to compare a rendered value with expected value parsed from config.ini
// yet to be implemented
describe('#render()', () => {
  it('should return contain job path input with placeholder equal to jobPath from props', () => {
    const component = render(new RunJobDialog(defaultProps).render());
    const input = component.getByPlaceholderText(defaultProps.jobPath);
    expect(input).toBe(
      component.getAllByLabelText('Path to job directory:')[0]
    );
  });
  it('should return contain job arguments input with placeholder equal to {"key": "value"}', () => {
    const component = render(new RunJobDialog(defaultProps).render());
    const input = component.getByPlaceholderText('{"key": "value"}');
    expect(input).toBe(component.getAllByLabelText('Arguments:')[0]);
  });
});

describe('#onPathChange', () => {
  it('should change the path in jobData', () => {
    const component = render(new RunJobDialog(defaultProps).render());
    const input = component.getByPlaceholderText(defaultProps.jobPath);
    fireEvent.change(input, { target: { value: 'other/path' } });
    expect(jobData.get(VdkOption.PATH)).toEqual('other/path');
  });
});

describe('#onArgumentsChange', () => {
  it('should change the arguments in jobData', () => {
    const component = render(new RunJobDialog(defaultProps).render());
    const input = component.getByPlaceholderText('{"key": "value"}');
    fireEvent.change(input, { target: { value: '{"my_key": "my_value"}' } });
    expect(jobData.get(VdkOption.ARGUMENTS)).toEqual('{"my_key": "my_value"}');
  });
});


describe('findFailingCellId', () => {
  it('should return empty string for invalid message', () => {
    const message = 'An error occurred';
    expect(findFailingCellId(message)).toEqual('');
  });

  it('should return cell ID for valid message', () => {
    const message = 'An error occurred in cell_id:1234-abcd-5678';
    expect(findFailingCellId(message)).toEqual('1234-abcd-5678');
  });

  it('should return cell ID for valid message with uppercase hex characters', () => {
    const message = 'An error occurred in cell_id:1234-ABCD-5678';
    expect(findFailingCellId(message)).toEqual('1234-ABCD-5678');
  });

  it('should return empty string for message with invalid cell ID', () => {
    const message = 'An error occurred in cell_id:invalid-cell-id';
    expect(findFailingCellId(message)).toEqual('');
  });
});

import { showDialog } from '@jupyterlab/apputils';
import { getNotebookInfo } from '../serverRequests';
//import React from 'react';

jest.mock('@jupyterlab/apputils', () => ({
  showDialog: jest.fn(),
  Dialog: {
   okButton: jest.fn(),
    cancelButton: jest.fn()
  }
}));

jest.mock('../serverRequests', () => ({
  getNotebookInfo: jest.fn(),
}));

describe('handleErrorsProducedByNotebookCell', () => {
  const failingCellId = '1234-abcd-5678';
  let docManager: IDocumentManager;

  beforeEach(() => {
    docManager = {
      openOrReveal: jest.fn(),
    } as unknown as IDocumentManager;
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should return false if no failing cell ID is found', async () => {
    let message = new VdkErrorMessage('');
    message.what_happened = '';
    const result = await handleErrorsProducedByNotebookCell(
      message,
      docManager
    );
    expect(result).toBe(false);
  });

  it('should return true if failing cell ID is found', async () => {
    let message = new VdkErrorMessage('');
    message.exception_message = 'Exception message';
    message.what_happened= `An error occurred in cell_id:${failingCellId}`;
    message.why_it_happened = 'Why it happened';
    message.consequences = 'Consequences';
    message.countermeasures = 'Countermeasures';

    (getNotebookInfo as jest.Mock).mockResolvedValueOnce({
      path: '/path/to/notebook.ipynb',
      cellIndex: '0',
    });
    const showDialogMock = showDialog as jest.MockedFunction<typeof showDialog>;
    const acceptResult = { button: { accept: true } };
    (showDialogMock as jest.Mock).mockResolvedValueOnce(acceptResult);

    const result = await handleErrorsProducedByNotebookCell(
      message,
      docManager
    );

    expect(docManager.openOrReveal).toHaveBeenCalledWith('/path/to/notebook.ipynb');
    expect(result).toBe(true);
  });

});

describe('getCellInputAreaPrompt', () => {
  test('returns the prompt element when it exists', () => {
    const mockPromptElement = document.createElement('div');
    mockPromptElement.classList.add('jp-InputArea-prompt');

    const mockCellInputArea = document.createElement('div');
    mockCellInputArea.classList.add('jp-Cell-inputArea');
    mockCellInputArea.appendChild(mockPromptElement);

    const mockCellInputWrapper = document.createElement('div');
    mockCellInputWrapper.classList.add('jp-Cell-inputWrapper');
    mockCellInputWrapper.appendChild(mockCellInputArea);

    const mockFailingCell = document.createElement('div');
    mockFailingCell.appendChild(mockCellInputWrapper);

    const result = getCellInputAreaPrompt(mockFailingCell);

    expect(result).toBe(mockPromptElement);
  });

  test('returns undefined when prompt element does not exist', () => {
    const mockCellInputArea = document.createElement('div');
    mockCellInputArea.classList.add('jp-Cell-inputArea');

    const mockCellInputWrapper = document.createElement('div');
    mockCellInputWrapper.classList.add('jp-Cell-inputWrapper');
    mockCellInputWrapper.appendChild(mockCellInputArea);

    const mockFailingCell = document.createElement('div');
    mockFailingCell.appendChild(mockCellInputWrapper);

    const result = getCellInputAreaPrompt(mockFailingCell);

    expect(result).toBeUndefined();
  });
});
