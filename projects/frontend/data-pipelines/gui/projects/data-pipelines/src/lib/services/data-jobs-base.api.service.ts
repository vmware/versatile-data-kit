/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/naming-convention */

import { Inject, Injectable } from '@angular/core';

import { Observable } from 'rxjs';

import { ApolloQueryResult, DefaultOptions, gql, InMemoryCache } from '@apollo/client/core';

import { Apollo, ApolloBase, QueryRef } from 'apollo-angular';
import { HttpLink } from 'apollo-angular/http';

import { TaurusBaseApiService } from '@versatiledatakit/shared';

import {
    DATA_PIPELINES_CONFIGS,
    DataJob,
    DataJobExecutionsPage,
    DataJobExecutionsReqVariables,
    DataJobPage,
    DataJobReqVariables,
    DataPipelinesConfig
} from '../model';

/**
 * ** Data Jobs Service build on top of Apollo gql client.
 */
@Injectable()
export class DataJobsBaseApiService extends TaurusBaseApiService<DataJobsBaseApiService> {
    /**
     * @inheritDoc
     */
    static override readonly CLASS_NAME: string = 'DataJobsBaseApiService';

    /**
     * @inheritDoc
     */
    static override readonly PUBLIC_NAME: string = 'Data-Pipelines-Service';

    private static readonly APOLLO_METHOD = 'GET';
    private static readonly APOLLO_DEFAULT_OPTIONS: DefaultOptions = {
        watchQuery: {
            fetchPolicy: 'no-cache',
            errorPolicy: 'all'
        },
        query: {
            fetchPolicy: 'no-cache',
            errorPolicy: 'all'
        }
    };

    /**
     * ** Constructor.
     */
    constructor(
        @Inject(DATA_PIPELINES_CONFIGS) private readonly dataPipelinesConfig: DataPipelinesConfig,
        private readonly apollo: Apollo,
        private readonly httpLink: HttpLink
    ) {
        super(DataJobsBaseApiService.CLASS_NAME);

        this.registerErrorCodes(DataJobsBaseApiService);
    }

    /**
     * ** Get all DataJobs for provided OwnerTeam and load data based on provided gqlQuery.
     */
    getJobs(ownerTeam: string, gqlQuery: string, variables: DataJobReqVariables): Observable<ApolloQueryResult<DataJobPage>> {
        return this.getApolloClientFor(ownerTeam).query({
            query: gql`
                ${gqlQuery}
            `,
            variables
        });
    }

    /**
     * ** Create Apollo watcher for gqlQuery.
     */
    watchForJobs(ownerTeam: string, gqlQuery: string, variables: DataJobReqVariables): QueryRef<DataJobPage, DataJobReqVariables> {
        return this.getApolloClientFor(ownerTeam).watchQuery({
            query: gql`
                ${gqlQuery}
            `,
            variables
        });
    }

    /**
     * ** Get all DataJob Executions for provided OwnerTeam and load data based on provided gqlQuery.
     */
    getExecutions(
        ownerTeam: string,
        gqlQuery: string,
        variables: DataJobExecutionsReqVariables
    ): Observable<ApolloQueryResult<DataJobExecutionsPage>> {
        return this.getApolloClientFor(ownerTeam).query({
            query: gql`
                ${gqlQuery}
            `,
            variables
        });
    }

    private getApolloClientFor(ownerTeam: string): ApolloBase<DataJob> {
        if (!this.apollo.use(ownerTeam)) {
            this.apollo.createNamed(ownerTeam, {
                cache: new InMemoryCache({
                    typePolicies: {
                        Query: {
                            fields: {
                                jobs: (_existing, _options) => {
                                    return {};
                                },
                                executions: (_existing, _options) => {
                                    return {};
                                }
                            }
                        }
                    }
                }),
                link: this.httpLink.create({
                    uri: `${this._resolvePipelinesServiceUrl()}/data-jobs/for-team/${ownerTeam}/jobs`,
                    method: DataJobsBaseApiService.APOLLO_METHOD
                }),
                defaultOptions: DataJobsBaseApiService.APOLLO_DEFAULT_OPTIONS
            });
        }

        return this.apollo.use(ownerTeam) as ApolloBase<DataJob>;
    }

    private _resolvePipelinesServiceUrl(): string {
        return this.dataPipelinesConfig?.resourceServer?.getUrl ? this.dataPipelinesConfig.resourceServer.getUrl() : '';
    }
}
