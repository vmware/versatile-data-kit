/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ChangeDetectionStrategy, Component, Inject, Input } from '@angular/core';

import {
    DATA_PIPELINES_CONFIGS,
    DataJobExecution,
    DataJobExecutions,
    DataJobExecutionStatus,
    DataJobExecutionType,
    DataPipelinesConfig
} from '../../../model';

@Component({
    selector: 'lib-executions-timeline',
    templateUrl: './executions-timeline.component.html',
    styleUrls: ['./executions-timeline.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class ExecutionsTimelineComponent {
    static manualRunKnownUser = 'This job is triggered manually by user';
    static manualRunNoUser = 'This job is triggered manually, but there is no info about the user';

    @Input() jobExecutions: DataJobExecutions = [];
    @Input() next: Date = null;

    dataJobExecutionStatus = DataJobExecutionStatus;

    constructor(
        @Inject(DATA_PIPELINES_CONFIGS)
        public dataPipelinesModuleConfig: DataPipelinesConfig
    ) {}

    /**
     * ** NgFor elements tracking function.
     */
    trackByFn(index: number, execution: DataJobExecution): string {
        return `${index}|${execution.id}`;
    }

    isExecutionManual(execution: DataJobExecution): boolean {
        return execution?.type === DataJobExecutionType.MANUAL;
    }

    getManualExecutedByTitle(execution: DataJobExecution): string {
        if (!execution || !execution.startedBy || !execution.startedBy.startsWith('manual/')) {
            // execution has no info abot user provided
            return ExecutionsTimelineComponent.manualRunNoUser;
        }

        const user = execution.startedBy.replace('manual/', '');

        return `${ExecutionsTimelineComponent.manualRunKnownUser} ${user}`;
    }
}
