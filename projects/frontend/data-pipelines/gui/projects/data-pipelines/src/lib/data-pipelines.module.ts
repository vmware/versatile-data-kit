/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ModuleWithProviders, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { TruncateModule } from '@yellowspot/ng-truncate';

import { NgxChartsModule } from '@swimlane/ngx-charts';

import { TimeagoModule } from 'ngx-timeago';
import { LottieModule } from 'ngx-lottie';

import { DpDatePickerModule } from 'ng2-date-picker';

import {
    ClarityModule,
    ClrDatagridModule,
    ClrSpinnerModule,
} from '@clr/angular';

import { VdkComponentsModule } from '@versatiledatakit/shared';

import { TaurusSharedNgRxModule } from '@versatiledatakit/shared';

import { AttributesDirective } from './shared/directives';

import {
    ContactsPresentPipe,
    ExecutionSuccessRatePipe,
    ExtractContactsPipe,
    ExtractJobStatusPipe,
    FormatDeltaPipe,
    FormatSchedulePipe,
    ParseEpochPipe,
    ParseNextRunPipe,
} from './shared/pipes';

import {
    ColumnFilterComponent,
    ConfirmationDialogModalComponent,
    DeleteModalComponent,
    EmptyStateComponent,
    ExecutionsTimelineComponent,
    GridActionComponent,
    QuickFiltersComponent,
    StatusCellComponent,
    StatusPanelComponent,
    WidgetValueComponent,
} from './shared/components';

import {
    DataJobsApiService,
    DataJobsBaseApiService,
    DataJobsPublicApiService,
    DataJobsService,
    DataJobsServiceImpl,
} from './services';

import { DATA_PIPELINES_CONFIGS, DataPipelinesConfig } from './model';

import { DataJobsEffects } from './state/effects';

import { FormatDurationPipe } from './shared/pipes/format-duration.pipe';

import { DataJobsExplorePageComponent } from './components/data-jobs-explore';
import { DataJobsExploreGridComponent } from './components/data-jobs-explore/components/grid';

import { DataJobsManagePageComponent } from './components/data-jobs-manage';
import { DataJobsManageGridComponent } from './components/data-jobs-manage/components/grid';

import { DataJobPageComponent } from './components/data-job';
import { DataJobDetailsPageComponent } from './components/data-job/pages/details';
import {
    DataJobDeploymentDetailsModalComponent,
    DataJobExecutionsGridComponent,
    DataJobExecutionsPageComponent,
    DataJobExecutionStatusComponent,
    DataJobExecutionStatusFilterComponent,
    DataJobExecutionTypeComponent,
    DataJobExecutionTypeFilterComponent,
    ExecutionDurationChartComponent,
    ExecutionStatusChartComponent,
    TimePeriodFilterComponent,
} from './components/data-job/pages/executions';

import {
    DataJobsExecutionsWidgetComponent,
    DataJobsFailedWidgetComponent,
    DataJobsHealthPanelComponent,
    DataJobsWidgetOneComponent,
    WidgetExecutionStatusGaugeComponent,
} from './components/widgets';

const routes: Routes = [];

@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(routes),
        VdkComponentsModule.forRoot(),
        ClrDatagridModule,
        ClrSpinnerModule,
        ClarityModule,
        LottieModule,
        FormsModule,
        ReactiveFormsModule,
        TruncateModule,
        TimeagoModule.forRoot(),
        TaurusSharedNgRxModule.forFeatureEffects([DataJobsEffects]),
        DpDatePickerModule,
        NgxChartsModule,
    ],
    declarations: [
        AttributesDirective,
        FormatDeltaPipe,
        FormatSchedulePipe,
        ParseNextRunPipe,
        ContactsPresentPipe,
        ExecutionSuccessRatePipe,
        ExtractJobStatusPipe,
        ExtractContactsPipe,
        ParseEpochPipe,
        DataJobsExplorePageComponent,
        DataJobsExploreGridComponent,
        DataJobsManagePageComponent,
        DataJobsManageGridComponent,
        DataJobPageComponent,
        DataJobDetailsPageComponent,
        DataJobExecutionsPageComponent,
        DataJobExecutionTypeComponent,
        DataJobExecutionStatusFilterComponent,
        DataJobDeploymentDetailsModalComponent,
        DataJobExecutionsGridComponent,
        DataJobExecutionTypeFilterComponent,
        TimePeriodFilterComponent,
        ExecutionStatusChartComponent,
        ExecutionDurationChartComponent,
        DataJobExecutionStatusComponent,
        DeleteModalComponent,
        ConfirmationDialogModalComponent,
        GridActionComponent,
        StatusCellComponent,
        StatusPanelComponent,
        ExecutionsTimelineComponent,
        // Widgets
        DataJobsWidgetOneComponent,
        WidgetValueComponent,
        ColumnFilterComponent,
        FormatDurationPipe,
        QuickFiltersComponent,
        DataJobsExecutionsWidgetComponent,
        DataJobsFailedWidgetComponent,
        WidgetExecutionStatusGaugeComponent,
        DataJobsHealthPanelComponent,
        EmptyStateComponent,
    ],
    exports: [
        DataJobsExplorePageComponent,
        DataJobsExploreGridComponent,
        DataJobsManagePageComponent,
        DataJobsManageGridComponent,
        DataJobPageComponent,
        DataJobDetailsPageComponent,
        DataJobExecutionsPageComponent,
        DataJobsWidgetOneComponent,
        DataJobsExecutionsWidgetComponent,
        DataJobsFailedWidgetComponent,
        WidgetExecutionStatusGaugeComponent,
        DataJobsHealthPanelComponent,
    ],
})
export class DataPipelinesModule {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    static forRoot(
        config: DataPipelinesConfig = {} as any,
    ): ModuleWithProviders<DataPipelinesModule> {
        return {
            ngModule: DataPipelinesModule,
            providers: [
                DataJobsBaseApiService,
                DataJobsPublicApiService,
                DataJobsApiService,
                { provide: DataJobsService, useClass: DataJobsServiceImpl },
                { provide: DATA_PIPELINES_CONFIGS, useValue: config },
            ],
        };
    }
}
