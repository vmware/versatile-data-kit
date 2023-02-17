/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';
import { HttpClient } from '@angular/common/http';

import { of } from 'rxjs';

import { ApolloQueryResult } from '@apollo/client/core';

import { DATA_PIPELINES_CONFIGS, DataJob, DataJobPage } from '../model';

import { DataJobsBaseApiService } from './data-jobs-base.api.service';

import { DataJobsApiService, MISSING_DEFAULT_TEAM_MESSAGE, RESERVED_DEFAULT_TEAM_NAME_MESSAGE } from './data-jobs.api.service';

describe('DataJobsApiService', () => {
    let service: DataJobsApiService;
    let dataJobsBaseServiceStub: jasmine.SpyObj<DataJobsBaseApiService>;
    let httpClientStub: jasmine.SpyObj<HttpClient>;

    const TEST_JOB_DETAILS = {
        /* eslint-disable-next-line @typescript-eslint/naming-convention */
        job_name: 'job001',
        team: 'taurus',
        description: 'descpription001'
    };

    beforeEach(() => {
        dataJobsBaseServiceStub = jasmine.createSpyObj<DataJobsBaseApiService>('dataJobsBaseService', ['getJobs']);
        httpClientStub = jasmine.createSpyObj<HttpClient>('httpClient', ['get', 'post', 'patch', 'put', 'delete']);

        httpClientStub.get.and.returnValue(of({}));
        httpClientStub.post.and.returnValue(of({}));
        httpClientStub.patch.and.returnValue(of({}));
        httpClientStub.put.and.returnValue(of({}));
        httpClientStub.delete.and.returnValue(of({}));

        TestBed.configureTestingModule({
            providers: [
                DataJobsApiService,
                { provide: HttpClient, useValue: httpClientStub },
                { provide: DataJobsBaseApiService, useValue: dataJobsBaseServiceStub },
                {
                    provide: DATA_PIPELINES_CONFIGS,
                    useFactory: () => ({
                        defaultOwnerTeamName: 'all'
                    })
                }
            ]
        });

        service = TestBed.inject(DataJobsApiService);
    });

    it('can load instance', () => {
        expect(service).toBeTruthy();
    });

    describe('Methods::', () => {
        describe('|getJobs|', () => {
            it('should verify will make expected calls', () => {
                // Given
                const apolloQueryResult: ApolloQueryResult<DataJobPage> = {
                    data: {
                        content: [{}],
                        totalItems: 1,
                        totalPages: 1
                    },
                    loading: false,
                    networkStatus: 7
                };
                const apolloQueryRef = of(apolloQueryResult);

                dataJobsBaseServiceStub.getJobs.and.returnValue(apolloQueryRef);

                // When
                service.getJobs([], 'searchQueryValue', 1, 1);

                // Then
                expect(dataJobsBaseServiceStub.getJobs).toHaveBeenCalledWith(
                    'all',
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
                        pageNumber: 1,
                        pageSize: 1,
                        filter: [],
                        search: 'searchQueryValue'
                    }
                );
            });
        });

        describe('|getJobListState|', () => {
            it('should verify will make expected calls', () => {
                // Given
                const apolloQueryResult: ApolloQueryResult<DataJobPage> = {
                    data: {
                        content: [{}],
                        totalItems: 1,
                        totalPages: 1
                    },
                    loading: false,
                    networkStatus: 7
                };
                dataJobsBaseServiceStub.getJobs.and.returnValue(of(apolloQueryResult));

                // When
                service.getJob('supercollider_demo', 'test-job-taur');

                // Then
                expect(dataJobsBaseServiceStub.getJobs).toHaveBeenCalledWith(
                    'supercollider_demo',
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
                        filter: [
                            { property: 'config.team', pattern: 'supercollider_demo', sort: null },
                            { property: 'jobName', pattern: 'test-job-taur', sort: null }
                        ]
                    }
                );
            });

            it('should verify will return expected data for given response', (done) => {
                // Given
                const dataJob: DataJob = {};
                const apolloQueryResult1: ApolloQueryResult<DataJobPage> = undefined;
                const apolloQueryResult2: ApolloQueryResult<DataJobPage> = {
                    data: undefined,
                    loading: false,
                    networkStatus: 7
                };
                const apolloQueryResult3: ApolloQueryResult<DataJobPage> = {
                    data: {
                        content: undefined
                    },
                    loading: false,
                    networkStatus: 7
                };
                const apolloQueryResult4: ApolloQueryResult<DataJobPage> = {
                    data: {
                        content: []
                    },
                    loading: false,
                    networkStatus: 7
                };
                const apolloQueryResult5: ApolloQueryResult<DataJobPage> = {
                    data: {
                        content: [dataJob],
                        totalItems: 1,
                        totalPages: 1
                    },
                    loading: false,
                    networkStatus: 7
                };
                dataJobsBaseServiceStub.getJobs.and.returnValues(
                    of(apolloQueryResult1),
                    of(apolloQueryResult2),
                    of(apolloQueryResult3),
                    of(apolloQueryResult4),
                    of(apolloQueryResult5)
                );

                const executeNextCall = (executionId) => {
                    if (executionId === 4) {
                        service.getJob('supercollider_demo', 'test-job-taur')
                               .subscribe((value) => {
                                   expect(value).toBe(dataJob);
                                   done();
                               });
                    } else {
                        service.getJob('supercollider_demo', 'test-job-taur')
                               .subscribe((value) => {
                                   expect(value).toBeNull();
                                   executeNextCall(++executionId);
                               });
                    }
                };

                // When/Then
                executeNextCall(0);
            });
        });

        describe('|getJobExecution|', () => {
            it('should verify will make expected calls', () => {
                // Given
                const teamName = 'teamA';
                const jobName = 'jobA';
                const executionId = 'executionA';

                // When
                const response = service.getJobExecution(teamName, jobName, executionId);

                // Then
                expect(response).toBeDefined();
                expect(httpClientStub.get).toHaveBeenCalledWith(
                    `/data-jobs/for-team/${ teamName }/jobs/${ jobName }/executions/${ executionId }`
                );
            });
        });
    });

    describe('validateModuleConfig', () => {
        it('validates dataPipelinesModuleConfig with empty defaultOwnerTeamName', () => {
            // @ts-ignore
            expect(() => service._validateModuleConfig({
                defaultOwnerTeamName: ''
            })).toThrow(new Error(MISSING_DEFAULT_TEAM_MESSAGE));
        });

        it('validates dataPipelinesModuleConfig with reserved defaultOwnerTeamName', () => {
            // @ts-ignore
            expect(() => service._validateModuleConfig({
                defaultOwnerTeamName: 'default'
            })).toThrow(new Error(RESERVED_DEFAULT_TEAM_NAME_MESSAGE));
        });
    });

    describe('getJobDetails', () => {
        it('returs observable', () => {
            const jobDetailsObservable = service.getJobDetails('team001', 'job001');
            expect(jobDetailsObservable).toBeDefined();
        });
    });

    describe('removeJob', () => {
        it('returs observable', () => {
            const removeJobObservable = service.removeJob('team001', 'job001');
            expect(removeJobObservable).toBeDefined();
        });
    });

    describe('downloadFile', () => {
        it('returs observable', () => {
            const downloadFileObservable = service.downloadFile('team001', 'job001');
            expect(downloadFileObservable).toBeDefined();
        });
    });

    describe('getJobDeployments', () => {
        it('returs observable', () => {
            const getJobDeploymentsObservable = service.getJobDeployments('team001', 'job001');
            expect(getJobDeploymentsObservable).toBeDefined();
        });
    });

    describe('updateDataJobStatus', () => {
        it('returs observable', () => {
            const updateDataJobStatusObservable = service.updateDataJobStatus('team001', 'job001', 'deploy001', false);
            expect(updateDataJobStatusObservable).toBeDefined();
        });
    });

    describe('updateDataJobStatus', () => {
        it('returs observable', () => {
            const updateDataJobStatusObservable = service.updateDataJobStatus('team001', 'job001', null, false);
            expect(updateDataJobStatusObservable).toBeDefined();
        });
    });

    describe('updateDataJob', () => {
        it('returs observable', () => {
            const updateDataJobStatusObservable = service.updateDataJob('team001', 'job001', TEST_JOB_DETAILS);
            expect(updateDataJobStatusObservable).toBeDefined();
        });
    });

    describe('getJobExecutions', () => {
        it('returs observable', () => {
            const jobExecutionsObservable = service.getJobExecutions('team001', 'job001');
            expect(jobExecutionsObservable).toBeDefined();
        });
    });

    describe('executeDataJob', () => {
        it('returns observable', () => {
            const teamName = 'team001';
            const jobName = 'job001';
            const deploymentId = 'hhw-dff-fgg-100';

            const executeDataJobObservable = service.executeDataJob(teamName, jobName, deploymentId);
            expect(executeDataJobObservable).toBeDefined();
            expect(httpClientStub.post)
                .toHaveBeenCalledWith(`/data-jobs/for-team/${ teamName }/jobs/${ jobName }/deployments/${ deploymentId }/executions`, {})

        });
    });

    describe('cancelDataJob', () => {
        it('returns observable', () => {

            const teamName = 'team001';
            const jobName = 'job001';
            const deploymentId = 'hhw-dff-fgg-100';
            const executionId = 'hhw-dff-fgg-100';

            const executeDataJobObservable = service.executeDataJob(teamName, jobName, deploymentId);
            expect(executeDataJobObservable).toBeDefined();
            expect(httpClientStub.post)
                .toHaveBeenCalledWith(`/data-jobs/for-team/${ teamName }/jobs/${ jobName }/deployments/${ deploymentId }/executions`, {})

            const cancelExecutionDataJobObservable = service.cancelDataJobExecution(teamName, jobName, executionId);
            expect(cancelExecutionDataJobObservable).toBeDefined();
            expect(httpClientStub.delete)
                .toHaveBeenCalledWith(`/data-jobs/for-team/${ teamName }/jobs/${ jobName }/executions/${ executionId }`)

        });
    });
});
