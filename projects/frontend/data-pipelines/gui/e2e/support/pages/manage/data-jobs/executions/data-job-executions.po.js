/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { DataJobBasePO } from '../../../base/data-pipelines/data-job-base.po';
import { DataJobsBasePO } from '../../../base/data-pipelines/data-jobs-base.po';

export class DataJobManageExecutionsPage extends DataJobBasePO {
    /**
     * ** Returns instance of the page object.
     *
     * @returns {DataJobManageExecutionsPage}
     */
    static getPage() {
        return new DataJobManageExecutionsPage();
    }

    /**
     * @inheritDoc
     * @return {DataJobManageExecutionsPage}
     */
    static navigateTo(teamName, jobName) {
        /**
         * @type {DataJobManageExecutionsPage}
         */
        const page = super.navigateTo(
            'manage',
            teamName,
            jobName,
            'executions'
        );
        page.waitForGridToLoad(null);
        page.waitForViewToRenderShort();

        return page;
    }

    /**
     * ** Navigate to Data Job executions page with provided URL.
     *
     * @param {string} url
     * @return {DataJobManageExecutionsPage}
     */
    static navigateToExecutionsWithUrl(url) {
        const page = this.navigateToDataJobUrl(url, 3);

        page.waitForGridToLoad(null);
        page.waitForViewToRenderShort();

        return page;
    }

    /* Utils */

    /**
     * ** Converts from view time to seconds.
     *
     * @example
     *
     *      - val=1m 34s
     *      - val=45s
     *
     * @return {number}
     */
    convertStringContentToSeconds(val) {
        const params = val.trim().split(' ');

        if (params.length === 2) {
            return (
                parseInt(params[0].trim().replace(/m$/, ''), 10) * 60 +
                parseInt(params[1].trim().replace(/s$/, ''), 10)
            );
        } else {
            return parseInt(params[0].trim().replace(/s$/, ''), 10);
        }
    }

    /* Selectors */

    /**
     * ** Wait until Data grid is loaded.
     *
     * @param {string} contextSelector
     * @param {number} timeout
     * @returns {Cypress.Chainable<Subject>}
     */
    waitForGridToLoad(
        contextSelector,
        timeout = DataJobsBasePO.WAIT_SHORT_TASK
    ) {
        return this._waitForGridToLoad(
            'data-pipelines-data-job-executions',
            timeout
        );
    }

    // General

    getExecRefreshBtn() {
        return cy.get('[data-cy=data-pipelines-job-executions-refresh-btn');
    }

    getExecLoadingSpinner() {
        return cy.get(
            '[data-cy=data-pipelines-job-executions-loading-spinner]'
        );
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
        return cy.get('[data-cy=data-pipelines-job-executions-datagrid]', {
            timeout: DataJobManageExecutionsPage.WAIT_SHORT_TASK
        });
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

    // status
    getDataGridExecStatusHeader() {
        return this.getDataGrid()
            .should('exist')
            .find('[data-cy=data-pipelines-job-executions-status-header]');
    }

    getDataGridExecStatusFilterOpenerBtn() {
        return this.getDataGridExecStatusHeader()
            .should('exist')
            .find('.datagrid-filter-toggle');
    }

    getDataGridExecStatusFilters() {
        return this.getDataGridPopupFilter()
            .should('exist')
            .find('[data-cy=data-pipelines-job-executions-status-filters]');
    }

    getDataGridExecStatusSortBtn() {
        return this.getDataGridExecStatusHeader()
            .should('exist')
            .find('.datagrid-column-title');
    }

    /**
     * ** Get status filter label
     *
     * @param {'succeeded'|'platform_error'|'user_error'|'running'|'submitted'|'skipped'|'cancelled'} status
     * @return {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getDataGridExecStatusFilterLabel(status) {
        return cy.get(
            `[data-cy=dp-job-executions-status-filter-label-${status}]`
        );
    }

    /**
     * ** Get status filter checkbox
     *
     * @param {'succeeded'|'platform_error'|'user_error'|'running'|'submitted'|'skipped'|'cancelled'} status
     * @return {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getDataGridExecStatusFilterCheckbox(status) {
        return cy.get(
            `[data-cy=dp-job-executions-status-filter-checkbox-${status}]`
        );
    }

    getDataGridExecStatusFilterCheckboxesStatuses() {
        return cy
            .get('[data-cy=dp-job-executions-status-filter-checkbox] input')
            .then(($checkboxes) => {
                return cy.wrap(
                    Array.from($checkboxes).map((checkbox) => {
                        const key = checkbox
                            .getAttribute('data-cy')
                            .split('-')
                            .pop();
                        const value = checkbox.checked;

                        return [key, value];
                    })
                );
            });
    }

    // type
    getDataGridExecTypeHeader() {
        return this.getDataGrid()
            .should('exist')
            .find('[data-cy=data-pipelines-job-executions-type-header]');
    }

    getDataGridExecTypeFilterOpenerBtn() {
        return this.getDataGridExecTypeHeader()
            .should('exist')
            .find('.datagrid-filter-toggle');
    }

    getDataGridExecTypeSortBtn() {
        return this.getDataGridExecTypeHeader()
            .should('exist')
            .find('.datagrid-column-title');
    }

    /**
     * ** Get type filter label
     *
     * @param {'manual'|'scheduled'} type
     * @return {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getDataGridExecTypeFilterLabel(type) {
        return cy.get(`[data-cy=dp-job-executions-type-filter-label-${type}]`);
    }

    /**
     * ** Get type filter checkbox
     *
     * @param {'manual'|'scheduled'} type
     * @return {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getDataGridExecTypeFilterCheckbox(type) {
        return cy.get(
            `[data-cy=dp-job-executions-type-filter-checkbox-${type}]`
        );
    }

    getDataGridExecTypeFilterCheckboxesStatuses() {
        return cy
            .get('[data-cy=dp-job-executions-type-filter-checkbox] input')
            .then(($checkboxes) => {
                return cy.wrap(
                    Array.from($checkboxes).map((checkbox) => {
                        const key = checkbox
                            .getAttribute('data-cy')
                            .split('-')
                            .pop();
                        const value = checkbox.checked;

                        return [key, value];
                    })
                );
            });
    }

    // duration
    getDataGridExecDurationHeader() {
        return this.getDataGrid()
            .should('exist')
            .find('[data-cy=data-pipelines-job-executions-duration-header]');
    }

    getDataGridExecDurationFilterOpenerBtn() {
        return this.getDataGridExecDurationHeader()
            .should('exist')
            .find('.datagrid-filter-toggle');
    }

    getDataGridExecDurationSortBtn() {
        return this.getDataGridExecDurationHeader()
            .should('exist')
            .find('.datagrid-column-title');
    }

    // exec start
    getDataGridExecStartHeader() {
        return this.getDataGrid()
            .should('exist')
            .find('[data-cy=data-pipelines-job-executions-start-header]');
    }

    getDataGridExecStartFilterOpenerBtn() {
        return this.getDataGridExecStartHeader()
            .should('exist')
            .find('.datagrid-filter-toggle');
    }

    getDataGridExecStartSortBtn() {
        return this.getDataGridExecStartHeader()
            .should('exist')
            .find('.datagrid-column-title');
    }

    // exec end
    getDataGridExecEndHeader() {
        return this.getDataGrid()
            .should('exist')
            .find('[data-cy=data-pipelines-job-executions-end-header]');
    }

    getDataGridExecEndFilterOpenerBtn() {
        return this.getDataGridExecEndHeader()
            .should('exist')
            .find('.datagrid-filter-toggle');
    }

    getDataGridExecEndSortBtn() {
        return this.getDataGridExecEndHeader()
            .should('exist')
            .find('.datagrid-column-title');
    }

    // id
    getDataGridExecIDHeader() {
        return this.getDataGrid()
            .should('exist')
            .find('[data-cy=data-pipelines-job-executions-id-header]');
    }

    getDataGridExecIDFilterOpenerBtn() {
        return this.getDataGridExecIDHeader()
            .should('exist')
            .find('.datagrid-filter-toggle');
    }

    getDataGridExecIDSortBtn() {
        return this.getDataGridExecIDHeader()
            .should('exist')
            .find('.datagrid-column-title');
    }

    // version
    getDataGridExecVersionHeader() {
        return this.getDataGrid()
            .should('exist')
            .find('[data-cy=data-pipelines-job-executions-version-header]');
    }

    getDataGridExecVersionFilterOpenerBtn() {
        return this.getDataGridExecVersionHeader()
            .should('exist')
            .find('.datagrid-filter-toggle');
    }

    getDataGridExecVersionSortBtn() {
        return this.getDataGridExecVersionHeader()
            .should('exist')
            .find('.datagrid-column-title');
    }

    // Rows and Cells

    getDataGridRows() {
        return this.getDataGrid()
            .should('exist')
            .find('clr-dg-row.datagrid-row');
    }

    getDataGridRow(rowIndex) {
        return this.getDataGridRows()
            .should('have.length.gte', rowIndex - 1)
            .then((rows) => Array.from(rows)[rowIndex - 1]);
    }

    getDataGridCells(rowIndex) {
        return this.getDataGridRow(rowIndex)
            .should('exist')
            .find('clr-dg-cell.datagrid-cell');
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
                return $rows.reduce((accumulator, row) => {
                    const _cells = Array.from(
                        row.querySelectorAll('clr-dg-cell.datagrid-cell')
                    );

                    if (_cells[cellIndex - 1]) {
                        accumulator.push(_cells[cellIndex - 1]);
                    }

                    return accumulator;
                }, []);
            });
    }

    getDataGridCellByIdentifier(rowIndex, identifier) {
        return this.getDataGridRow(rowIndex).should('exist').find(identifier);
    }

    getDataGridCellsByIdentifier(identifier) {
        return this.getDataGrid().should('exist').find(identifier);
    }

    // type
    getDataGridExecTypeCell(rowIndex) {
        return this.getDataGridCellByIdentifier(
            rowIndex,
            '[data-cy=data-pipelines-job-executions-type-cell]'
        );
    }

    /**
     * ** Get containers in cells for given type.
     *
     * @param {'manual'|'scheduled'} type
     * @return {Cypress.Chainable<Array<string>>}
     */
    getDataGridExecTypeContainers(type) {
        return this.getDataGrid()
            .should('exist')
            .find('[data-cy=data-pipelines-job-executions-type-container]')
            .then(($containers) => {
                return cy.wrap(
                    Array.from($containers)
                        .map((container) =>
                            container.getAttribute('title').toLowerCase()
                        )
                        .filter((title) => new RegExp(`^${type}`).test(title))
                );
            });
    }

    // getDataGridExecStatusFilterCheckboxesStatuses() {
    //     return cy.get('[data-cy=dp-job-executions-status-filter-checkbox] input')
    //              .then(($checkboxes) => {
    //                  return cy.wrap(Array.from($checkboxes).map((checkbox) => {
    //                      const key = checkbox.getAttribute('data-cy').split('-').pop();
    //                      const value = checkbox.checked;
    //
    //                      return [key, value];
    //                  }));
    //              });
    // }

    // duration
    getDataGridExecDurationCell(rowIndex) {
        return this.getDataGridCellByIdentifier(
            rowIndex,
            '[data-cy=data-pipelines-job-executions-duration-cell]'
        );
    }

    // exec start
    getDataGridExecStartCell(rowIndex) {
        return this.getDataGridCellByIdentifier(
            rowIndex,
            '[data-cy=data-pipelines-job-executions-start-cell]'
        );
    }

    getDataGridExecStartCells() {
        return this.getDataGridCellsByIdentifier(
            '[data-cy=data-pipelines-job-executions-start-cell]'
        );
    }

    generateExecStartFilterValue() {
        return this.getDataGridExecStartCells().then(($cells) => {
            const pmCells = Array.from($cells).map((cell) =>
                /PM$/.test(`${cell.innerText?.trim()}`)
            );
            if (pmCells.length >= 2) {
                return cy.wrap('PM');
            }

            const amCells = Array.from($cells).map((cell) =>
                /AM$/.test(`${cell.innerText?.trim()}`)
            );
            if (amCells.length >= 2) {
                return cy.wrap('AM');
            }

            throw new Error('Unhandled use case in test scenarios');
        });
    }

    // exec end
    getDataGridExecEndCell(rowIndex) {
        return this.getDataGridCellByIdentifier(
            rowIndex,
            '[data-cy=data-pipelines-job-executions-end-cell]'
        );
    }

    getDataGridExecEndCells() {
        return this.getDataGridCellsByIdentifier(
            '[data-cy=data-pipelines-job-executions-end-cell]'
        );
    }

    generateExecEndFilterValue() {
        return this.getDataGridExecEndCells().then(($cells) => {
            const pmCells = Array.from($cells).map((cell) =>
                /PM$/.test(`${cell.innerText?.trim()}`)
            );

            if (pmCells.length > 0) {
                return cy.wrap('PM');
            }

            return cy.wrap('AM');
        });
    }

    // id
    getDataGridExecIDCell(rowIndex) {
        return this.getDataGridCellByIdentifier(
            rowIndex,
            '[data-cy=data-pipelines-job-executions-id-cell]'
        );
    }

    getDataGridExecIDCells() {
        return this.getDataGridCellsByIdentifier(
            '[data-cy=data-pipelines-job-executions-id-cell]'
        );
    }

    // exec version
    getDataGridExecVersionCell(rowIndex) {
        return this.getDataGridCellByIdentifier(
            rowIndex,
            '[data-cy=data-pipelines-job-executions-job-version-cell]'
        );
    }

    getDataGridExecVersionCells() {
        return this.getDataGridCellsByIdentifier(
            '[data-cy=data-pipelines-job-executions-job-version-cell]'
        );
    }

    // Pagination

    getDataGridPagination() {
        return this.getDataGrid()
            .should('exist')
            .find(
                '[data-cy=data-pipelines-job-executions-datagrid-pagination]'
            );
    }

    /* Actions */

    // General

    refreshExecData() {
        this.getExecRefreshBtn().should('exist').click({ force: true });
    }

    // DataGrid

    typeToTextFilterInput(value) {
        this.getDataGridInputFilter().should('exist').type(value);

        this.waitForViewToRender();
    }

    clearTextFilterInput() {
        this.getDataGridInputFilter().should('exist').clear({ force: true });

        this.waitForViewToRender();
    }

    closeFilter() {
        this.getDataGridPopupFilterCloseBtn()
            .should('exist')
            .click({ force: true });

        this.waitForViewToRenderShort();
    }

    // Header

    // status
    /**
     * ** Open status filter.
     */
    openStatusFilter() {
        this.getDataGridExecStatusFilterOpenerBtn()
            .should('exist')
            .click({ force: true });

        this.waitForViewToRenderShort();
    }

    /**
     * ** Choose filter by some status.
     *
     * @param {'succeeded'|'platform_error'|'user_error'|'running'|'submitted'|'skipped'|'cancelled'} status
     */
    filterByStatus(status) {
        this.getDataGridExecStatusFilterCheckbox(status)
            .should('exist')
            .as('checkbox')
            .invoke('is', ':checked')
            .then((checked) => {
                if (!checked) {
                    this.getDataGridExecStatusFilterLabel(status)
                        .should('exist')
                        .click({ force: true });
                }
            });

        this.waitForViewToRender();
    }

    /**
     * ** Clear filter by some status.
     *
     * @param {'succeeded'|'platform_error'|'user_error'|'running'|'submitted'|'skipped'|'cancelled'} status
     */
    clearFilterByStatus(status) {
        this.getDataGridExecStatusFilterCheckbox(status)
            .should('exist')
            .as('checkbox')
            .invoke('is', ':checked')
            .then((checked) => {
                if (checked) {
                    this.getDataGridExecStatusFilterLabel(status)
                        .should('exist')
                        .click({ force: true });
                }
            });

        this.waitForViewToRender();
    }

    sortByExecStatus() {
        this.getDataGridExecStatusSortBtn()
            .should('exist')
            .click({ force: true });

        this.waitForViewToRender();
    }

    // type
    openTypeFilter() {
        this.getDataGridExecTypeFilterOpenerBtn()
            .should('exist')
            .click({ force: true });

        this.waitForViewToRenderShort();
    }

    /**
     * ** Choose filter by some type.
     *
     * @param {'manual'|'scheduled'} type
     */
    filterByType(type) {
        this.getDataGridExecTypeFilterCheckbox(type)
            .should('exist')
            .as('checkbox')
            .invoke('is', ':checked')
            .then((checked) => {
                if (!checked) {
                    this.getDataGridExecTypeFilterLabel(type).click({
                        force: true
                    });
                }
            });

        this.waitForViewToRender();
    }

    /**
     * ** Clear filter by some type.
     *
     * @param {'manual'|'scheduled'} type
     */
    clearFilterByType(type) {
        this.getDataGridExecTypeFilterCheckbox(type)
            .should('exist')
            .as('checkbox')
            .invoke('is', ':checked')
            .then((checked) => {
                if (checked) {
                    this.getDataGridExecTypeFilterLabel(type)
                        .should('exist')
                        .click({ force: true });
                }
            });

        this.waitForViewToRender();
    }

    sortByExecType() {
        this.getDataGridExecTypeSortBtn()
            .should('exist')
            .click({ force: true });

        this.waitForViewToRender();
    }

    // duration
    openDurationFilter() {
        this.getDataGridExecDurationFilterOpenerBtn()
            .should('exist')
            .click({ force: true });

        this.waitForViewToRenderShort();
    }

    sortByExecDuration() {
        this.getDataGridExecDurationSortBtn()
            .should('exist')
            .click({ force: true });

        this.waitForViewToRender();
    }

    // exec start
    openExecStartFilter() {
        this.getDataGridExecStartFilterOpenerBtn()
            .should('exist')
            .click({ force: true });

        this.waitForViewToRenderShort();
    }

    sortByExecStart() {
        this.getDataGridExecStartSortBtn()
            .should('exist')
            .click({ force: true });

        this.waitForViewToRender();
    }

    // exec end
    openExecEndFilter() {
        this.getDataGridExecEndFilterOpenerBtn()
            .should('exist')
            .click({ force: true });

        this.waitForViewToRenderShort();
    }

    sortByExecEnd() {
        this.getDataGridExecEndSortBtn().should('exist').click({ force: true });

        this.waitForViewToRender();
    }

    // id
    openIDFilter() {
        this.getDataGridExecIDFilterOpenerBtn()
            .should('exist')
            .click({ force: true });

        this.waitForViewToRenderShort();
    }

    sortByExecID() {
        this.getDataGridExecIDSortBtn().should('exist').click({ force: true });

        this.waitForViewToRender();
    }

    // version
    openVersionFilter() {
        this.getDataGridExecVersionFilterOpenerBtn()
            .should('exist')
            .click({ force: true });

        this.waitForViewToRenderShort();
    }

    sortByExecVersion() {
        this.getDataGridExecVersionSortBtn()
            .should('exist')
            .click({ force: true });

        this.waitForViewToRender();
    }
}
