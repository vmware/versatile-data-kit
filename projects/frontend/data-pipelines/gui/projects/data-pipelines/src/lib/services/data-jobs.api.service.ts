/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Inject, Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { ApolloQueryResult } from '@apollo/client/core';

import {
    ApiPredicate,
    CollectionsUtil,
    TaurusBaseApiService,
} from '@versatiledatakit/shared';

import {
    DATA_PIPELINES_CONFIGS,
    DataJob,
    DataJobDeploymentDetails,
    DataJobDetails,
    DataJobExecutionDetails,
    DataJobExecutionFilter,
    DataJobExecutionOrder,
    DataJobExecutionsPage,
    DataJobPage,
    DataPipelinesConfig,
} from '../model';

import { DataJobsBaseApiService } from './data-jobs-base.api.service';

export const MISSING_DEFAULT_TEAM_MESSAGE =
    'The defaultOwnerTeamName property need to be set for the DATA_PIPELINES_CONFIGS';

export const RESERVED_DEFAULT_TEAM_NAME_MESSAGE = `The 'default' value is reserved, and can not be used for defaultOwnerTeamName property`;

@Injectable()
export class DataJobsApiService extends TaurusBaseApiService<DataJobsApiService> {
    /**
     * @inheritDoc
     */
    static override readonly CLASS_NAME: string = 'DataJobsApiService';

    /**
     * @inheritDoc
     */
    static override readonly PUBLIC_NAME: string = 'Data-Pipelines-Service';

    ownerTeamName: string;

    constructor(
        @Inject(DATA_PIPELINES_CONFIGS)
        dataPipelinesModuleConfig: DataPipelinesConfig,
        private readonly http: HttpClient,
        private readonly dataJobsBaseService: DataJobsBaseApiService,
    ) {
        super(DataJobsApiService.CLASS_NAME);

        this.registerErrorCodes(DataJobsApiService);

        this._validateModuleConfig(dataPipelinesModuleConfig);

        this.ownerTeamName = dataPipelinesModuleConfig?.defaultOwnerTeamName;
        if (dataPipelinesModuleConfig?.ownerTeamNamesObservable) {
            dataPipelinesModuleConfig.ownerTeamNamesObservable.subscribe(
                (result: string[]) => {
                    if (result?.length) {
                        //Take the first element from the teams array
                        this.ownerTeamName = result[0];
                    }
                },
            );
        }
    }

    getJobs(
        filters: ApiPredicate[],
        searchQueryValue: string,
        pageNumber: number,
        pageSize: number,
    ): Observable<ApolloQueryResult<DataJobPage>> {
        return this.dataJobsBaseService.getJobs(
            this.ownerTeamName,
            `query jobsQuery($filter: [Predicate], $search: String, $pageNumber: Int, $pageSize: Int)
              {
                jobs(pageNumber: $pageNumber, pageSize: $pageSize, filter: $filter, search: $search) {
                  content {
                    jobName
                    config {
                      team
                      description
                      sourceUrl
                      schedule {
                        scheduleCron
                        nextRunEpochSeconds
                      }
                      contacts {
                        notifiedOnJobSuccess
                        notifiedOnJobDeploy
                        notifiedOnJobFailureUserError
                        notifiedOnJobFailurePlatformError
                      }
                    }
                    deployments {
                      id
                      enabled
                      lastDeployedDate
                      lastDeployedBy
                      lastExecutionStatus
                      lastExecutionTime
                      lastExecutionDuration
                      successfulExecutions
                      failedExecutions
                      executions(pageNumber: 1, pageSize: 10, order: { property: "startTime", direction: DESC }) {
						id
                        status
                        logsUrl
                      }
                    }
                  }
                  totalPages
                  totalItems
                }
              }`,
            {
                pageNumber,
                pageSize,
                filter: filters,
                search: searchQueryValue,
            },
        );
    }

    getJob(teamName: string, jobName: string): Observable<DataJob> {
        return this.dataJobsBaseService
            .getJobs(
                teamName,
                `query jobsQuery($filter: [Predicate])
              {
                jobs(pageNumber: 1, pageSize: 1, filter: $filter) {
                  content {
                    jobName
                    config {
                      team
                      description
                      sourceUrl
                      schedule {
                        scheduleCron
                        nextRunEpochSeconds
                      }
                      contacts {
                        notifiedOnJobSuccess
                        notifiedOnJobDeploy
                        notifiedOnJobFailureUserError
                        notifiedOnJobFailurePlatformError
                      }
                    }
                    deployments {
                      id
                      enabled
                      executions(pageNumber: 1, pageSize: 10, order: { property: "startTime", direction: DESC }) {
                        id
                        status
                        logsUrl
                        startedBy
                        startTime
                        endTime
                      }
                    }
                  }
                  totalPages
                  totalItems
                }
              }`,
                {
                    filter: this._createTeamJobNameFilter(teamName, jobName),
                },
            )
            .pipe(
                map((response: ApolloQueryResult<DataJobPage>) => {
                    if (
                        !CollectionsUtil.isArray(response?.data?.content) ||
                        response.data.content.length === 0
                    ) {
                        return null;
                    }

                    return response.data.content[0];
                }),
            );
    }

    getJobDetails(
        teamName: string,
        jobName: string,
    ): Observable<DataJobDetails> {
        return this.http.get<DataJobDetails>(
            `/data-jobs/for-team/${teamName}/jobs/${jobName}`,
        );
    }

    removeJob(teamName: string, jobName: string): Observable<DataJobDetails> {
        return this.http.delete(
            `/data-jobs/for-team/${teamName}/jobs/${jobName}`,
        );
    }

    downloadFile(teamName: string, jobName: string): Observable<Blob> {
        const httpHeaders = new HttpHeaders();
        httpHeaders.append('Accept', 'application/octet-stream');

        return this.http.get(
            `/data-jobs/for-team/${teamName}/jobs/${jobName}/keytab`,
            {
                headers: httpHeaders,
                responseType: 'blob',
            },
        );
    }

    getJobExecutions(
        teamName: string,
        jobName: string,
    ): Observable<DataJobExecutionDetails[]>;
    getJobExecutions(
        teamName: string,
        jobName: string,
        forceGraphQL: boolean,
        filter?: DataJobExecutionFilter,
        order?: DataJobExecutionOrder,
        pageNumber?: number,
        pageSize?: number,
    ): Observable<DataJobExecutionsPage>;
    getJobExecutions(
        teamName: string,
        jobName: string,
        forceGraphQL = false,
        filter: DataJobExecutionFilter = null,
        order: DataJobExecutionOrder = null,
        pageNumber: number = null,
        pageSize: number = null,
    ):
        | Observable<DataJobExecutionDetails[]>
        | Observable<DataJobExecutionsPage> {
        if (!forceGraphQL) {
            return this.http.get<DataJobExecutionDetails[]>(
                `/data-jobs/for-team/${teamName}/jobs/${jobName}/executions`,
            );
        }

        const preparedFilter = { ...(filter ?? {}) };

        if (jobName.length > 0) {
            if (CollectionsUtil.isArray(preparedFilter.jobNameIn)) {
                preparedFilter.jobNameIn.push(jobName);
            } else {
                preparedFilter.jobNameIn = [jobName];
            }
        }

        return this.dataJobsBaseService
            .getExecutions(
                teamName,
                `query jobsQuery($pageNumber: Int, $pageSize: Int, $filter: DataJobExecutionFilter, $order: DataJobExecutionOrder)
              {
                executions(pageNumber: $pageNumber, pageSize: $pageSize, filter: $filter, order: $order) {
                  content {
                    id
                    type
                    jobName
                    status
                    startTime
                    endTime
                    startedBy
                    message
                    opId
                    logsUrl
                    deployment {
                      enabled
                      jobVersion
                      deployedDate
                      deployedBy
                      resources {
                        cpuLimit
                        cpuRequest
                        memoryLimit
                        memoryRequest
                      }
                      schedule {
                        scheduleCron
                      }
                      vdkVersion
                      status
                    }
                  }
                  totalPages
                  totalItems
                }
              }`,
                {
                    pageNumber: pageNumber ?? 1,
                    pageSize: pageSize ?? 500,
                    filter: preparedFilter,
                    order: order ?? null,
                },
            )
            .pipe(map((response) => response.data));
    }

    getJobExecution(
        teamName: string,
        jobName: string,
        executionId: string,
    ): Observable<DataJobExecutionDetails> {
        return this.http.get<DataJobExecutionDetails>(
            `/data-jobs/for-team/${teamName}/jobs/${jobName}/executions/${executionId}`,
        );
    }

    getJobDeployments(
        teamName: string,
        jobName: string,
    ): Observable<DataJobDeploymentDetails[]> {
        return this.http.get<DataJobDeploymentDetails[]>(
            `/data-jobs/for-team/${teamName}/jobs/${jobName}/deployments`,
        );
    }

    updateDataJobStatus(
        teamName: string,
        jobName: string,
        deploymentId: string,
        dataJobEnabled: boolean,
    ): Observable<{ enabled: boolean }> {
        const deploymentStatus = { enabled: dataJobEnabled };

        if (!deploymentId) {
            console.log(
                `Status update will be processed with default deploymentId`,
            );
            deploymentId = 'default';
        }

        return this.http.patch<{ enabled: boolean }>(
            `/data-jobs/for-team/${teamName}/jobs/${jobName}/deployments/${deploymentId}`,
            deploymentStatus,
        );
    }

    updateDataJob(
        teamName: string,
        jobName: string,
        dataJob: DataJobDetails,
    ): Observable<DataJobDetails> {
        return this.http.put<DataJobDetails>(
            `/data-jobs/for-team/${teamName}/jobs/${jobName}`,
            dataJob,
        );
    }

    executeDataJob(
        teamName: string,
        jobName: string,
        deploymentId: string,
    ): Observable<undefined> {
        return this.http.post<undefined>(
            `/data-jobs/for-team/${teamName}/jobs/${jobName}/deployments/${deploymentId}/executions`,
            {},
        );
    }

    cancelDataJobExecution(
        teamName: string,
        jobName: string,
        executionId: string,
    ): Observable<any> {
        return this.http.delete(
            `/data-jobs/for-team/${teamName}/jobs/${jobName}/executions/${executionId}`,
        );
    }

    private _createTeamJobNameFilter(teamName: string, jobName: string) {
        return [
            { property: 'config.team', pattern: teamName, sort: null },
            { property: 'jobName', pattern: jobName, sort: null },
        ];
    }

    private _validateModuleConfig(
        dataPipelinesModuleConfig: DataPipelinesConfig,
    ) {
        if (!dataPipelinesModuleConfig?.defaultOwnerTeamName) {
            throw new Error(MISSING_DEFAULT_TEAM_MESSAGE);
        }

        if (dataPipelinesModuleConfig?.defaultOwnerTeamName === 'default') {
            throw new Error(RESERVED_DEFAULT_TEAM_NAME_MESSAGE);
        }
    }
}
