/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { DatePipe } from '@angular/common';
import { Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges } from '@angular/core';

import { ActiveElement, Chart, ChartData, registerables, ScatterDataPoint, TimeUnit } from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import zoomPlugin from 'chartjs-plugin-zoom';
import 'chartjs-adapter-date-fns';

import { CollectionsUtil } from '@versatiledatakit/shared';

import { DateUtil } from '../../../../../shared/utils';

import { DATA_PIPELINES_DATE_TIME_FORMAT, DataJobExecutionStatus } from '../../../../../model';

import { DataJobExecutionToGridDataJobExecution, GridDataJobExecution } from '../model';

type CustomChartData = Partial<ScatterDataPoint> & {
    startTime: number;
    duration: number;
    endTime: string;
    status: DataJobExecutionStatus;
    opId: string;
    id: string;
};

interface ZoomPeriod {
    from: Date;
    to: Date;
}

@Component({
    selector: 'lib-execution-duration-chart',
    templateUrl: './execution-duration-chart.component.html',
    styleUrls: ['./execution-duration-chart.component.scss'],
    providers: [DatePipe]
})
export class ExecutionDurationChartComponent implements OnInit, OnChanges {
    @Input() jobExecutions: GridDataJobExecution[] = [];

    /**
     * ** Flag that indicates if duration chart is zoomed or not.
     */
    @Input() chartZoomed = false;

    /**
     * ** Emits event whenever focus on execution changes.
     *
     *      - Value could be either executionId or null.
     */
    @Output() executionIdFocused = new EventEmitter<CustomChartData['id']>();

    /**
     * ** Event Emitter that emits events on every user zoom period change in duration chart or reset zoom.
     */
    @Output() zoomPeriodChanged: EventEmitter<ZoomPeriod> = new EventEmitter<ZoomPeriod>();

    /**
     * ** Reference to Duration chart instance.
     */
    chart: Chart<'line', CustomChartData[], number>;

    /**
     * ** Currently focussed execution id, it could be either string if there is focussed execution or null if nothing is focussed.
     * @private
     */
    private _focusedExecutionId: CustomChartData['id'];

    /**
     * ** Zoom selection reference with from and to values.
     * @private
     */
    private _zoomPeriod: ZoomPeriod = {
        from: null,
        to: null
    };

    constructor(private readonly datePipe: DatePipe) {
        Chart.register(...registerables, ChartDataLabels, zoomPlugin);
    }

    resetZoom() {
        this._zoomPeriod = {
            from: null,
            to: null
        };

        this.zoomPeriodChanged.next(this._zoomPeriod);
    }

    /**
     * @inheritDoc
     */
    ngOnChanges(changes: SimpleChanges): void {
        if (!changes['jobExecutions'].firstChange) {
            this._updateChart();
        }
    }

    /**
     * @inheritDoc
     */
    ngOnInit(): void {
        this._initChart();
    }

    private _initChart(): void {
        const chartData: CustomChartData[] = this._getChartData();
        const unit: TimeUnit = this._getTimeScaleUnit(chartData);
        const [min, max] = this._getMinMaxExecutionTupleAdjusted(chartData, unit);

        const data: ChartData<'line', CustomChartData[], number> = {
            labels: this._getChartLabels(),
            datasets: [
                {
                    data: chartData,
                    fill: false,
                    pointRadius: 3,
                    pointBorderColor: (context) =>
                        DataJobExecutionToGridDataJobExecution.resolveColor((context.raw as { status: string })?.status),
                    pointBackgroundColor: (context) =>
                        DataJobExecutionToGridDataJobExecution.resolveColor((context.raw as { status: string })?.status),
                    pointBorderWidth: 3,
                    parsing: {
                        xAxisKey: 'startTime',
                        yAxisKey: 'duration'
                    }
                }
            ]
        };

        this.chart = new Chart<'line', CustomChartData[], number>('durationChart', {
            type: 'line',
            data,
            options: {
                // callback listen for hover events in duration chart and process events
                onHover: (event, activeElements) => {
                    this._emitFocussedExecutionId(activeElements);
                },
                showLine: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit
                        },
                        min,
                        max
                    },
                    y: {
                        title: {
                            display: true,
                            text: `Duration ${this._getDurationUnit().name}`
                        }
                    }
                },
                maintainAspectRatio: false,
                plugins: {
                    zoom: {
                        zoom: {
                            drag: {
                                enabled: true
                            },
                            mode: 'x',
                            onZoomComplete: (context) => {
                                const from = new Date(Math.floor(context.chart.scales['x'].min));
                                const to = new Date(Math.ceil(context.chart.scales['x'].max));

                                if (this._zoomPeriod.from === from && this._zoomPeriod.to === to) {
                                    return;
                                }

                                this._zoomPeriod = {
                                    from,
                                    to
                                };

                                this.zoomPeriodChanged.next(this._zoomPeriod);
                            }
                        }
                    },
                    datalabels: {
                        display: false
                    },
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const rawValues = context.raw as CustomChartData;

                                // eslint-disable-next-line @typescript-eslint/restrict-plus-operands
                                return (
                                    `Duration: ${context.parsed.y} | ${rawValues.status}` +
                                    (rawValues.endTime
                                        ? ` | End: ${this.datePipe.transform(rawValues.endTime, DATA_PIPELINES_DATE_TIME_FORMAT, 'UTC')}`
                                        : '')
                                );
                            }
                        }
                    }
                }
            }
        });
    }

    private _updateChart(): void {
        const chartLabels: number[] = this._getChartLabels();
        const chartData: CustomChartData[] = this._getChartData();
        const unit: TimeUnit = this._getTimeScaleUnit(chartData);
        const [min, max] = this._getMinMaxExecutionTupleAdjusted(chartData, unit);

        this.chart.data.labels = chartLabels;
        this.chart.data.datasets[0].data = chartData;

        this.chart.options.scales['x'] = {
            type: 'time',
            time: {
                unit
            },
            min,
            max
        };

        this.chart.update();
    }

    private _getChartLabels(): number[] {
        return this.jobExecutions.map((execution) => DateUtil.normalizeToUTC(execution.startTime).getTime());
    }

    private _getChartData(): CustomChartData[] {
        const divider = this._getDurationUnit().divider;

        return this.jobExecutions
            .map((execution) => {
                return {
                    startTime: DateUtil.normalizeToUTC(execution.startTime).getTime(),
                    duration: Math.round((this._getJobDurationSeconds(execution) / divider) * 100) / 100,
                    endTime: execution.endTime ? execution.endTime : undefined,
                    status: execution.status,
                    opId: execution.opId,
                    id: execution.id
                } as CustomChartData;
            })
            .sort((ex1, ex2) => ex1.startTime - ex2.startTime);
    }

    private _getTimeScaleUnit(chartData: CustomChartData[]): TimeUnit {
        const [min, max] = this._getMinMaxExecutionTuple(chartData);

        if (CollectionsUtil.isNil(min) || CollectionsUtil.isNil(max)) {
            return 'day';
        }

        const _min = CollectionsUtil.isNumber(min) ? min : new Date(min).getTime();
        const _max = CollectionsUtil.isNumber(max) ? max : new Date(max).getTime();
        const diff = _max - _min;

        if (diff > this._getTimeUnitMilliseconds('year') + this._getTimeUnitMilliseconds('second')) {
            return 'year';
        }

        if (diff > this._getTimeUnitMilliseconds('month') + this._getTimeUnitMilliseconds('second')) {
            return 'month';
        }

        if (diff > 2 * this._getTimeUnitMilliseconds('week')) {
            return 'week';
        }

        if (diff > this._getTimeUnitMilliseconds('day') + this._getTimeUnitMilliseconds('second')) {
            return 'day';
        }

        if (diff > this._getTimeUnitMilliseconds('hour') + this._getTimeUnitMilliseconds('second')) {
            return 'hour';
        }

        if (diff > this._getTimeUnitMilliseconds('minute') + this._getTimeUnitMilliseconds('millisecond')) {
            return 'minute';
        }

        if (diff > this._getTimeUnitMilliseconds('second') + this._getTimeUnitMilliseconds('millisecond')) {
            return 'second';
        }

        return 'millisecond';
    }

    private _getDurationUnit(): { name: string; divider: number } {
        const maxDurationSeconds = this._getMaxDurationSeconds();

        if (maxDurationSeconds > 60) {
            return maxDurationSeconds > 3600 ? { name: 'hours', divider: 3600 } : { name: 'minutes', divider: 60 };
        } else {
            return { name: 'seconds', divider: 1 };
        }
    }

    private _getMaxDurationSeconds(): number {
        return this.jobExecutions
            .map((execution) => this._getJobDurationSeconds(execution))
            .sort((v1, v2) => v1 - v2)
            .pop();
    }

    private _getJobDurationSeconds(execution: GridDataJobExecution): number {
        const endTime = execution.endTime ? new Date(execution.endTime).getTime() : Date.now();
        const delta = endTime - new Date(execution.startTime).getTime();

        return delta / 1000;
    }

    private _emitFocussedExecutionId(activeElements: ActiveElement[]): void {
        if (activeElements.length > 0) {
            const element: { $context?: { raw?: CustomChartData } } = activeElements[0].element as unknown;
            const executionId = element?.$context?.raw?.id ?? null;

            // if event emits that element is focussed and that value is same as previous skip processing
            if (this._focusedExecutionId === executionId) {
                return;
            }

            // when element is focused for the first time, save executionId in component context
            this._focusedExecutionId = executionId;
            // emit executionId to parent component
            this.executionIdFocused.next(executionId);
        } else {
            // if event emits that no element is focussed and that value is same as previous skip processing
            if (!this._focusedExecutionId) {
                return;
            }

            // when focused element lose focus clear executionId from component context
            this._focusedExecutionId = null;
            // emit null value to parent component
            this.executionIdFocused.next(null);
        }
    }

    private _getMinMaxExecutionTuple(chartData: CustomChartData[]): [number, number] {
        if (chartData.length === 0) {
            if (CollectionsUtil.isDate(this._zoomPeriod.from) && CollectionsUtil.isDate(this._zoomPeriod.to)) {
                return [this._zoomPeriod.from.getTime(), this._zoomPeriod.to.getTime()];
            }

            return [null, null];
        }

        if (chartData.length === 1) {
            if (CollectionsUtil.isDate(this._zoomPeriod.from) && CollectionsUtil.isDate(this._zoomPeriod.to)) {
                if (this._zoomPeriod.to.getTime() - this._zoomPeriod.from.getTime() > 5 * this._getTimeUnitMilliseconds('minute')) {
                    return [this._zoomPeriod.from.getTime(), this._zoomPeriod.to.getTime()];
                }
            }

            return [chartData[0].startTime, chartData[0].startTime];
        }

        return [chartData[0].startTime, chartData[chartData.length - 1].startTime];
    }

    private _getMinMaxExecutionTupleAdjusted(chartData: CustomChartData[], unit: TimeUnit): [number, number] {
        const [min, max] = this._getMinMaxExecutionTuple(chartData);

        let adjustment: number;

        switch (unit) {
            case 'millisecond':
                adjustment = 10 * this._getTimeUnitMilliseconds('millisecond');
                break;
            case 'second':
                adjustment = 5 * this._getTimeUnitMilliseconds('second');
                break;
            case 'minute':
                adjustment = 5 * this._getTimeUnitMilliseconds('minute');
                break;
            case 'hour':
                adjustment = 2 * this._getTimeUnitMilliseconds('hour');
                break;
            case 'day':
                adjustment = 15 * this._getTimeUnitMilliseconds('hour');
                break;
            case 'week':
                adjustment = 3 * this._getTimeUnitMilliseconds('day');
                break;
            case 'month':
                adjustment = this._getTimeUnitMilliseconds('month');
                break;
            case 'year':
                adjustment = this._getTimeUnitMilliseconds('year');
                break;
            default:
                console.error(
                    // eslint-disable-next-line @typescript-eslint/restrict-template-expressions
                    `Taurus DataPipelines ExecutionDurationChartComponent unsupported time format unit ${unit}`
                );
        }

        return [min - adjustment, max + adjustment];
    }

    private _getTimeUnitMilliseconds(unit: 'millisecond' | 'second' | 'minute' | 'hour' | 'day' | 'week' | 'month' | 'year'): number {
        switch (unit) {
            case 'millisecond':
                return 1;
            case 'second':
                return 1000;
            case 'minute':
                return 1000 * 60;
            case 'hour':
                return 1000 * 60 * 60;
            case 'day':
                return 1000 * 60 * 60 * 24;
            case 'week':
                return 1000 * 60 * 60 * 24 * 7;
            case 'month':
                return 1000 * 60 * 60 * 24 * 31;
            case 'year':
                return 1000 * 60 * 60 * 24 * 365;
            default:
                console.error(
                    // eslint-disable-next-line @typescript-eslint/restrict-template-expressions
                    `Taurus DataPipelines ExecutionDurationChartComponent unsupported time format unit ${unit}`
                );

                return 0;
        }
    }
}
