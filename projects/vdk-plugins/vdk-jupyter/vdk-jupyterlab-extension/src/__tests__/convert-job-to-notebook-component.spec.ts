/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */
import ConvertJobToNotebookDialog, {
  initializeNotebookContent
} from '../components/ConvertJobToNotebook';
import { render, fireEvent } from '@testing-library/react';
import { jobData } from '../jobData';
import { VdkOption } from '../vdkOptions/vdk_options';
import { IJobPathProp } from '../components/props';

const defaultProps: IJobPathProp = {
  jobPath: 'test-path'
};

// created with the expectation to compare a rendered value with expected value parsed from config.ini
// yet to be implemented
describe('#render()', () => {
  it('should return contain job path input with placeholder equal to jobPath from props', () => {
    const component = render(
      new ConvertJobToNotebookDialog(defaultProps).render()
    );
    const input = component.getByPlaceholderText(defaultProps.jobPath);
    expect(input).toBe(
      component.getAllByLabelText('Path to job directory:')[0]
    );
  });
});

describe('#onPathChange', () => {
  it('should change the path in jobData', () => {
    const component = render(
      new ConvertJobToNotebookDialog(defaultProps).render()
    );
    const input = component.getByPlaceholderText(defaultProps.jobPath);
    fireEvent.change(input, { target: { value: 'other/path' } });
    expect(jobData.get(VdkOption.PATH)).toEqual('other/path');
  });
});

describe('initializeNotebookContent', () => {
  it('should create a notebook content correctly', () => {
    const codeStructure = [
      'def run(job_input: IJobInput)',
      'print("Hello, world!")'
    ];
    const fileNames = ['file1', 'file2'];

    const expectedNotebookContent = [
      { source: '#### file1', type: 'markdown' },
      { source: codeStructure[0], type: 'code' },
      { source: 'run(job_input)', type: 'code' },
      { source: '#### file2', type: 'markdown' },
      { source: codeStructure[1], type: 'code' }
    ];

    const result = initializeNotebookContent(codeStructure, fileNames);
    expect(result).toEqual(expectedNotebookContent);
  });

  it('should not add a run cell when there is no run function', () => {
    const codeStructure = ['print("Hello, world!")'];
    const fileNames = ['file1'];

    const expectedNotebookContent = [
      { source: '#### file1', type: 'markdown' },
      { source: codeStructure[0], type: 'code' }
    ];

    const result = initializeNotebookContent(codeStructure, fileNames);
    expect(result).toEqual(expectedNotebookContent);
  });

  it('should return an empty array when codeStructure and fileNames are empty', () => {
    const codeStructure: string[] = [];
    const fileNames: string[] = [];

    const result = initializeNotebookContent(codeStructure, fileNames);
    expect(result).toEqual([]);
  });

  it('should add a run cell for each run function in codeStructure', () => {
    const codeStructure = [
      'def run(job_input: IJobInput)',
      'def run(job_input: IJobInput)'
    ];
    const fileNames = ['file1', 'file2'];

    const expectedNotebookContent = [
      { source: '#### file1', type: 'markdown' },
      { source: codeStructure[0], type: 'code' },
      { source: 'run(job_input)', type: 'code' },
      { source: '#### file2', type: 'markdown' },
      { source: codeStructure[1], type: 'code' },
      { source: 'run(job_input)', type: 'code' }
    ];

    const result = initializeNotebookContent(codeStructure, fileNames);
    expect(result).toEqual(expectedNotebookContent);
  });
});
