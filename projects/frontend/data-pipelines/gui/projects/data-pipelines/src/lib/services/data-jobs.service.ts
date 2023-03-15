/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/naming-convention */

import { Injectable } from '@angular/core';

import { BehaviorSubject, Observable, Subject } from 'rxjs';

import { ComponentModel, ComponentService } from '@versatiledatakit/shared';

import {
    FETCH_DATA_JOB,
    FETCH_DATA_JOB_EXECUTIONS,
    FETCH_DATA_JOBS,
    UPDATE_DATA_JOB,
} from '../state/actions';
import { DataJobUpdateTasks, TASK_LOAD_JOB_EXECUTIONS } from '../state/tasks';

import { DataJobExecutions } from '../model';

export abstract class DataJobsService {
    /**
     * ** Trigger Action for loading DataJobs data.
     */
    abstract loadJobs(model: ComponentModel): void;

    /**
     * ** Trigger Actions to load all necessary data for Data Job.
     */
    abstract loadJob(model: ComponentModel): void;

    /**
     * ** Trigger Action for loading Data Job executions data.
     */
    abstract loadJobExecutions(model: ComponentModel): void;

    /**
     * ** Trigger Action update Job.
     */
    abstract updateJob(model: ComponentModel, task: DataJobUpdateTasks): void;

    /**
     * ** Returns Observable(Subject) that fires when Running Job Execution ID change.
     */
    abstract getNotifiedForRunningJobExecutionId(): Observable<string>;

    /**
     * ** Send new event to Observable stream.
     */
    abstract notifyForRunningJobExecutionId(id: string): void;

    /**
     * ** Returns Observable(Subject) that fires with new Job Executions.
     */
    abstract getNotifiedForJobExecutions(): Observable<DataJobExecutions>;

    /**
     * ** Send new event to Observable stream.
     */
    abstract notifyForJobExecutions(executions: DataJobExecutions): void;

    /**
     * ** Returns Observable(BehaviorSubject) that fires with team name implicitly.
     */
    abstract getNotifiedForTeamImplicitly(): Observable<string>;

    /**
     * ** Send new event to Observable stream.
     */
    abstract notifyForTeamImplicitly(team: string): void;
}

@Injectable()
export class DataJobsServiceImpl extends DataJobsService {
    private readonly _runningJobExecutionId: Subject<string>;
    private readonly _jobExecutions: Subject<DataJobExecutions>;
    private readonly _implicitTeam: BehaviorSubject<string>;

    /**
     * ** Constructor.
     */
    constructor(private readonly componentService: ComponentService) {
        super();

        this._runningJobExecutionId = new Subject<string>();
        this._jobExecutions = new Subject<DataJobExecutions>();
        this._implicitTeam = new BehaviorSubject<string>(undefined);
    }

    /**
     * @inheritDoc
     */
    loadJobs(model: ComponentModel): void {
        this.componentService.load(model.getComponentState());
        this.componentService.dispatchAction(
            FETCH_DATA_JOBS,
            model.getComponentState(),
        );
    }

    loadJob(model: ComponentModel): void {
        this.componentService.load(model.getComponentState());
        this.componentService.dispatchAction(
            FETCH_DATA_JOB,
            model.getComponentState(),
        );
    }

    /**
     * @inheritDoc
     */
    loadJobExecutions(model: ComponentModel): void {
        this.componentService.load(model.getComponentState());
        this.componentService.dispatchAction(
            FETCH_DATA_JOB_EXECUTIONS,
            model.getComponentState(),
            TASK_LOAD_JOB_EXECUTIONS,
        );
    }

    /**
     * @inheritDoc
     */
    updateJob(model: ComponentModel, task: DataJobUpdateTasks): void {
        this.componentService.load(model.getComponentState());
        this.componentService.dispatchAction(
            UPDATE_DATA_JOB,
            model.getComponentState(),
            task,
        );
    }

    /**
     * @inheritDoc
     */
    getNotifiedForJobExecutions(): Observable<DataJobExecutions> {
        return this._jobExecutions.asObservable();
    }

    /**
     * @inheritDoc
     */
    notifyForJobExecutions(executions: DataJobExecutions): void {
        this._jobExecutions.next(executions);
    }

    /**
     * @inheritDoc
     */
    getNotifiedForRunningJobExecutionId(): Observable<string> {
        return this._runningJobExecutionId.asObservable();
    }

    /**
     * @inheritDoc
     */
    notifyForRunningJobExecutionId(id: string): void {
        this._runningJobExecutionId.next(id);
    }

    /**
     * @inheritDoc
     */
    getNotifiedForTeamImplicitly(): Observable<string> {
        return this._implicitTeam.asObservable();
    }

    /**
     * @inheritDoc
     */
    notifyForTeamImplicitly(team: string): void {
        this._implicitTeam.next(team);
    }
}
