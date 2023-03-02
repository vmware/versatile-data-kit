/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';

import { forkJoin, of, Subject } from 'rxjs';

import { ApolloQueryResult } from '@apollo/client/core';

import { ApiPredicate } from '@versatiledatakit/shared';

import { DataJobPage } from '../model';

import { DataJobsBaseApiService } from './data-jobs-base.api.service';
import { DataJobsPublicApiService } from './data-jobs-public.api.service';

describe('DataJobsPublicApiService', () => {
    let dataJobsBaseServiceStub: jasmine.SpyObj<DataJobsBaseApiService>;

    let service: DataJobsPublicApiService;

    beforeEach(() => {
        dataJobsBaseServiceStub = jasmine.createSpyObj<DataJobsBaseApiService>(
            'dataJobsBaseServiceStub',
            ['getJobs']
        );
        dataJobsBaseServiceStub.getJobs.and.returnValue(
            new Subject<ApolloQueryResult<DataJobPage>>()
        );

        TestBed.configureTestingModule({
            providers: [
                DataJobsPublicApiService,
                {
                    provide: DataJobsBaseApiService,
                    useValue: dataJobsBaseServiceStub,
                },
            ],
        });
        service = TestBed.inject(DataJobsPublicApiService);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    describe('Methods::', () => {
        describe('|getAllDataJobs|', () => {
            it('should verify will make expected calls scenario 1', () => {
                // Given
                const apolloQueryResult: ApolloQueryResult<DataJobPage> = {
                    data: {
                        content: [{}],
                        totalItems: 1,
                        totalPages: 1,
                    },
                    loading: false,
                    networkStatus: 7,
                };
                const apolloQueryRef = of(apolloQueryResult);

                dataJobsBaseServiceStub.getJobs.and.returnValue(apolloQueryRef);

                // When
                service.getAllDataJobs('teamA').subscribe();

                // Then
                expect(dataJobsBaseServiceStub.getJobs).toHaveBeenCalledWith(
                    'teamA',
                    `query jobsQuery($filter: [Predicate], $search: String, $pageNumber: Int, $pageSize: Int)
						{
						  jobs(filter: $filter, search: $search, pageNumber: $pageNumber, pageSize: $pageSize) {
						    content {
						      jobName
						      config {
						        team
						        description
						        sourceUrl
						      }
						    }
						    totalPages
						    totalItems
						  }
						}`,
                    {
                        filter: [],
                        search: null,
                        pageNumber: 1,
                        pageSize: 1000,
                    }
                );
            });

            it('should verify will make expected calls scenario 2', (done) => {
                // Given
                const apolloQueryResult: ApolloQueryResult<DataJobPage> = {
                    data: {
                        content: [{}],
                        totalItems: 2500,
                        totalPages: 3,
                    },
                    loading: false,
                    networkStatus: 7,
                };
                const apolloQueryRef = of(apolloQueryResult);
                let counter = 0;

                dataJobsBaseServiceStub.getJobs.and.returnValue(apolloQueryRef);

                // When/Then
                service.getAllDataJobs('teamA').subscribe((value) => {
                    expect(
                        dataJobsBaseServiceStub.getJobs.calls.argsFor(counter)
                    ).toEqual([
                        'teamA',
                        `query jobsQuery($filter: [Predicate], $search: String, $pageNumber: Int, $pageSize: Int)
						{
						  jobs(filter: $filter, search: $search, pageNumber: $pageNumber, pageSize: $pageSize) {
						    content {
						      jobName
						      config {
						        team
						        description
						        sourceUrl
						      }
						    }
						    totalPages
						    totalItems
						  }
						}`,
                        {
                            filter: [],
                            search: null,
                            pageNumber: counter + 1,
                            pageSize: 1000,
                        },
                    ]);

                    counter++;

                    expect(value?.length).toEqual(counter);

                    if (counter === 3) {
                        done();
                    }
                });
            });
        });

        describe('|getDataJobsTotalForTeam|', () => {
            it('should verify will make expected calls', (done) => {
                // Given
                const apolloQueryResult: ApolloQueryResult<DataJobPage> = {
                    data: {
                        content: [{}, {}, {}, {}, {}],
                        totalItems: 5,
                        totalPages: 1,
                    },
                    loading: false,
                    networkStatus: 7,
                };
                const assertionFilters: ApiPredicate[] = [
                    {
                        property: 'config.team',
                        pattern: 'teamA',
                        sort: null,
                    },
                ];

                dataJobsBaseServiceStub.getJobs.and.returnValues(
                    of(apolloQueryResult),
                    // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
                    of(undefined),
                    of({
                        ...apolloQueryResult,
                        data: undefined,
                    }),
                    of({
                        ...apolloQueryResult,
                        data: {
                            ...apolloQueryResult.data,
                            totalItems: undefined,
                        },
                    })
                );

                // When/Then
                forkJoin([
                    service.getDataJobsTotal('teamA'),
                    service.getDataJobsTotal('teamA'),
                    service.getDataJobsTotal('teamA'),
                    service.getDataJobsTotal('teamA'),
                ]).subscribe(([value1, value2, value3, value4]) => {
                    expect(value1).toEqual(5);
                    expect(value2).toEqual(0);
                    expect(value3).toEqual(0);
                    expect(value4).toEqual(0);
                    expect(
                        dataJobsBaseServiceStub.getJobs
                    ).toHaveBeenCalledWith(
                        'teamA',
                        `query jobsQuery($filter: [Predicate], $search: String, $pageNumber: Int, $pageSize: Int)
						{
						  jobs(filter: $filter, search: $search, pageNumber: $pageNumber, pageSize: $pageSize) {
						    content {
						      jobName
						      config {
						        team
						      }
						    }
						    totalPages
						    totalItems
						  }
						}`,
                        {
                            filter: assertionFilters,
                            search: null,
                            pageNumber: 1,
                            pageSize: 1,
                        }
                    );

                    done();
                });
            });
        });
    });
});
