/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, ElementRef, Inject, Input, OnInit } from '@angular/core';
import { DOCUMENT, Location } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';

import { ComponentService, ErrorHandlerService, NavigationService, RouterService } from '@vdk/shared';

import { DATA_PIPELINES_CONFIGS, DataPipelinesConfig, DisplayMode } from '../../../../model';
import { DataJobsApiService, DataJobsService } from '../../../../services';

import { DataJobsBaseGridComponent } from '../../../base-grid/data-jobs-base-grid.component';

@Component({
    selector: 'lib-data-jobs-explore-grid',
    templateUrl: './data-jobs-explore-grid.component.html',
    styleUrls: ['./data-jobs-explore-grid.component.scss']
})
export class DataJobsExploreGridComponent extends DataJobsBaseGridComponent implements OnInit {
    //Decorators are not inherited in Angular. If we need @Input() we need to declare it here
    @Input() override teamNameFilter: string;
    @Input() override displayMode: DisplayMode;

    readonly uuid = 'DataJobsExploreGridComponent';

    constructor( // NOSONAR
        componentService: ComponentService,
        navigationService: NavigationService,
        activatedRoute: ActivatedRoute,
        routerService: RouterService,
        dataJobsService: DataJobsService,
        dataJobsApiService: DataJobsApiService,
        errorHandlerService: ErrorHandlerService,
        location: Location,
        router: Router,
        elementRef: ElementRef<HTMLElement>,
        @Inject(DOCUMENT) document: Document,
        @Inject(DATA_PIPELINES_CONFIGS) dataPipelinesModuleConfig: DataPipelinesConfig
    ) {

        super(
            componentService,
            navigationService,
            activatedRoute,
            routerService,
            dataJobsService,
            dataJobsApiService,
            errorHandlerService,
            location,
            router,
            elementRef,
            document,
            dataPipelinesModuleConfig,
            'explore_data_jobs_grid_user_config',
            {
                hiddenColumns: {
                    description: true,
                    lastExecutionDuration: true,
                    successRate: true,
                    nextRun: true,
                    lastDeployedDate: true,
                    lastDeployedBy: true,
                    source: true,
                    logsUrl: true
                }
            });
    }

    showTeamsColumn() {
        return (this.dataPipelinesModuleConfig?.exploreConfig?.showTeamsColumn);
    }
}
