/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';
import { DataJobDeploymentDetails } from '../../model/data-job-details.model';
import { ExtractJobStatusPipe } from './extract-job-status.pipe';

const TEST_JOB_DEPLOYMENT_DETAILS: DataJobDeploymentDetails = {
    id: 'id002',
    enabled: true,
    /* eslint-disable-next-line @typescript-eslint/naming-convention */
    job_version: 'v001',
    mode: 'special',
    /* eslint-disable-next-line @typescript-eslint/naming-convention */
    vdk_version: 'v002',
    contacts: null,
    /* eslint-disable @typescript-eslint/naming-convention */
    deployed_date: '2020-11-11T10:10:10Z',
    deployed_by: 'pmitev',
    resources: {
        memory_limit: 1000,
        memory_request: 1000,
        cpu_limit: 0.5,
        cpu_request: 0.5,
    },
    /* eslint-enable @typescript-eslint/naming-convention */
};

describe('ExtractJobStatusPipe', () => {
    let pipe: ExtractJobStatusPipe;
    let deploymentDetails: DataJobDeploymentDetails;

    beforeEach(() => {
        TestBed.configureTestingModule({ providers: [ExtractJobStatusPipe] });
        pipe = TestBed.inject(ExtractJobStatusPipe);
        deploymentDetails = TEST_JOB_DEPLOYMENT_DETAILS;
    });

    it('can instantiate ExtractJobStatusPipe', () => {
        expect(pipe).toBeTruthy();
    });

    it('transforms empty deploymentDetails to NOT_DEPLOYED', () => {
        expect(pipe.transform([])).toEqual('Not Deployed');
    });

    it('transforms disabled deploymentDetails to DISABLED', () => {
        deploymentDetails.enabled = false;

        const jobDeployments = [deploymentDetails];
        expect(pipe.transform(jobDeployments)).toEqual('Disabled');
    });

    it('transforms enabled deploymentDetails to DISABLED', () => {
        deploymentDetails.enabled = true;

        const jobExecutions = [deploymentDetails];
        expect(pipe.transform(jobExecutions)).toEqual('Enabled');
    });
});
