/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';

import { TestBed } from '@angular/core/testing';

import { of } from 'rxjs';

import { ApolloQueryResult, gql, InMemoryCache } from '@apollo/client/core';

import { Apollo, ApolloBase, QueryRef } from 'apollo-angular';
import { HttpLink, HttpLinkHandler } from 'apollo-angular/http';

import { ErrorHandlerService } from '@versatiledatakit/shared';

import {
    DataJobExecutionsPage,
    DataJobExecutionsReqVariables,
    DataJobPage,
    DataJobReqVariables,
} from '../model';

import { DataJobsBaseApiService } from './data-jobs-base.api.service';

describe('DataJobsBaseApiService', () => {
    let service: DataJobsBaseApiService;
    let apolloStub: jasmine.SpyObj<Apollo>;
    let httpLinkStub: jasmine.SpyObj<HttpLink>;
    let httpClientStub: jasmine.SpyObj<HttpClient>;
    let errorHandlerServiceStub: jasmine.SpyObj<ErrorHandlerService>;

    let apolloBaseStub: jasmine.SpyObj<ApolloBase>;

    beforeEach(() => {
        apolloStub = jasmine.createSpyObj<Apollo>('apolloService', [
            'use',
            'createNamed',
        ]);
        httpLinkStub = jasmine.createSpyObj<HttpLink>('httpLinkService', [
            'create',
        ]);
        httpClientStub = jasmine.createSpyObj<HttpClient>('httpClientService', [
            'request',
        ]);
        errorHandlerServiceStub = jasmine.createSpyObj<ErrorHandlerService>(
            'errorHandlerService',
            ['processError', 'handleError']
        );

        apolloBaseStub = jasmine.createSpyObj<ApolloBase>('apolloBase', [
            'query',
            'watchQuery',
        ]);

        TestBed.configureTestingModule({
            providers: [
                DataJobsBaseApiService,
                { provide: Apollo, useValue: apolloStub },
                { provide: HttpLink, useValue: httpLinkStub },
                { provide: HttpClient, useValue: httpClientStub },
                {
                    provide: ErrorHandlerService,
                    useValue: errorHandlerServiceStub,
                },
            ],
        });

        service = TestBed.inject(DataJobsBaseApiService);
    });

    it('should verify service instance is created', () => {
        // Then
        expect(service).toBeTruthy();
    });

    describe('Methods::', () => {
        describe('|getJobs|', () => {
            it('should verify will make expected calls', () => {
                // Given
                const gqlQuery = `query jobsQuery($filter: [Predicate], $search: String, $pageNumber: Int, $pageSize: Int)
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
                                }`;
                const ownerTeam = 'supercollider_test';
                const dataJobReqVariables: DataJobReqVariables = {
                    pageNumber: 2,
                    pageSize: 25,
                    filter: [],
                    search: 'sup',
                };
                const apolloLinkHandlerStub: HttpLinkHandler = {} as any;
                const apolloMockResponse: ApolloQueryResult<DataJobPage> = {
                    data: {
                        content: [],
                        totalItems: 25,
                        totalPages: 1,
                    },
                    networkStatus: 7,
                    loading: false,
                };

                apolloBaseStub.query.and.returnValue(of(apolloMockResponse));
                apolloStub.use.and.returnValues(null, apolloBaseStub);
                httpLinkStub.create.and.returnValue(apolloLinkHandlerStub);

                // When
                let dataJobPage: DataJobPage;
                service
                    .getJobs(ownerTeam, gqlQuery, dataJobReqVariables)
                    .subscribe((r) => (dataJobPage = r.data));

                // Then
                expect(apolloStub.use.calls.argsFor(0)).toEqual([ownerTeam]);
                expect(httpLinkStub.create).toHaveBeenCalledWith({
                    uri: `/data-jobs/for-team/${ownerTeam}/jobs`,
                    method: 'GET',
                });
                expect(apolloStub.createNamed.calls.argsFor(0)[0]).toEqual(
                    ownerTeam
                );
                expect(
                    apolloStub.createNamed.calls.argsFor(0)[1].cache
                ).toEqual(jasmine.any(InMemoryCache));
                expect(apolloStub.createNamed.calls.argsFor(0)[1].link).toBe(
                    apolloLinkHandlerStub
                );
                expect(
                    apolloStub.createNamed.calls.argsFor(0)[1].defaultOptions
                ).toEqual({
                    watchQuery: {
                        fetchPolicy: 'no-cache',
                        errorPolicy: 'all',
                    },
                    query: {
                        fetchPolicy: 'no-cache',
                        errorPolicy: 'all',
                    },
                });
                expect(apolloStub.use.calls.argsFor(1)).toEqual([ownerTeam]);
                expect(apolloBaseStub.query).toHaveBeenCalledWith({
                    query: gql`
                        ${gqlQuery}
                    `,
                    variables: dataJobReqVariables,
                });
                expect(dataJobPage).toBe(apolloMockResponse.data);
            });
        });

        describe('|watchForJobs|', () => {
            it('should verify will make expected calls', () => {
                // Given
                const gqlQuery = `query jobsQuery($filter: [Predicate], $search: String, $pageNumber: Int, $pageSize: Int)
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
                                }`;
                const ownerTeam = 'supercollider_test';
                const dataJobReqVariables: DataJobReqVariables = {
                    pageNumber: 2,
                    pageSize: 25,
                    filter: [],
                    search: 'sup',
                };
                const apolloLinkHandlerStub = {} as HttpLinkHandler;
                const apolloQueryResult: ApolloQueryResult<DataJobPage> = {
                    data: {
                        content: [],
                        totalItems: 25,
                        totalPages: 1,
                    },
                    networkStatus: 7,
                    loading: false,
                };
                const apolloMockResponse: QueryRef<
                    DataJobPage,
                    DataJobReqVariables
                > = {
                    valueChanges: of(apolloQueryResult),
                } as QueryRef<DataJobPage, DataJobReqVariables>;

                apolloBaseStub.watchQuery.and.returnValue(apolloMockResponse);
                apolloStub.use.and.returnValues(null, apolloBaseStub);
                httpLinkStub.create.and.returnValue(apolloLinkHandlerStub);

                // When
                let dataJobPage: DataJobPage;
                service
                    .watchForJobs(ownerTeam, gqlQuery, dataJobReqVariables)
                    .valueChanges.subscribe((r) => (dataJobPage = r.data));

                // Then
                expect(apolloStub.use.calls.argsFor(0)).toEqual([ownerTeam]);
                expect(httpLinkStub.create).toHaveBeenCalledWith({
                    uri: `/data-jobs/for-team/${ownerTeam}/jobs`,
                    method: 'GET',
                });
                expect(apolloStub.createNamed.calls.argsFor(0)[0]).toEqual(
                    ownerTeam
                );
                expect(
                    apolloStub.createNamed.calls.argsFor(0)[1].cache
                ).toEqual(jasmine.any(InMemoryCache));
                expect(apolloStub.createNamed.calls.argsFor(0)[1].link).toBe(
                    apolloLinkHandlerStub
                );
                expect(
                    apolloStub.createNamed.calls.argsFor(0)[1].defaultOptions
                ).toEqual({
                    watchQuery: {
                        fetchPolicy: 'no-cache',
                        errorPolicy: 'all',
                    },
                    query: {
                        fetchPolicy: 'no-cache',
                        errorPolicy: 'all',
                    },
                });
                expect(apolloStub.use.calls.argsFor(1)).toEqual([ownerTeam]);
                expect(apolloBaseStub.watchQuery).toHaveBeenCalledWith({
                    query: gql`
                        ${gqlQuery}
                    `,
                    variables: dataJobReqVariables,
                });
                expect(dataJobPage).toBe(apolloQueryResult.data);
            });
        });

        describe('|getExecutions|', () => {
            it('should verify will make expected calls', () => {
                // Given
                // eslint-disable-next-line max-len
                const gqlQuery = `query jobsQuery($pageNumber: Int, $pageSize: Int, $filter: DataJobExecutionFilter, $order: DataJobExecutionOrder)
                                {
                                  executions(pageNumber: $pageNumber, pageSize: $pageSize, filter: $filter, order: $order) {
                                    content {
                                      id
                                      type
                                      jobName
                                      status
                                      startTime
                                      deployment {
                                        enabled
                                        jobVersion
                                        resources {
                                          cpuLimit
                                          cpuRequest
                                        }
                                      }
                                    }
                                    totalPages
                                    totalItems
                                  }
                                }`;
                const ownerTeam = 'supercollider_test';
                const dataJobReqVariables: DataJobExecutionsReqVariables = {
                    pageNumber: 2,
                    pageSize: 25,
                };
                const apolloLinkHandlerStub = {} as HttpLinkHandler;
                const apolloMockResponse: ApolloQueryResult<DataJobExecutionsPage> =
                    {
                        data: {
                            content: [],
                            totalItems: 25,
                            totalPages: 1,
                        },
                        networkStatus: 7,
                        loading: false,
                    };

                apolloBaseStub.query.and.returnValue(of(apolloMockResponse));
                apolloStub.use.and.returnValues(null, apolloBaseStub);
                httpLinkStub.create.and.returnValue(apolloLinkHandlerStub);

                // When
                let dataJobExecutionsPage: DataJobExecutionsPage;
                service
                    .getExecutions(ownerTeam, gqlQuery, dataJobReqVariables)
                    .subscribe((r) => (dataJobExecutionsPage = r.data));

                // Then
                expect(apolloStub.use.calls.argsFor(0)).toEqual([ownerTeam]);
                expect(httpLinkStub.create).toHaveBeenCalledWith({
                    uri: `/data-jobs/for-team/${ownerTeam}/jobs`,
                    method: 'GET',
                });
                expect(apolloStub.createNamed.calls.argsFor(0)[0]).toEqual(
                    ownerTeam
                );
                expect(
                    apolloStub.createNamed.calls.argsFor(0)[1].cache
                ).toEqual(jasmine.any(InMemoryCache));
                expect(apolloStub.createNamed.calls.argsFor(0)[1].link).toBe(
                    apolloLinkHandlerStub
                );
                expect(
                    apolloStub.createNamed.calls.argsFor(0)[1].defaultOptions
                ).toEqual({
                    watchQuery: {
                        fetchPolicy: 'no-cache',
                        errorPolicy: 'all',
                    },
                    query: {
                        fetchPolicy: 'no-cache',
                        errorPolicy: 'all',
                    },
                });
                expect(apolloStub.use.calls.argsFor(1)).toEqual([ownerTeam]);
                expect(apolloBaseStub.query).toHaveBeenCalledWith({
                    query: gql`
                        ${gqlQuery}
                    `,
                    variables: dataJobReqVariables,
                });
                expect(dataJobExecutionsPage).toBe(apolloMockResponse.data);
            });
        });
    });
});
