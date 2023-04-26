/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnChanges, OnInit, SimpleChanges } from '@angular/core';

import { Chart, registerables } from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';

import { DataJobExecutionToGridDataJobExecution, GridDataJobExecution } from '../model/data-job-execution';

@Component({
    selector: 'lib-execution-status-chart',
    templateUrl: './execution-status-chart.component.html',
    styleUrls: ['./execution-status-chart.component.scss']
})
export class ExecutionStatusChartComponent implements OnInit, OnChanges {
    @Input() jobExecutions: GridDataJobExecution[];

    totalExecutions: number;
    chart: Chart;

    constructor() {
        Chart.register(...registerables, ChartDataLabels);
    }

    getDoughnutLabels(): string[] {
        return this.jobExecutions.map((execution) => execution.status as string).filter((item, i, ar) => ar.indexOf(item) === i);
    }

    getDoughnutData(): number[] {
        const data: number[] = [];

        this.getDoughnutLabels().forEach((label) =>
            data.push(this.jobExecutions.filter((execution) => (execution.status as string) === label).length)
        );

        return data;
    }

    getDoughnutLabelColors(): string[] {
        const colors: string[] = [];
        const statusColorMap = DataJobExecutionToGridDataJobExecution.getStatusColorsMap();

        this.getDoughnutLabels().forEach((label) => {
            colors.push(statusColorMap[label] as string);
        });

        return colors;
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (!changes['jobExecutions'].isFirstChange()) {
            this.totalExecutions = this.jobExecutions.length;
            this.chart.data.labels = this.getDoughnutLabels();
            this.chart.data.datasets[0].backgroundColor = this.getDoughnutLabelColors();
            this.chart.data.datasets[0].data = this.getDoughnutData();
            this.chart.update();
        }
    }

    ngOnInit(): void {
        this.totalExecutions = this.jobExecutions.length;

        const data = {
            labels: this.getDoughnutLabels(),
            datasets: [
                {
                    data: this.getDoughnutData(),
                    backgroundColor: this.getDoughnutLabelColors(),
                    hoverOffset: 4
                }
            ]
        };

        this.chart = new Chart('statusChart', {
            type: 'doughnut',
            data,
            options: {
                spacing: 1,
                elements: {
                    arc: {
                        borderWidth: 0
                    }
                },
                cutout: 70,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false,
                        position: 'left'
                    },
                    datalabels: {
                        color: 'black',
                        font: {
                            size: 16
                        }
                    },
                    tooltip: {
                        xAlign: 'center',
                        yAlign: 'center'
                    }
                }
            }
        });
    }
}
