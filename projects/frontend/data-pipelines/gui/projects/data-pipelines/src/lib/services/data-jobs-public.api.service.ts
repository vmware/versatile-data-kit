/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';

import { EMPTY, expand, Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { ApiPredicate } from '@versatiledatakit/shared';

import { DataJob, DataJobPage } from '../model';

import { DataJobsBaseApiService } from './data-jobs-base.api.service';

@Injectable()
export class DataJobsPublicApiService {
    /**
     * ** Constructor.
     */
    constructor(private readonly dataJobsBaseService: DataJobsBaseApiService) {}

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
                dataJobs = dataJobs.concat(
                    dataJobPage.content as unknown as DataJob[],
                );

                return dataJobs;
            }),
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
                sort: null,
            },
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
                    pageSize: 1,
                },
            )
            .pipe(map((response) => response?.data?.totalItems ?? 0));
    }

    /**
     * ** Retrieve the data-jobs page.
     */
    private _getDataJobsPage(
        team: string,
        pageNumber: number,
        pageSize: number,
        filters: ApiPredicate[] = [],
        searchQueryValue: string = null,
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
                    pageSize,
                },
            )
            .pipe(map((response) => response.data));
    }
}
