/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, ElementRef, HostBinding, Inject, Input, OnInit } from '@angular/core';
import { DOCUMENT, Location } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';

import { ComponentService, ErrorHandlerService, NavigationService, RouterService } from '@versatiledatakit/shared';

import { DATA_PIPELINES_CONFIGS, DataPipelinesConfig, DisplayMode } from '../../../../model';
import { DataJobsApiService, DataJobsService } from '../../../../services';

import { DataJobsBaseGridComponent } from '../../../base-grid/data-jobs-base-grid.component';

@Component({
    selector: 'lib-data-jobs-explore-grid',
    templateUrl: './data-jobs-explore-grid.component.html',
    styleUrls: ['./data-jobs-explore-grid.component.scss']
})
export class DataJobsExploreGridComponent extends DataJobsBaseGridComponent implements OnInit {
    /**
     * @inheritDoc
     */
    static override readonly CLASS_NAME: string = 'DataJobsExploreGridComponent';

    /**
     * @inheritDoc
     */
    static override readonly PUBLIC_NAME: string = 'DataJobs-ExploreGrid-Component';

    //Decorators are not inherited in Angular. If we need @Input() we need to declare it here
    @Input() override teamNameFilter: string;
    @Input() override displayMode: DisplayMode;

    @HostBinding('attr.data-cy') attributeDataCy = 'data-pipelines-explore-data-jobs';

    readonly uuid = 'DataJobsExploreGridComponent';

    constructor(
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
        @Inject(DATA_PIPELINES_CONFIGS)
        dataPipelinesModuleConfig: DataPipelinesConfig
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
            },
            DataJobsExploreGridComponent.CLASS_NAME
        );
    }

    showTeamsColumn() {
        return this.dataPipelinesModuleConfig?.exploreConfig?.showTeamsColumn;
    }

    updateQuickFilter($event) {
        let activeStatus = '';
        if ($event.activatedFilter && $event.activatedFilter['label']) {
            activeStatus = $event.activatedFilter['label'];
        }
        this.updateDeploymentStatus(activeStatus);
    }
}
