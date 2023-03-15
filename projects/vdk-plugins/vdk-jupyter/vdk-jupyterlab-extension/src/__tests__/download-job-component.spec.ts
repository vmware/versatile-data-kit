/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */
import DownloadJobDialog, {
  IDownloadJobDialogProps
} from '../components/DownloadJob';
import { render, fireEvent } from '@testing-library/react';
import { jobData } from '../jobData';
import { VdkOption } from '../vdkOptions/vdk_options';

const defaultProps: IDownloadJobDialogProps = {
  parentPath: 'test-path'
};

// created with the expectation to compare a rendered value with expected value parsed from config.ini
// yet to be implemented
describe('#render()', () => {
  it('should return contain job name input with placeholder equal to jobName from props', () => {
    const component = render(new DownloadJobDialog(defaultProps).render());
    const input = component.getByPlaceholderText('default-name');
    expect(input).toBe(component.getAllByLabelText('Job Name:')[0]);
  });

  it('should return contain job team input with placeholder equal to jobTeam from props', () => {
    const component = render(new DownloadJobDialog(defaultProps).render());
    const input = component.getByPlaceholderText('default-team');
    expect(input).toBe(component.getAllByLabelText('Job Team:')[0]);
  });

  it('should return contain job path input with placeholder equal to jobPath from props', () => {
    const component = render(new DownloadJobDialog(defaultProps).render());
    const input = component.getByPlaceholderText(defaultProps.parentPath);
    expect(input).toBe(
      component.getAllByLabelText('Path to job directory:')[0]
    );
  });
});

describe('#onNameChange', () => {
  it('should change the job name in jobData', () => {
    const component = render(new DownloadJobDialog(defaultProps).render());
    const input = component.getByPlaceholderText('default-name');
    fireEvent.change(input, { target: { value: 'second-name' } });
    expect(jobData.get(VdkOption.NAME)).toEqual('second-name');
  });
});

describe('#onTeamChange', () => {
  it('should change the job team in jobData', () => {
    const component = render(new DownloadJobDialog(defaultProps).render());
    const input = component.getByPlaceholderText('default-team');
    fireEvent.change(input, { target: { value: 'second-team' } });
    expect(jobData.get(VdkOption.TEAM)).toEqual('second-team');
  });
});

describe('#onRestApiUrlChange', () => {
  it('should change the rest api url in jobData', () => {
    const component = render(new DownloadJobDialog(defaultProps).render());
    const input = component.getByPlaceholderText('http://my_vdk_instance');
    fireEvent.change(input, { target: { value: 'random-url' } });
    expect(jobData.get(VdkOption.REST_API_URL)).toEqual('random-url');
  });
});

describe('#onPathChange', () => {
  it('should change the path in jobData', () => {
    const component = render(new DownloadJobDialog(defaultProps).render());
    const input = component.getByPlaceholderText(defaultProps.parentPath);
    fireEvent.change(input, { target: { value: 'other/path' } });
    expect(jobData.get(VdkOption.PATH)).toEqual('other/path');
  });
});
