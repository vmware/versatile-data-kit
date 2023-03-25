/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */
import DeleteJobDialog from '../components/DeleteJob';
import { render, fireEvent } from '@testing-library/react';
import { jobData } from '../jobData';
import { VdkOption } from '../vdkOptions/vdk_options';
import { IJobNameAndTeamProps } from '../components/props';

const defaultProps: IJobNameAndTeamProps = {
  jobName: 'test-name',
  jobTeam: 'test-team'
};

// created with the expectation to compare a rendered value with expected value parsed from config.ini
// yet to be implemented
describe('#render()', () => {
  it('should return contain job name input with placeholder equal to jobName from props', () => {
    const component = render(new DeleteJobDialog(defaultProps).render());
    const input = component.getByPlaceholderText(defaultProps.jobName);
    expect(input).toBe(component.getAllByLabelText('Job Name:')[0]);
  });

  it('should return contain job team input with placeholder equal to jobTeam from props', () => {
    const component = render(new DeleteJobDialog(defaultProps).render());
    const input = component.getByPlaceholderText(defaultProps.jobTeam);
    expect(input).toBe(component.getAllByLabelText('Job Team:')[0]);
  });
});

describe('#onNameChange', () => {
  it('should change the job name in jobData', () => {
    const component = render(new DeleteJobDialog(defaultProps).render());
    const input = component.getByPlaceholderText(defaultProps.jobName);
    fireEvent.change(input, { target: { value: 'second-name' } });
    expect(jobData.get(VdkOption.NAME)).toEqual('second-name');
  });
});

describe('#onTeamChange', () => {
  it('should change the job team in jobData', () => {
    const component = render(new DeleteJobDialog(defaultProps).render());
    const input = component.getByPlaceholderText(defaultProps.jobTeam);
    fireEvent.change(input, { target: { value: 'second-team' } });
    expect(jobData.get(VdkOption.TEAM)).toEqual('second-team');
  });
});

describe('#onRestApiUrlChange', () => {
  it('should change the rest api url in jobData', () => {
    const component = render(new DeleteJobDialog(defaultProps).render());
    const input = component.getByPlaceholderText('http://my_vdk_instance');
    fireEvent.change(input, { target: { value: 'random-url' } });
    expect(jobData.get(VdkOption.REST_API_URL)).toEqual('random-url');
  });
});
