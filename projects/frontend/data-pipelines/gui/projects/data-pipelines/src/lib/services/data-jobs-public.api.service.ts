/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

import { Inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { EMPTY, expand, Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

import { ApiPredicate, TaurusBaseApiService } from '@versatiledatakit/shared';

import { ErrorUtil } from '../shared/utils';

import { DATA_PIPELINES_CONFIGS, DataJob, DataJobPage, DataPipelinesConfig, IPcsOAuthDto } from '../model';

import { DataJobsBaseApiService } from './data-jobs-base.api.service';

@Injectable()
export class DataJobsPublicApiService extends TaurusBaseApiService<DataJobsPublicApiService> {
    /**
     * @inheritDoc
     */
    static override readonly CLASS_NAME: string = 'DataJobsPublicApiService';

    /**
     * @inheritDoc
     */
    static override readonly PUBLIC_NAME: string = 'Data-Pipelines-Service';

    /**
     * ** Constructor.
     */
    constructor(
        @Inject(DATA_PIPELINES_CONFIGS) private readonly dataPipelinesConfig: DataPipelinesConfig,
        private readonly dataJobsBaseService: DataJobsBaseApiService,
        private readonly httpClient: HttpClient
    ) {
        super(DataJobsPublicApiService.CLASS_NAME);

        this.registerErrorCodes(DataJobsPublicApiService);
    }

    /**
     * ** Retrieve all DataJobs for Team.
     */
    getAllDataJobs(team: string): Observable<
        Array<{
            jobName?: string;
            config?: {
                team?: string;
                description?: string;
                sourceUrl?: string;
            };
        }>
    > {
        const pageSize = 1000;
        let pageNumber = 1;
        let dataJobs: DataJob[] = [];

        return this._getDataJobsPage(team, pageNumber, pageSize).pipe(
            expand((dataJobPage) => {
                if (dataJobPage.totalPages <= pageNumber) {
                    return EMPTY;
                } else {
                    return this._getDataJobsPage(team, ++pageNumber, pageSize);
                }
            }),
            map((dataJobPage) => {
                dataJobs = dataJobs.concat(dataJobPage.content as unknown as DataJob[]);

                return dataJobs;
            }),
            catchError((error: unknown) => throwError(() => ErrorUtil.extractError(error as Error)))
        );
    }

    /**
     * ** Get total number of Data Jobs assets for Team.
     */
    getDataJobsTotal(team: string): Observable<number> {
        const filters: ApiPredicate[] = [
            {
                property: 'config.team',
                pattern: team,
                sort: null
            }
        ];

        return this.dataJobsBaseService
            .getJobs(
                team,
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
                    filter: filters,
                    search: null,
                    pageNumber: 1,
                    pageSize: 1
                }
            )
            .pipe(
                map((response) => response?.data?.totalItems ?? 0),
                catchError((error: unknown) => throwError(() => ErrorUtil.extractError(error as Error)))
            );
    }

    /**
     * ** Returns OAuth app client id for given Team name.
     */
    getTeamOAuthClientId(teamName: string): Observable<IPcsOAuthDto> {
        return this.httpClient.get<IPcsOAuthDto>(
            `${this._resolvePipelinesServiceUrl()}/data-jobs/teams/${teamName}/oauth-credentials/client-id`
        );
    }

    /**
     * ** Returns inventory of found OAuth apps client ids for given Team names.
     */
    getInventoryOfTeamsOAuthClientIds(clientIds: string[]): Observable<IPcsOAuthDto[]> {
        return this.httpClient.post<IPcsOAuthDto[]>(
            `${this._resolvePipelinesServiceUrl()}/data-jobs/oauth-credentials/client-ids`,
            clientIds
        );
    }

    /**
     * ** Retrieve the data-jobs page.
     */
    private _getDataJobsPage(
        team: string,
        pageNumber: number,
        pageSize: number,
        filters: ApiPredicate[] = [],
        searchQueryValue: string = null
    ): Observable<DataJobPage> {
        return this.dataJobsBaseService
            .getJobs(
                team,
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
                    filter: filters,
                    search: searchQueryValue,
                    pageNumber,
                    pageSize
                }
            )
            .pipe(map((response) => response.data));
    }

    private _resolvePipelinesServiceUrl(): string {
        return this.dataPipelinesConfig?.resourceServer?.getUrl ? this.dataPipelinesConfig.resourceServer.getUrl() : '';
    }
}
