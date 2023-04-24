/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { DataJobBasePO } from '../../../../application/data-job-base.po';

export class DataJobManageExecutionsPage extends DataJobBasePO {
    static getPage() {
        return new DataJobManageExecutionsPage();
    }

    static navigateTo(teamName, jobName) {
        return super.navigateToUrl(`/manage/data-jobs/${teamName}/${jobName}/executions`);
    }

    /* Utils */

    /**
     * @example
     *
     *      - val=1m 34s
     *      - val=45s
     */
    convertStringContentToSeconds(val) {
        const params = val.split(' ');

        if (params.length === 2) {
            return parseInt(params[0].trim().replace(/m$/, ''), 10) * 60 + parseInt(params[1].trim().replace(/s$/, ''), 10);
        } else {
            return parseInt(params[0].trim().replace(/s$/, ''), 10);
        }
    }

    /* Selectors */

    // General

    getExecRefreshBtn() {
        return cy.get('[data-cy=data-pipelines-job-executions-refresh-btn');
    }

    getExecLoadingSpinner() {
        return cy.get('[data-cy=data-pipelines-job-executions-loading-spinner]');
    }

    // Charts

    getStatusChart() {
        return cy.get('[data-cy=data-pipelines-job-executions-status-chart]');
    }

    getDurationChart() {
        return cy.get('[data-cy=data-pipelines-job-executions-duration-chart]');
    }

    getTimePeriod() {
        return cy.get('[data-cy=data-pipelines-job-executions-time-period]');
    }

    // DataGrid

    getDataGrid() {
        return cy.get('[data-cy=data-pipelines-job-executions-datagrid]');
    }

    getDataGridPopupFilter() {
        return cy.get('.datagrid-filter.clr-popover-content');
    }

    getDataGridInputFilter() {
        return this.getDataGridPopupFilter().should('exist').find('input');
    }

    getDataGridPopupFilterCloseBtn() {
        return this.getDataGridPopupFilter().should('exist').find('.close');
    }

    getDataGridSpinner() {
        return this.getDataGrid().should('exist').find('.datagrid-spinner');
    }

    // Header

    getDataGridExecStatusHeader() {
        return this.getDataGrid().should('exist').find('[data-cy=data-pipelines-job-executions-status-header]');
    }

    getDataGridExecStatusFilterOpenerBtn() {
        return this.getDataGridExecStatusHeader().should('exist').find('.datagrid-filter-toggle');
    }

    getDataGridExecStatusFilters() {
        return this.getDataGridPopupFilter().should('exist').find('[data-cy=data-pipelines-job-executions-status-filters]');
    }

    getDataGridExecTypeHeader() {
        return this.getDataGrid().should('exist').find('[data-cy=data-pipelines-job-executions-type-header]');
    }

    getDataGridExecTypeFilterOpenerBtn() {
        return this.getDataGridExecTypeHeader().should('exist').find('.datagrid-filter-toggle');
    }

    getDataGridExecTypeFilters() {
        return this.getDataGridPopupFilter().should('exist').find('[data-cy=data-pipelines-job-executions-type-filters]');
    }

    getDataGridExecDurationHeader() {
        return this.getDataGrid().should('exist').find('[data-cy=data-pipelines-job-executions-duration-header]');
    }

    getDataGridExecDurationSortBtn() {
        return this.getDataGridExecDurationHeader().should('exist').find('.datagrid-column-title');
    }

    getDataGridExecStartHeader() {
        return this.getDataGrid().should('exist').find('[data-cy=data-pipelines-job-executions-start-header]');
    }

    getDataGridExecStartSortBtn() {
        return this.getDataGridExecStartHeader().should('exist').find('.datagrid-column-title');
    }

    getDataGridExecEndHeader() {
        return this.getDataGrid().should('exist').find('[data-cy=data-pipelines-job-executions-end-header]');
    }

    getDataGridExecEndSortBtn() {
        return this.getDataGridExecEndHeader().should('exist').find('.datagrid-column-title');
    }

    getDataGridExecIDHeader() {
        return this.getDataGrid().should('exist').find('[data-cy=data-pipelines-job-executions-id-header]');
    }

    getDataGridExecIDFilterOpenerBtn() {
        return this.getDataGridExecIDHeader().should('exist').find('.datagrid-filter-toggle');
    }

    getDataGridExecVersionHeader() {
        return this.getDataGrid().should('exist').find('[data-cy=data-pipelines-job-executions-version-header]');
    }

    getDataGridExecVersionFilterOpenerBtn() {
        return this.getDataGridExecVersionHeader().should('exist').find('.datagrid-filter-toggle');
    }

    // Rows and Cells

    getDataGridRows() {
        return this.getDataGrid().should('exist').find('clr-dg-row.datagrid-row');
    }

    getDataGridRow(rowIndex) {
        return this.getDataGridRows()
            .should('have.length.gte', rowIndex - 1)
            .then((rows) => Array.from(rows)[rowIndex - 1]);
    }

    getDataGridCells(rowIndex) {
        return this.getDataGridRow(rowIndex).should('exist').find('clr-dg-cell.datagrid-cell');
    }

    getDataGridCellByIndex(rowIndex, cellIndex) {
        if (rowIndex) {
            return this.getDataGridCells(rowIndex)
                .should('have.length.gte', cellIndex - 1)
                .then((cells) => Array.from(cells)[cellIndex - 1]);
        }

        return this.getDataGridRows()
            .should('have.length.gte', 0)
            .then(($rows) => {
                const _rows = $rows.reduce((accumulator, row) => {
                    const _cells = Array.from(row.querySelectorAll('clr-dg-cell.datagrid-cell'));

                    if (_cells[cellIndex - 1]) {
                        accumulator.push(_cells[cellIndex - 1]);
                    }

                    return accumulator;
                }, []);

                return _rows;
            });
    }

    getDataGridCellByIdentifier(rowIndex, identifier) {
        return this.getDataGridRow(rowIndex).should('exist').find(identifier);
    }

    getDataGridExecTypeCell(rowIndex) {
        return this.getDataGridCellByIdentifier(rowIndex, '[data-cy=data-pipelines-job-executions-type-cell]');
    }

    getDataGridExecTypeContainer(rowIndex) {
        return this.getDataGridExecTypeCell(rowIndex).should('exist').find('[data-cy=data-pipelines-job-executions-type-container]');
    }

    getDataGridExecDurationCell(rowIndex) {
        return this.getDataGridCellByIdentifier(rowIndex, '[data-cy=data-pipelines-job-executions-duration-cell]');
    }

    getDataGridExecStartCell(rowIndex) {
        return this.getDataGridCellByIdentifier(rowIndex, '[data-cy=data-pipelines-job-executions-start-cell]');
    }

    getDataGridExecEndCell(rowIndex) {
        return this.getDataGridCellByIdentifier(rowIndex, '[data-cy=data-pipelines-job-executions-end-cell]');
    }

    // Pagination

    getDataGridPagination() {
        return this.getDataGrid().should('exist').find('[data-cy=data-pipelines-job-executions-datagrid-pagination]');
    }

    /* Actions */

    // General

    refreshExecData() {
        this.getExecRefreshBtn().should('exist').click({ force: true });
    }

    // DataGrid

    typeToFilterInput(value) {
        this.getDataGridInputFilter().should('exist').type(value);

        this.waitForViewToRenderShort();
    }

    clearFilterInput() {
        this.getDataGridInputFilter().should('exist').clear({ force: true });

        this.waitForViewToRenderShort();
    }

    closeFilter() {
        this.getDataGridPopupFilterCloseBtn().should('exist').click({ force: true });

        this.waitForViewToRenderShort();
    }

    // Header

    openStatusFilter() {
        this.getDataGridExecStatusFilterOpenerBtn().should('exist').click({ force: true });

        this.waitForViewToRenderShort();
    }

    openTypeFilter() {
        this.getDataGridExecTypeFilterOpenerBtn().should('exist').click({ force: true });

        this.waitForViewToRenderShort();
    }

    openIDFilter() {
        this.getDataGridExecIDFilterOpenerBtn().should('exist').click({ force: true });

        this.waitForViewToRenderShort();
    }

    openVersionFilter() {
        this.getDataGridExecVersionFilterOpenerBtn().should('exist').click({ force: true });

        this.waitForViewToRenderShort();
    }

    sortByExecDuration() {
        this.getDataGridExecDurationSortBtn().should('exist').click({ force: true });

        this.waitForViewToRenderShort();
    }

    sortByExecStart() {
        this.getDataGridExecStartSortBtn().should('exist').click({ force: true });

        this.waitForViewToRenderShort();
    }

    sortByExecEnd() {
        this.getDataGridExecEndSortBtn().should('exist').click({ force: true });

        this.waitForViewToRenderShort();
    }
}
