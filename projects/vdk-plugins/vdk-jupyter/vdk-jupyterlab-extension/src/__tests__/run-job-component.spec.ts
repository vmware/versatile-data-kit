/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */
import RunJobDialog, { IRunJobDialogProps } from '../components/RunJob';
import { render, fireEvent } from '@testing-library/react';
import { jobData } from '../jobData';
import { VdkOption } from '../vdkOptions/vdk_options';

const defaultProps: IRunJobDialogProps = {
  jobPath: 'test-path'
};

describe('#constructor()', () => {
  it('should return a new instance', () => {
    const box = new RunJobDialog(defaultProps);
    expect(box).toBeInstanceOf(RunJobDialog);
  });
});

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
