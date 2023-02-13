/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, ElementRef, Inject, OnInit } from '@angular/core';
import { DOCUMENT, Location } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';

import { VmwToastType } from '@vdk/shared';

import { ComponentService, ErrorHandlerService, NavigationService, RouterService, ToastService } from '@vdk/shared';

import { ErrorUtil } from '../../../../shared/utils';

import { ConfirmationModalOptions, ModalOptions } from '../../../../shared/model';

import { DATA_PIPELINES_CONFIGS, DataJobStatus, DataPipelinesConfig, ToastDefinitions } from '../../../../model';
import { DataJobsApiService, DataJobsService } from '../../../../services';

import { ClrGridUIState, DataJobsBaseGridComponent } from '../../../base-grid/data-jobs-base-grid.component';

@Component({
    selector: 'lib-data-jobs-manage-grid',
    templateUrl: './data-jobs-manage-grid.component.html',
    styleUrls: ['./data-jobs-manage-grid.component.scss']
})
export class DataJobsManageGridComponent extends DataJobsBaseGridComponent implements OnInit {
    readonly uuid = 'DataJobsManageGridComponent';

    confirmStatusOptions: ModalOptions;
    confirmExecuteNowOptions: ModalOptions;

    override clrGridDefaultFilter: ClrGridUIState['filter'] = {
        // eslint-disable-next-line @typescript-eslint/naming-convention
        'deployments.enabled': DataJobStatus.ENABLED
    };
    override clrGridDefaultSort: ClrGridUIState['sort'] = {
        // eslint-disable-next-line @typescript-eslint/naming-convention
        'deployments.lastExecutionTime': -1
    };

    override quickFiltersDefaultActiveIndex = 1;

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
        @Inject(DATA_PIPELINES_CONFIGS) dataPipelinesModuleConfig: DataPipelinesConfig,
        private readonly toastService: ToastService
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
            'manage_data_jobs_grid_user_config',
            {
                hiddenColumns: {
                    description: true,
                    nextRun: true,
                    lastDeployedDate: true,
                    lastDeployedBy: true,
                    notifications: true,
                    source: true
                }
            });

        this.confirmStatusOptions = new ConfirmationModalOptions();
        this.confirmExecuteNowOptions = new ConfirmationModalOptions();

        this._inputConfig(dataPipelinesModuleConfig);
    }

    enable() {
        this.confirmStatusOptions.message = `Job <strong>${ this.selectedJob.jobName }</strong> will be enabled`;
        this.confirmStatusOptions.infoText = `Enabling this job means that <strong> it will be scheduled for execution</strong>`;
        this.confirmStatusOptions.opened = true;
    }

    disable() {
        this.confirmStatusOptions.message = `Job <strong>${ this.selectedJob.jobName }</strong> will be disabled`;
        this.confirmStatusOptions.infoText = `Disabling this job means that <strong>
    it will NOT be scheduled for execution anymore</strong>`;
        this.confirmStatusOptions.opened = true;
    }

    onJobStatusChange() {
        const selectedJobDeployment = this.extractSelectedJobDeployment();
        if (!selectedJobDeployment) {
            console.log('Status update action will not be performed for job with no deployments.');
            return;
        }

        this.subscriptions.push(
            this.dataJobsApiService.updateDataJobStatus(
                this.selectedJob.config?.team,
                this.selectedJob.jobName,
                selectedJobDeployment.id,
                !selectedJobDeployment.enabled
            )
                .subscribe({
                    next: () => {
                        selectedJobDeployment.enabled = !selectedJobDeployment.enabled;

                        const state = selectedJobDeployment.enabled
                            ? 'enabled'
                            : 'disabled';

                        this.toastService.show({
                            type: VmwToastType.INFO,
                            title: `Status update completed`,
                            description: `Data job "${ this.selectedJob.jobName }" successfully ${ state }`
                        });
                    },
                    error: (error: unknown) => {
                        this.errorHandlerService.processError(
                            ErrorUtil.extractError(error as Error),
                            {
                                title: `Updating status for Data job "${ this.selectedJob?.jobName }" failed`
                            }
                        );
                    }
                })
        );
    }

    executeDataJob() {
        this.confirmExecuteNowOptions.message = `Job <strong>${ this.selectedJob.jobName }</strong> will be queued for execution.`;
        this.confirmExecuteNowOptions.infoText = `Confirming will result in immediate data job execution.`;
        this.confirmExecuteNowOptions.opened = true;
    }

    onExecuteDataJob() {
        this.subscriptions.push(
            this.dataJobsApiService.executeDataJob(
                this.selectedJob.config?.team,
                this.selectedJob.jobName,
                this.extractSelectedJobDeployment().id
            )
                .subscribe({
                    next: () => {
                        this.toastService.show(ToastDefinitions.successfullyRanJob(this.selectedJob.jobName));
                    },
                    error: (error: unknown) => {
                        this.errorHandlerService.processError(
                            ErrorUtil.extractError(error as Error),
                            {
                                title: (error as HttpErrorResponse)?.status === 409
                                    ? 'Failed, Data job is already executing'
                                    : 'Failed to queue Data job for execution'
                            }
                        );
                    }
                })
        );
    }

    resetTeamNameFilter() {
        this.teamNameFilter = '';
    }

    showTeamsColumn() {
        return (this.dataPipelinesModuleConfig?.manageConfig?.showTeamsColumn);
    }

    extractSelectedJobDeployment() {
        return this.selectedJob?.deployments[this.selectedJob?.deployments?.length - 1];
    }

    private _inputConfig(dataPipelinesModuleConfig: DataPipelinesConfig) {
        if (dataPipelinesModuleConfig.manageConfig?.filterByTeamName) {
            this.filterByTeamName = dataPipelinesModuleConfig.manageConfig?.filterByTeamName;
        }

        if (dataPipelinesModuleConfig.manageConfig?.displayMode) {
            this.displayMode = dataPipelinesModuleConfig.manageConfig?.displayMode;
        }

        if (dataPipelinesModuleConfig.manageConfig?.selectedTeamNameObservable) {
            this.subscriptions.push(
                dataPipelinesModuleConfig.manageConfig
                                         ?.selectedTeamNameObservable
                                         .subscribe({
                                             next: (newTeam) => {
                                                 if (newTeam !== this.teamNameFilter) {
                                                     this.teamNameFilter = newTeam;
                                                     this.refresh();
                                                 }
                                             },
                                             error: (error: unknown) => {
                                                 this.resetTeamNameFilter();
                                                 console.error('Error loading selected team', error);
                                             }
                                         })
            );
        }
    }
}
