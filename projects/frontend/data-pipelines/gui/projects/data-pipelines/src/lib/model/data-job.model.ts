/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/naming-convention */

import { ApiPredicate } from '@vdk/shared';

import { DataJobContacts, DataJobSchedule, GraphQLResponsePage } from './data-job-base.model';

import { DataJobDeployment } from './data-job-deployments.model';

export type DataJobPage = GraphQLResponsePage<DataJob>;

export interface DataJob {
    jobName?: string;
    config?: DataJobConfig;
    deployments?: DataJobDeployment[];
}

export interface DataJobConfig {
    team?: string;
    description?: string;
    generateKeytab?: boolean;
    sourceUrl?: string;
    logsUrl?: string;
    schedule?: DataJobSchedule;
    contacts?: DataJobContacts;
}

/**
 * ** Request variables for DataJobs jobsQuery GraphQL API.
 */
export interface DataJobReqVariables {
    pageNumber?: number;
    pageSize?: number;
    filter?: ApiPredicate[];
    search?: string;
}

export enum DataJobStatus {
    ENABLED = 'Enabled',
    DISABLED = 'Disabled',
    NOT_DEPLOYED = 'Not Deployed'
}
