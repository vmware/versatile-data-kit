/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

import { take } from 'rxjs/operators';

import {
    FORM_STATE,
    VdkFormState,
    VmwToastType,
} from '@versatiledatakit/shared';

import {
    ASC,
    CollectionsUtil,
    ComponentModel,
    ComponentService,
    ErrorHandlerConfig,
    ErrorHandlerService,
    NavigationService,
    OnTaurusModelChange,
    OnTaurusModelError,
    OnTaurusModelInit,
    OnTaurusModelLoad,
    RouterService,
    RouteState,
    TaurusBaseComponent,
    ToastService,
} from '@versatiledatakit/shared';

import {
    ConfirmationModalOptions,
    DeleteModalOptions,
    ModalOptions,
} from '../../../../shared/model';
import {
    CronUtil,
    DataJobUtil,
    ErrorUtil,
    StringUtil,
} from '../../../../shared/utils';
import { ExtractJobStatusPipe, ParseEpochPipe } from '../../../../shared/pipes';

import {
    DATA_PIPELINES_CONFIGS,
    DataJob,
    DataJobDeployment,
    DataJobDetails,
    DataJobExecutionOrder,
    DataJobExecutions,
    DataJobStatus,
    DataPipelinesConfig,
    JOB_DEPLOYMENT_ID_REQ_PARAM,
    JOB_DETAILS_DATA_KEY,
    JOB_DETAILS_REQ_PARAM,
    JOB_EXECUTIONS_DATA_KEY,
    JOB_NAME_REQ_PARAM,
    JOB_STATE_DATA_KEY,
    JOB_STATE_REQ_PARAM,
    JOB_STATUS_REQ_PARAM,
    ORDER_REQ_PARAM,
    TEAM_NAME_REQ_PARAM,
} from '../../../../model';
import { DataJobsApiService, DataJobsService } from '../../../../services';

import {
    TASK_LOAD_JOB_DETAILS,
    TASK_LOAD_JOB_EXECUTIONS,
    TASK_LOAD_JOB_STATE,
    TASK_UPDATE_JOB_DESCRIPTION,
    TASK_UPDATE_JOB_STATUS,
} from '../../../../state/tasks';

@Component({
    selector: 'lib-data-job-details-page',
    templateUrl: './data-job-details-page.component.html',
    styleUrls: ['./data-job-details-page.component.scss'],
})
export class DataJobDetailsPageComponent
    extends TaurusBaseComponent
    implements
        OnInit,
        OnTaurusModelInit,
        OnTaurusModelLoad,
        OnTaurusModelChange,
        OnTaurusModelError
{
    readonly uuid = 'DataJobDetailsPageComponent';

    dataJobStatusEnum = DataJobStatus;

    jobName: string;
    teamName: string;
    jobState: DataJob;
    jobDetails: DataJobDetails;
    jobExecutions: DataJobExecutions = [];

    isJobEditable = false;

    shouldShowTeamsSection = false;

    cronError: string = null;

    next: Date;

    loadingExecutions = true;
    loadingInProgress = false;
    allowExecutionsByDeployment = false;

    tmForm: FormGroup;
    formState: VdkFormState;
    readFormState: VdkFormState;
    editableFormState: VdkFormState;

    canEditSection = true;

    collectorOptions: ModalOptions;
    confirmationOptions: ModalOptions;
    deleteOptions: ModalOptions;
    executeNowOptions: ModalOptions;

    showFullDescription = false;

    descriptionWordsBeforeTruncate = 12;

    get name() {
        return this.tmForm.get('name');
    }

    get team() {
        return this.tmForm.get('team');
    }

    get status() {
        return this.tmForm.get('status');
    }

    get description() {
        return this.tmForm.get('description');
    }

    constructor(
        // NOSONAR
        componentService: ComponentService,
        navigationService: NavigationService,
        activatedRoute: ActivatedRoute,
        private readonly router: Router,
        private readonly routerService: RouterService,
        private readonly dataJobsService: DataJobsService,
        private readonly dataJobsApiService: DataJobsApiService,
        private readonly formBuilder: FormBuilder,
        private readonly toastService: ToastService,
        private readonly errorHandlerService: ErrorHandlerService,
        @Inject(DATA_PIPELINES_CONFIGS)
        public readonly dataPipelinesModuleConfig: DataPipelinesConfig,
    ) {
        super(componentService, navigationService, activatedRoute);

        this.formState = new VdkFormState(FORM_STATE.VIEW);
        this.readFormState = new VdkFormState(FORM_STATE.VIEW);
        this.editableFormState = new VdkFormState(FORM_STATE.CAN_EDIT);

        this.confirmationOptions = new ConfirmationModalOptions();
        this.deleteOptions = new DeleteModalOptions();
        this.executeNowOptions = new ConfirmationModalOptions();

        this._initForm();
    }

    isDescriptionSubmitEnabled(): boolean {
        return (
            this._isFormSubmitEnabled() &&
            this.description.value !== this.jobDetails.description
        );
    }

    isStatusSubmitEnabled(): boolean {
        return (
            this._isFormSubmitEnabled() &&
            this.status.value !==
                ExtractJobStatusPipe.transform(this.jobState?.deployments)
        );
    }

    isJobRunning(): boolean {
        return DataJobUtil.isJobRunning(this.jobExecutions);
    }

    showNoNotificationsLabel(notifications: string[]): boolean {
        return !notifications || notifications.length < 1;
    }

    sectionStateChange(sectionState: VdkFormState) {
        if (sectionState.state === FORM_STATE.CAN_EDIT) {
            switch (sectionState.emittingSection) {
                case 'status':
                    this.status.setValue(
                        ExtractJobStatusPipe.transform(
                            this.jobState?.deployments,
                        ),
                    );
                    break;
                case 'description':
                    this.description.setValue(this.jobDetails.description);
                    break;
                default:
                    break;
            }
            this.canEditSection = true;
        } else if (sectionState.state === FORM_STATE.SUBMIT) {
            this.submitForm(sectionState);
        } else if (sectionState.state === FORM_STATE.EDIT) {
            this.canEditSection = false;
        }
    }

    submitForm(event: VdkFormState) {
        if (
            event.emittingSection === 'description' &&
            this.isDescriptionSubmitEnabled()
        ) {
            this._doSubmitDescriptionUpdate();
        }

        if (
            event.emittingSection === 'status' &&
            this.isStatusSubmitEnabled()
        ) {
            this._doSubmitStatusUpdate();
        }
    }

    editOperationEnded() {
        this.formState = new VdkFormState(FORM_STATE.CAN_EDIT);
        this.canEditSection = true;
    }

    loadJobExecutions() {
        this.dataJobsService.loadJobExecutions(this.model);
    }

    redirectToHealthStatus() {
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        this.router
            .navigateByUrl(
                StringUtil.stringFormat(
                    this.dataPipelinesModuleConfig.healthStatusUrl,
                    this.jobDetails.job_name,
                ),
            )
            .then();
    }

    /**
     * @inheritDoc
     */
    onModelInit(): void {
        this.routerService
            .getState()
            .pipe(take(1))
            .subscribe((routeState) => this._initialize(routeState));
    }

    /**
     * @inheritDoc
     */
    onModelLoad(model: ComponentModel, task: string): void {
        if (task === TASK_LOAD_JOB_EXECUTIONS) {
            this.loadingExecutions = false;
        }
    }

    /**
     * @inheritDoc
     */
    onModelChange(model: ComponentModel, task: string): void {
        if (task === TASK_LOAD_JOB_STATE) {
            this.jobState = model
                .getComponentState()
                .data.get(JOB_STATE_DATA_KEY);
            this._initializeNextRunDate();
            this.allowExecutionsByDeployment =
                ExtractJobStatusPipe.transform(this.jobState?.deployments) !==
                DataJobStatus.NOT_DEPLOYED;
            this.cronError = CronUtil.getNextExecutionErrors(
                this.jobState?.config?.schedule?.scheduleCron,
            );

            return;
        }

        if (task === TASK_LOAD_JOB_DETAILS) {
            this.jobDetails = model
                .getComponentState()
                .data.get(JOB_DETAILS_DATA_KEY);
            this._updateForm();

            return;
        }

        if (task === TASK_LOAD_JOB_EXECUTIONS) {
            const executions: DataJobExecutions = model
                .getComponentState()
                .data.get(JOB_EXECUTIONS_DATA_KEY);

            if (executions) {
                this.dataJobsService.notifyForJobExecutions([...executions]);

                // eslint-disable-next-line @typescript-eslint/unbound-method
                const runningExecution = executions.find(
                    DataJobUtil.isJobRunningPredicate,
                );
                if (runningExecution) {
                    this.dataJobsService.notifyForRunningJobExecutionId(
                        runningExecution.id,
                    );
                }
            }

            return;
        }

        if (task === TASK_UPDATE_JOB_DESCRIPTION) {
            this.toastService.show({
                type: VmwToastType.INFO,
                title: `Description update completed`,
                description: `Data job "${this.jobName}" description successfully updated`,
            });

            this.jobDetails = model
                .getComponentState()
                .data.get(JOB_DETAILS_DATA_KEY);

            this.editOperationEnded();

            return;
        }

        if (task === TASK_UPDATE_JOB_STATUS) {
            this.toastService.show({
                type: VmwToastType.INFO,
                title: `Status update completed`,
                description:
                    `Data job "${this.jobName}" successfully ` +
                    `${
                        !this._extractJobDeployment()?.enabled
                            ? 'enabled'
                            : 'disabled'
                    }`,
            });

            this.jobState = model
                .getComponentState()
                .data.get(JOB_STATE_DATA_KEY);

            this.editOperationEnded();
        }
    }

    /**
     * @inheritDoc
     */
    onModelError(model: ComponentModel, task: string): void {
        const error = ErrorUtil.extractError(model.getComponentState().error);

        let errorHandlerConfig: ErrorHandlerConfig;

        switch (task) {
            case TASK_LOAD_JOB_DETAILS:
                this._resetJobDetails();
                break;
            case TASK_LOAD_JOB_EXECUTIONS:
                // No-op.
                break;
            case TASK_LOAD_JOB_STATE:
                // No-op.
                break;
            case TASK_UPDATE_JOB_DESCRIPTION:
                errorHandlerConfig = {
                    title: 'Description update failed',
                };
                this.editOperationEnded();
                break;
            case TASK_UPDATE_JOB_STATUS:
                errorHandlerConfig = {
                    title: 'Status update failed',
                };
                this.editOperationEnded();
                break;
            default:
            // No-op.
        }

        this.errorHandlerService.processError(error, errorHandlerConfig);
    }

    /**
     * @inheritDoc
     */
    override ngOnInit() {
        super.ngOnInit();

        this._initializeNextRunDate();

        this.shouldShowTeamsSection =
            this.dataPipelinesModuleConfig?.exploreConfig?.showTeamsColumn;
    }

    private _initialize(state: RouteState): void {
        const teamParamKey = state.getData<string>('teamParamKey');
        this.teamName = state.getParam(teamParamKey);

        if (
            CollectionsUtil.isNil(teamParamKey) ||
            CollectionsUtil.isNil(this.teamName)
        ) {
            this._subscribeForImplicitTeam();
        }

        const jobParamKey = state.getData<string>('jobParamKey');
        this.jobName = state.getParam(jobParamKey);

        this.isJobEditable = !!state.getData('editable');

        if (this.isJobEditable) {
            this.formState = this.editableFormState;
        }

        this._subscribeForExecutions();

        this.dataJobsService.loadJob(
            this.model
                .withRequestParam(TEAM_NAME_REQ_PARAM, this.teamName)
                .withRequestParam(JOB_NAME_REQ_PARAM, this.jobName)
                .withRequestParam(ORDER_REQ_PARAM, {
                    property: 'startTime',
                    direction: ASC,
                } as DataJobExecutionOrder),
        );
    }

    private _subscribeForImplicitTeam(): void {
        this.dataJobsService
            .getNotifiedForTeamImplicitly()
            .pipe(take(1))
            .subscribe((teamName) => (this.teamName = teamName));
    }

    private _extractJobDeployment(): DataJobDeployment {
        if (!this.jobState?.deployments) {
            return null;
        }
        return this.jobState?.deployments[
            this.jobState?.deployments.length - 1
        ];
    }

    private _isFormSubmitEnabled(): boolean {
        return !this.tmForm?.pristine && this.tmForm?.valid;
    }

    private _initForm(): void {
        this.tmForm = this.formBuilder.group({
            name: '',
            team: '',
            status: '',
            description: '',
        });
    }

    private _updateForm(): void {
        this.tmForm.setValue({
            name: this.jobDetails.job_name,
            team: this.jobDetails.team,
            status: ExtractJobStatusPipe.transform(this.jobState?.deployments),
            description: this.jobDetails.description,
        });
    }

    private _doSubmitDescriptionUpdate(): void {
        const jobDetailsUpdated: DataJobDetails = {
            ...this.jobDetails,
            description: this.description.value as string,
        };

        this.dataJobsService.updateJob(
            this.model
                .withRequestParam(TEAM_NAME_REQ_PARAM, jobDetailsUpdated.team)
                .withRequestParam(
                    JOB_NAME_REQ_PARAM,
                    jobDetailsUpdated.job_name,
                )
                .withRequestParam(JOB_DETAILS_REQ_PARAM, jobDetailsUpdated),
            TASK_UPDATE_JOB_DESCRIPTION,
        );
    }

    private _doSubmitStatusUpdate(): void {
        const jobDeployment = this._extractJobDeployment();

        if (!jobDeployment) {
            console.log(
                'Status update will not be performed for job with no deployments.',
            );

            return;
        }

        const jobState: DataJob = {
            ...this.jobState,
            deployments: [
                {
                    ...this.jobState.deployments[0],
                    enabled: this.status.value === DataJobStatus.ENABLED,
                },
                ...this.jobState.deployments.slice(1),
            ],
        };

        this.dataJobsService.updateJob(
            this.model
                .withRequestParam(TEAM_NAME_REQ_PARAM, this.jobDetails.team)
                .withRequestParam(JOB_NAME_REQ_PARAM, this.jobDetails.job_name)
                .withRequestParam(JOB_DEPLOYMENT_ID_REQ_PARAM, jobDeployment.id)
                .withRequestParam(
                    JOB_STATUS_REQ_PARAM,
                    this.status.value === DataJobStatus.ENABLED,
                )
                .withRequestParam(JOB_STATE_REQ_PARAM, jobState),
            TASK_UPDATE_JOB_STATUS,
        );
    }

    private _initializeNextRunDate(): void {
        this.next = ParseEpochPipe.transform(
            this.jobState?.config?.schedule?.nextRunEpochSeconds,
        );
    }

    private _subscribeForExecutions(): void {
        this.subscriptions.push(
            this.dataJobsService
                .getNotifiedForJobExecutions()
                .subscribe((executions) => {
                    this.jobExecutions = executions;
                }),
        );
    }

    private _resetJobDetails(): void {
        if (!this.jobDetails) {
            this.jobDetails = {};
        }
    }
}
