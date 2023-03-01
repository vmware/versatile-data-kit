/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, HostListener, Input, OnInit } from '@angular/core';

import { Observable, of, throwError } from 'rxjs';
import { catchError, delay, map } from 'rxjs/operators';

import { ErrorHandlerService } from '@vdk/shared';

import { ErrorUtil } from '../../shared/utils';

import { DataJobExecutionStatus, DataJobPage } from '../../model';

import { DataJobsApiService } from '../../services';

export enum WidgetTab {
    /* eslint-disable-next-line @typescript-eslint/naming-convention */
    DATAJOBS,
    /* eslint-disable-next-line @typescript-eslint/naming-convention */
    EXECUTIONS,
    /* eslint-disable-next-line @typescript-eslint/naming-convention */
    FAILURES,
    /* eslint-disable-next-line @typescript-eslint/naming-convention */
    NONE,
}

// TODO: Remove when consume data from API
const executionsMock = [
    {
        jobName: 'data-job-1',
        status: DataJobExecutionStatus.FINISHED,
        startTime: Date.now(),
        endTime: Date.now(),
        startedBy: 'auserov',
    },
    {
        jobName: 'data-job-2',
        status: DataJobExecutionStatus.FAILED,
        startTime: Date.now(),
        endTime: Date.now(),
        startedBy: 'buserov',
    },
    {
        jobName: 'data-job-3',
        status: DataJobExecutionStatus.FINISHED,
        startTime: Date.now(),
        endTime: Date.now(),
        startedBy: 'cuserov',
    },
    {
        jobName: 'data-job-long-name-test-1',
        status: DataJobExecutionStatus.FINISHED,
        startTime: Date.now(),
        endTime: Date.now(),
        startedBy: 'duserov',
    },
    {
        jobName: 'data-job-long-name-test-2',
        status: DataJobExecutionStatus.FAILED,
        startTime: Date.now(),
        endTime: Date.now(),
        startedBy: 'euserov',
    },
    {
        jobName: 'data-job-long-name-test-3',
        status: DataJobExecutionStatus.SUBMITTED,
        startTime: Date.now(),
        endTime: Date.now(),
        startedBy: 'fuserov',
    },
    {
        jobName: 'data-job-long-name-test-4',
        status: DataJobExecutionStatus.PLATFORM_ERROR,
        startTime: Date.now(),
        endTime: Date.now(),
        startedBy: 'guserov',
    },
    {
        jobName: 'data-job-long-name-test-5',
        status: DataJobExecutionStatus.USER_ERROR,
        startTime: Date.now(),
        endTime: Date.now(),
        startedBy: 'huserov',
    },
    {
        jobName: 'data-job-a-very-long-name-listed-here-test-1',
        status: DataJobExecutionStatus.FINISHED,
        startTime: Date.now(),
        endTime: Date.now(),
        startedBy: 'fuserov',
    },
];

@Component({
    selector: 'lib-data-jobs-widget-one',
    templateUrl: './data-jobs-widget-one.component.html',
    styleUrls: ['./data-jobs-widget-one.component.scss', './widget.scss'],
})
export class DataJobsWidgetOneComponent implements OnInit {
    @Input() manageLink: string;

    selectedTab: WidgetTab = WidgetTab.DATAJOBS;
    jobs$: Observable<DataJobPage>;
    /* eslint-disable @typescript-eslint/no-explicit-any */
    executions$: Observable<any>;
    failures$: Observable<any>;
    /* eslint-enable @typescript-eslint/no-explicit-any */
    widgetTab = WidgetTab;
    pageSize = 25;
    currentPage = 1;

    errorJobs: boolean;

    constructor(
        private readonly dataJobsService: DataJobsApiService,
        private readonly errorHandlerService: ErrorHandlerService
    ) {}

    @HostListener('window:resize')
    onWindowResize() {
        // Listener was needed because ChangeDetection cycle doesn't run for Component on "window resize event"
        // and doesn't update the data grid column width as expected,
        // so only solution was to add dummy listener for window:resize which triggers ChangeDetection cycle inside the Component.
        // No-op! Updates the component when the window resizes. This is used for resizing the data grid columns.
    }

    ngOnInit() {
        this.refreshAll();
    }

    refreshAll() {
        this.refresh(this.currentPage, WidgetTab.DATAJOBS);
        this.refresh(this.currentPage, WidgetTab.EXECUTIONS);
        this.refresh(this.currentPage, WidgetTab.FAILURES);
    }

    switchTab(tab: WidgetTab) {
        this.selectedTab = this.selectedTab !== tab ? tab : WidgetTab.NONE;
        this.currentPage = 1;
    }

    refresh(currentPage: number, tab: WidgetTab) {
        this.currentPage = currentPage;

        switch (tab) {
            case WidgetTab.DATAJOBS:
                this.errorJobs = false;
                this.jobs$ = this.dataJobsService
                    .getJobs([], '', this.currentPage, this.pageSize)
                    .pipe(
                        map((result) => result?.data),
                        catchError((error: unknown) => {
                            this.errorJobs = !!error;

                            this.errorHandlerService.processError(
                                ErrorUtil.extractError(error as Error)
                            );

                            return throwError(() => error);
                        })
                    );
                break;
            case WidgetTab.EXECUTIONS:
                // TODO: Consume data from API
                this.executions$ = of({
                    data: {
                        totalItems: 0,
                        totalPages: executionsMock.length / this.pageSize,
                        content: [],
                    },
                }).pipe(
                    map((result) => result?.data),
                    delay(1200) // TODO: Remove delay when consume data from API
                );
                break;
            case WidgetTab.FAILURES:
                // TODO: Consume data from API
                const failuresMock = executionsMock.filter(
                    (e) => e.status === DataJobExecutionStatus.FAILED
                );
                this.failures$ = of({
                    data: {
                        totalItems: 0,
                        totalPages: failuresMock.length / this.pageSize,
                        content: [],
                    },
                }).pipe(
                    map((result) => result?.data),
                    delay(1800) // TODO: Remove delay when consume data from API
                );
                break;
        }
    }
}
