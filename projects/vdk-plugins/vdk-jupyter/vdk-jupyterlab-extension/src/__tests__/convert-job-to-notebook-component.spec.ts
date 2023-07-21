/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */
import ConvertJobToNotebookDialog from '../components/ConvertJobToNotebook';
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
