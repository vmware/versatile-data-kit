/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/member-ordering */

import { Component, Inject, OnInit } from '@angular/core';
import { ActivatedRoute, Params } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';

import { interval, of, Subject, timer } from 'rxjs';
import { catchError, filter, finalize, map, switchMap, take, takeUntil, takeWhile, tap } from 'rxjs/operators';

import { ClrLoadingState } from '@clr/angular';

import * as fileSaver from 'file-saver';

import {
    ASC,
    CollectionsUtil,
    ComponentModel,
    ComponentService,
    ErrorHandlerService,
    ErrorRecord,
    NavigationService,
    OnTaurusModelError,
    OnTaurusModelInit,
    RouterService,
    RouteState,
    TaurusBaseComponent,
    ToastService,
    VmwToastType
} from '@versatiledatakit/shared';

import { DataJobUtil, ErrorUtil } from '../../shared/utils';
import { ExtractJobStatusPipe } from '../../shared/pipes';
import { ConfirmationModalOptions, DeleteModalOptions, ModalOptions } from '../../shared/model';

import {
    DATA_PIPELINES_CONFIGS,
    DataJobDeployment,
    DataJobExecution,
    DataJobExecutionDetails,
    DataJobExecutions,
    DataJobExecutionsPage,
    DataJobStatus,
    DataPipelinesConfig,
    ToastDefinitions
} from '../../model';

import { DataJobsApiService, DataJobsService } from '../../services';

enum TypeButtonState {
    /* eslint-disable-next-line @typescript-eslint/naming-convention */
    DOWNLOAD,
    /* eslint-disable-next-line @typescript-eslint/naming-convention */
    EXECUTE,
    /* eslint-disable-next-line @typescript-eslint/naming-convention */
    DELETE,
    /* eslint-disabe-next-line @typescript-eslint/naming-convention */
    STOP
}

@Component({
    selector: 'lib-data-job-page',
    templateUrl: './data-job-page.component.html',
    styleUrls: ['./data-job-page.component.scss']
})
export class DataJobPageComponent extends TaurusBaseComponent implements OnInit, OnTaurusModelInit, OnTaurusModelError {
    readonly uuid = 'DataJobPageComponent';

    teamName = '';
    jobName = '';
    isDataJobRunning = false;
    cancelDataJobDisabled = false;

    queryParams: Params = {};

    isSubpageNavigation = false;

    isJobAvailable = false;
    isJobEditable = false;

    isExecuteJobAllowed = false;
    isDownloadJobKeyAllowed = false;

    areJobExecutionsLoaded = false;

    loadingInProgress = false;

    jobExecutions: DataJobExecutions = [];
    jobDeployments: DataJobDeployment[] = [];

    deleteButtonsState = ClrLoadingState.DEFAULT;
    executeButtonsState = ClrLoadingState.DEFAULT;
    downloadButtonsState = ClrLoadingState.DEFAULT;
    stopButtonsState = ClrLoadingState.DEFAULT;

    deleteOptions: ModalOptions;
    executeNowOptions: ModalOptions;
    cancelNowOptions: ModalOptions;

    private _nonExistingJobMsgShowed = false;

    constructor(
        componentService: ComponentService,
        navigationService: NavigationService,
        activatedRoute: ActivatedRoute,
        private readonly routerService: RouterService,
        private readonly dataJobsService: DataJobsService,
        private readonly dataJobsApiService: DataJobsApiService,
        private readonly toastService: ToastService,
        private readonly errorHandlerService: ErrorHandlerService,
        @Inject(DATA_PIPELINES_CONFIGS)
        public readonly dataPipelinesModuleConfig: DataPipelinesConfig
    ) {
        super(componentService, navigationService, activatedRoute);

        this.isSubpageNavigation = !!activatedRoute.snapshot.data['activateSubpageNavigation'];

        this.deleteOptions = new DeleteModalOptions();
        this.executeNowOptions = new ConfirmationModalOptions();
        this.cancelNowOptions = new ConfirmationModalOptions();
    }

    /**
     * ** Navigate back leveraging provided router config.
     */
    doNavigateBack($event?: MouseEvent): void {
        $event?.preventDefault();

        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        this.navigateBack({ '$.team': this.teamName }).then();
    }

    /**
     * ** Returns if execution is in progress.
     */
    isExecutionInProgress(): boolean {
        return DataJobUtil.isJobRunning(this.jobExecutions);
    }

    /**
     * ** Show confirmation dialog for Job execution.
     */
    executeJob() {
        this.executeNowOptions.title = `Execute ${this.jobName} now?`;
        this.executeNowOptions.message = `Job <strong>${this.jobName}</strong> will be queued for execution.`;
        this.executeNowOptions.infoText = `Confirming will result in immediate data job execution.`;
        this.executeNowOptions.opened = true;
    }

    /**
     * ** On User confirm continue with Job execution.
     */
    confirmExecuteJob() {
        this._submitOperationStarted(TypeButtonState.EXECUTE);

        this.subscriptions.push(
            this.dataJobsApiService
                .executeDataJob(this.teamName, this.jobName, this._extractJobDeployment()?.id)
                .pipe(
                    finalize(() => {
                        this._submitOperationEnded();
                    })
                )
                .subscribe({
                    next: () => {
                        this.toastService.show(ToastDefinitions.successfullyRanJob(this.jobName));

                        let previousReqFinished = true;

                        this.areJobExecutionsLoaded = false;

                        this.subscriptions.push(
                            interval(1250) // Send polling request on every 1.25s until execution is accepted from backend
                                .pipe(
                                    // eslint-disable-next-line rxjs/no-unsafe-takeuntil
                                    takeUntil(timer(30000)), // Timer limit when polling to stop = 30s
                                    filter(() => previousReqFinished),
                                    tap(() => (previousReqFinished = false)),
                                    switchMap(() =>
                                        this.dataJobsApiService
                                            .getJobExecutions(this.teamName, this.jobName, true, null, {
                                                property: 'startTime',
                                                direction: ASC
                                            })
                                            .pipe(
                                                catchError((error: unknown) => {
                                                    this.errorHandlerService.processError(ErrorUtil.extractError(error as Error));

                                                    return of([]);
                                                }),
                                                finalize(() => {
                                                    previousReqFinished = true;
                                                })
                                            )
                                    ),
                                    map((executions: DataJobExecutionsPage) => (executions.content ? [...executions.content] : [])),
                                    takeWhile((executions) => {
                                        if (CollectionsUtil.isArrayEmpty(executions) || executions.length <= this.jobExecutions.length) {
                                            return true;
                                        }

                                        this.jobExecutions = executions;

                                        this.areJobExecutionsLoaded = true;

                                        const lastExecution = executions[executions.length - 1];
                                        if (!DataJobUtil.isJobRunningPredicate(lastExecution)) {
                                            return true;
                                        }

                                        this.dataJobsService.notifyForJobExecutions(executions);
                                        this.dataJobsService.notifyForRunningJobExecutionId(lastExecution.id);

                                        return false; // Stop polling if above condition is met.
                                    })
                                )
                                .subscribe() // eslint-disable-line rxjs/no-nested-subscribe
                        );
                    },
                    error: (error: unknown) => {
                        this.errorHandlerService.processError(ErrorUtil.extractError(error as Error), {
                            title:
                                (error as HttpErrorResponse)?.status === 409
                                    ? 'Failed, Data job is already executing'
                                    : 'Failed to queue Data job for execution'
                        });
                    }
                })
        );
    }

    /**
     * ** Download Job key.
     */
    downloadJobKey() {
        this._submitOperationStarted(TypeButtonState.DOWNLOAD);

        this.dataJobsApiService
            .downloadFile(this.teamName, this.jobName)
            .pipe(
                finalize(() => {
                    this._submitOperationEnded();
                })
            )
            .subscribe({
                next: (response: Blob) => {
                    const blob: Blob = new Blob([response], {
                        type: 'application/octet-stream'
                    });
                    // eslint-disable-next-line @typescript-eslint/no-unsafe-call,@typescript-eslint/no-unsafe-member-access
                    fileSaver.saveAs(blob, `${this.jobName}.keytab`);

                    this.toastService.show({
                        type: VmwToastType.INFO,
                        title: `Download completed`,
                        description: `Data job keytab "${this.jobName}.keytab" successfully downloaded`
                    });
                },
                error: (error: unknown) => {
                    const errorDescription =
                        (error as HttpErrorResponse)?.status === 404
                            ? `Download failed. Keytab file doesn't exist for this job.`
                            : `Download failed. Keytab file failed to download.`;

                    this.errorHandlerService.processError(ErrorUtil.extractError(error as Error), {
                        description: errorDescription
                    });
                }
            });
    }

    /**
     * ** Show confirmation dialog for Job Remove (Delete).
     */
    removeJob() {
        this.deleteOptions.message = `Job <strong>${this.jobName}</strong> will be deleted.
    Currently executing Data Jobs will be left to finish but the credentials will be revoked.`;
        this.deleteOptions.infoText = `Deleting this job means that <strong> it will be permanently removed from the system</strong>
    including all its state (properties), source code and any deployments.`;
        this.deleteOptions.showOkBtn = true;
        this.deleteOptions.cancelBtn = 'Cancel';
        this.deleteOptions.opened = true;
    }

    /**
     * ** On User confirm continue with Job Remove (Delete).
     */
    confirmRemoveJob() {
        this._submitOperationStarted(TypeButtonState.DELETE);

        this.dataJobsApiService
            .removeJob(this.teamName, this.jobName)
            .pipe(
                finalize(() => {
                    this._submitOperationEnded();
                })
            )
            .subscribe({
                next: () => {
                    this.toastService.show({
                        type: VmwToastType.INFO,
                        title: `Data job delete completed`,
                        description: `Data job "${this.jobName}" successfully deleted`
                    });

                    this.doNavigateBack();
                },
                error: (error: unknown) => {
                    this.errorHandlerService.processError(ErrorUtil.extractError(error as Error), {
                        title: `Data job delete failed`
                    });
                }
            });
    }

    confirmCancelDataJob() {
        this._submitOperationStarted(TypeButtonState.STOP);
        this.dataJobsApiService
            .cancelDataJobExecution(this.teamName, this.jobName, this.lastExecution()?.id)
            .pipe(
                finalize(() => {
                    this._submitOperationEnded();
                })
            )
            .subscribe({
                next: () => {
                    this.cancelDataJobDisabled = true;
                    this.toastService.show({
                        type: VmwToastType.INFO,
                        title: `Data job execution cancellation completed`,
                        description: `Data job "${this.jobName}" successfully canceled`
                    });
                },
                error: (error: unknown) => {
                    this.errorHandlerService.processError(ErrorUtil.extractError(error as Error), {
                        title: `Data job cancellation failed`
                    });
                }
            });
    }

    /**
     * ** Show confirmation dialog for Job execution cancellation.
     */
    cancelExecution() {
        this.cancelNowOptions.title = `Cancel ${this.lastExecution()?.id} now?`;
        this.cancelNowOptions.message = `Execution <strong>${this.lastExecution()?.id}</strong> will be canceled.`;
        this.cancelNowOptions.infoText = `Confirming will result in immediate data job execution cancellation.`;
        this.cancelNowOptions.opened = true;
    }

    lastExecution(): DataJobExecution {
        return this.jobExecutions[this.jobExecutions.length - 1];
    }

    isJobWithRunningStatus(): boolean {
        return this.lastExecution().status === 'RUNNING';
    }

    /**
     * @inheritDoc
     */
    onModelInit(): void {
        this.routerService
            .getState()
            .pipe(take(1))
            .subscribe((state) => this._initialize(state));
    }

    /**
     * @inheritDoc
     */
    onModelError(model: ComponentModel, _task: string, newErrorRecords: ErrorRecord[]) {
        newErrorRecords.forEach((errorRecord) => {
            const error = ErrorUtil.extractError(errorRecord.error);

            this.errorHandlerService.processError(error);
        });
    }

    private _initialize(state: RouteState): void {
        const teamParamKey = state.getData<string>('teamParamKey');
        this.teamName = state.getParam(teamParamKey);

        if (CollectionsUtil.isNil(teamParamKey) || CollectionsUtil.isNil(this.teamName)) {
            this._subscribeForImplicitTeam();
        }

        const jobParamKey = state.getData<string>('jobParamKey');
        this.jobName = state.getParam(jobParamKey);

        this.isJobEditable = !!state.getData('editable');

        this.queryParams = state.queryParams;

        this.isDownloadJobKeyAllowed = this.dataPipelinesModuleConfig.manageConfig?.allowKeyTabDownloads && this.isJobEditable;

        this._subscribeForTeamChange(state);
        this._subscribeForExecutionsChange();
        this._subscribeForExecutionIdChange();
        this._loadJobDetails();
        this._loadJobExecutions();
    }

    private _subscribeForImplicitTeam(): void {
        this.dataJobsService
            .getNotifiedForTeamImplicitly()
            .pipe(take(1))
            .subscribe((teamName) => (this.teamName = teamName));
    }

    private _subscribeForTeamChange(state: RouteState): void {
        const shouldActivateListener = !!state.getData<boolean>('activateListenerForTeamChange');

        if (shouldActivateListener && this.dataPipelinesModuleConfig?.manageConfig?.selectedTeamNameObservable) {
            this.subscriptions.push(
                this.dataPipelinesModuleConfig.manageConfig.selectedTeamNameObservable.subscribe((newTeam) => {
                    if (this.teamName !== newTeam) {
                        this.teamName = newTeam;

                        this.doNavigateBack();
                    }
                })
            );
        }
    }

    private _subscribeForExecutionsChange(): void {
        this.subscriptions.push(
            this.dataJobsService.getNotifiedForJobExecutions().subscribe((executions) => {
                this.jobExecutions = [...executions];
            })
        );
    }

    private _subscribeForExecutionIdChange(): void {
        const scheduleLastExecutionPolling = new Subject<string>();

        this.subscriptions.push(
            scheduleLastExecutionPolling
                .pipe(
                    switchMap((id) =>
                        interval(5000).pipe(
                            switchMap(() =>
                                this.dataJobsApiService.getJobExecution(this.teamName, this.jobName, id).pipe(
                                    map((execution) => {
                                        return {
                                            execution,
                                            error: null as Error
                                        };
                                    }),
                                    catchError((error: unknown) => {
                                        this.errorHandlerService.processError(ErrorUtil.extractError(error as Error));

                                        return of({
                                            execution: null as DataJobExecutionDetails,
                                            error: error as Error
                                        });
                                    })
                                )
                            ),
                            tap((data) => this._replaceRunningExecutionAndNotify(data.execution)),
                            takeWhile((data) => {
                                if (data.error instanceof HttpErrorResponse) {
                                    if (data.error.status === 404 || data.error.status >= 500) {
                                        this.isDataJobRunning = false;

                                        return false;
                                    }
                                }

                                const isRunning =
                                    CollectionsUtil.isNil(data.execution) || DataJobUtil.isJobRunningPredicate(data.execution);

                                if (!isRunning) {
                                    this.isDataJobRunning = false;
                                }
                                return isRunning;
                            })
                        )
                    )
                )
                .subscribe()
        );

        this.subscriptions.push(
            this.dataJobsService
                .getNotifiedForRunningJobExecutionId()
                .pipe(
                    switchMap((executionId: string) =>
                        this.dataJobsApiService.getJobExecution(this.teamName, this.jobName, executionId).pipe(
                            map((executionDetails) => [executionId, executionDetails]),
                            catchError((error: unknown) => {
                                this.errorHandlerService.processError(ErrorUtil.extractError(error as Error));

                                return of([executionId]);
                            })
                        )
                    )
                )
                .subscribe(([executionId, executionDetails]: [string, DataJobExecutionDetails]) => {
                    this.isDataJobRunning = true;
                    this.cancelDataJobDisabled = false;
                    this._replaceRunningExecutionAndNotify(executionDetails);
                    scheduleLastExecutionPolling.next(executionId);
                })
        );
    }

    private _loadJobDetails(): void {
        this.subscriptions.push(
            this.dataJobsApiService.getJobDetails(this.teamName, this.jobName).subscribe({
                error: (error: unknown) => {
                    if (error instanceof HttpErrorResponse) {
                        if (error.status === 404) {
                            this._showMessageJobNotExist();
                            this.doNavigateBack();
                        }

                        console.error('Error loading jobDetails', error);
                    }
                }
            })
        );
        this.subscriptions.push(
            this.dataJobsApiService.getJob(this.teamName, this.jobName).subscribe({
                next: (job) => {
                    if (CollectionsUtil.isDefined(job)) {
                        this.isJobAvailable = true;

                        this.jobDeployments = job.deployments;
                        this.isExecuteJobAllowed = ExtractJobStatusPipe.transform(this.jobDeployments) !== DataJobStatus.NOT_DEPLOYED;

                        return;
                    }

                    this._showMessageJobNotExist();
                    this.doNavigateBack();
                },
                error: (error: unknown) => {
                    this.errorHandlerService.processError(ErrorUtil.extractError(error as Error), {
                        title: `Loading Data job "${this.jobName}" failed`
                    });
                }
            })
        );
    }

    private _loadJobExecutions(): void {
        this.subscriptions.push(
            this.dataJobsApiService
                .getJobExecutions(this.teamName, this.jobName, true, null, {
                    property: 'startTime',
                    direction: ASC
                })
                .subscribe({
                    next: (value) => {
                        if (value?.content) {
                            this.dataJobsService.notifyForJobExecutions([...value.content]);

                            // eslint-disable-next-line @typescript-eslint/unbound-method
                            const runningExecution = value.content.find(DataJobUtil.isJobRunningPredicate);
                            if (runningExecution) {
                                this.dataJobsService.notifyForRunningJobExecutionId(runningExecution.id);
                            }
                        }

                        this.areJobExecutionsLoaded = true;
                    },
                    error: (error: unknown) => {
                        this.errorHandlerService.processError(ErrorUtil.extractError(error as Error));
                    }
                })
        );
    }

    private _replaceRunningExecutionAndNotify(executionDetails: DataJobExecutionDetails): void {
        if (CollectionsUtil.isNil(executionDetails)) {
            return;
        }

        const convertedExecution = DataJobUtil.convertFromExecutionDetailsToExecutionState(executionDetails);
        const foundIndex = this.jobExecutions.findIndex((ex) => ex.id === convertedExecution.id);

        if (foundIndex !== -1) {
            this.jobExecutions.splice(foundIndex, 1, convertedExecution);
        } else {
            this.jobExecutions.push(convertedExecution);
        }

        this.dataJobsService.notifyForJobExecutions(this.jobExecutions);
    }

    private _submitOperationStarted(type: TypeButtonState): void {
        switch (type) {
            case TypeButtonState.DELETE:
                this.deleteButtonsState = ClrLoadingState.LOADING;
                break;
            case TypeButtonState.DOWNLOAD:
                this.downloadButtonsState = ClrLoadingState.LOADING;
                break;
            case TypeButtonState.EXECUTE:
                this.executeButtonsState = ClrLoadingState.LOADING;
                break;
            case TypeButtonState.STOP:
                this.stopButtonsState = ClrLoadingState.LOADING;
                break;
        }

        this.loadingInProgress = true;
    }

    private _submitOperationEnded(): void {
        this.deleteButtonsState = ClrLoadingState.DEFAULT;
        this.downloadButtonsState = ClrLoadingState.DEFAULT;
        this.executeButtonsState = ClrLoadingState.DEFAULT;
        this.stopButtonsState = ClrLoadingState.DEFAULT;

        this.loadingInProgress = false;
    }

    private _extractJobDeployment(): DataJobDeployment {
        if (!this.jobDeployments) {
            return null;
        }

        return this.jobDeployments[this.jobDeployments.length - 1];
    }

    private _showMessageJobNotExist(): void {
        if (!this._nonExistingJobMsgShowed) {
            this._nonExistingJobMsgShowed = true;

            this.toastService.show({
                type: VmwToastType.FAILURE,
                title: `Job "${this.jobName}" doesn't exist`,
                description: `Data Job "${this.jobName}" for Team "${this.teamName}" doesn't exist, will load Data Jobs list`
            });
        }
    }
}
