/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { DatePipe, formatDate } from '@angular/common';
import { Component, Input, OnChanges, OnInit, SimpleChanges } from '@angular/core';

import { Chart, ChartData, registerables, ScatterDataPoint, TimeUnit } from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import zoomPlugin from 'chartjs-plugin-zoom';
import 'chartjs-adapter-date-fns';

import { CollectionsUtil } from '@versatiledatakit/shared';

import { DateUtil } from '../../../../../shared/utils';

import { DataJobExecutionStatus } from '../../../../../model';

import { DataJobExecutionToGridDataJobExecution, GridDataJobExecution } from '../model';

type CustomChartData = ScatterDataPoint & {
    startTime: number;
    duration: number;
    endTime: number;
    status: DataJobExecutionStatus;
    opId: string;
};

@Component({
    selector: 'lib-execution-duration-chart',
    templateUrl: './execution-duration-chart.component.html',
    styleUrls: ['./execution-duration-chart.component.scss'],
    providers: [DatePipe]
})
export class ExecutionDurationChartComponent implements OnInit, OnChanges {
    @Input() jobExecutions: GridDataJobExecution[] = [];

    chartZoomed = false;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    chart: Chart<'line', any, unknown>;

    constructor() {
        Chart.register(...registerables, ChartDataLabels, zoomPlugin);
    }

    getChartLabels(): number[] {
        return this.jobExecutions.map((execution) => DateUtil.normalizeToUTC(execution.startTime).getTime());
    }

    getData(min?: number, max?: number): CustomChartData[] {
        const divider = this.getDurationUnit().divider;
        const executions = CollectionsUtil.isDefined(min)
            ? this.jobExecutions.filter((ex) => {
                  const startTime = DateUtil.normalizeToUTC(ex.startTime).getTime();

                  return startTime >= min && startTime <= max;
              })
            : this.jobExecutions;

        return executions.map((execution) => {
            return {
                startTime: DateUtil.normalizeToUTC(execution.startTime).getTime(),
                duration: Math.round((this.getJobDurationSeconds(execution) / divider) * 100) / 100,
                endTime: execution.endTime ? new Date(execution.endTime) : undefined,
                status: execution.status,
                opId: execution.opId
            } as unknown as CustomChartData;
        });
    }

    getMaxDurationSeconds(): number {
        return this.jobExecutions
            .map((execution) => this.getJobDurationSeconds(execution))
            .reduce((prev, current) => (prev > current ? prev : current));
    }

    getJobDurationSeconds(execution: GridDataJobExecution) {
        return (
            ((execution.endTime ? new Date(execution.endTime).getTime() : new Date(Date.now()).getTime()) -
                new Date(execution.startTime).getTime()) /
            1000
        );
    }

    getDurationUnit(): { name: string; divider: number } {
        const maxDurationSeconds = this.getMaxDurationSeconds();

        if (maxDurationSeconds > 60) {
            return maxDurationSeconds > 3600 ? { name: 'hours', divider: 3600 } : { name: 'minutes', divider: 60 };
        } else {
            return { name: 'seconds', divider: 1 };
        }
    }

    resetZoom() {
        this._adjustTimeScaleUnit(null);
        this.chartZoomed = false;
        this.chart.resetZoom();
    }

    /**
     * @inheritDoc
     */
    ngOnChanges(changes: SimpleChanges): void {
        if (!changes['jobExecutions'].firstChange) {
            this.chart.data.labels = this.getChartLabels();
            this.chart.data.datasets[0].data = this.getData();
            this.chart.update();
        }
    }

    /**
     * @inheritDoc
     */
    ngOnInit(): void {
        this._initChart();
    }

    private _initChart(): void {
        const data: ChartData<'line'> = {
            labels: this.getChartLabels(),
            datasets: [
                {
                    data: this.getData(),
                    fill: false,
                    pointRadius: 3,
                    pointBorderColor: (context) =>
                        DataJobExecutionToGridDataJobExecution.resolveColor((context.raw as { status: string }).status),
                    pointBackgroundColor: (context) =>
                        DataJobExecutionToGridDataJobExecution.resolveColor((context.raw as { status: string }).status),
                    pointBorderWidth: 3,
                    parsing: {
                        xAxisKey: 'startTime',
                        yAxisKey: 'duration'
                    }
                }
            ]
        };

        this.chart = new Chart<'line'>('durationChart', {
            type: 'line',
            data,
            options: {
                showLine: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: this._getTimeScaleUnit(...this._getMinMaxExecutionTuple())
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: `Duration ${this.getDurationUnit().name}`
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
                                this._adjustTimeScaleUnit(context.chart);
                                this.chartZoomed = true;
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
                                const rawValues = context.raw as {
                                    status: string;
                                    endTime: Date;
                                };

                                // eslint-disable-next-line @typescript-eslint/restrict-plus-operands
                                return (
                                    `Duration: ${context.parsed.y}|${rawValues.status}` +
                                    (rawValues.endTime
                                        ? `|End: ${formatDate(rawValues.endTime, 'MMM d, y, hh:mm:ss a', 'en-US', 'UTC')}`
                                        : '')
                                );
                            }
                        }
                    }
                }
            }
        });
    }

    private _adjustTimeScaleUnit(chart: Chart): void {
        let unit: TimeUnit;
        let min: number = null;
        let max: number = null;

        if (CollectionsUtil.isDefined(chart)) {
            min = chart.scales['x'].min;
            max = chart.scales['x'].max;

            unit = this._getTimeScaleUnit(min, max);
        } else {
            unit = this._getTimeScaleUnit(...this._getMinMaxExecutionTuple());
        }

        this.chart.options.scales['x'] = {
            type: 'time',
            time: {
                unit
            },
            min,
            max
        };

        this.chart.data.datasets[0].data = this.getData(min, max);

        this.chart.update();
    }

    private _getMinMaxExecutionTuple(): [number, number] {
        const executions = this.getData();

        if (executions.length < 2) {
            return [null, null];
        }

        return [executions[0].startTime, executions[executions.length - 1].startTime];
    }

    private _getTimeScaleUnit(min: number | string, max: number | string): TimeUnit {
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
