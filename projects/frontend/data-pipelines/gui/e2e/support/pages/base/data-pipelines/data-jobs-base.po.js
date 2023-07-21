/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { DataPipelinesBasePO } from './data-pipelines-base.po';

export class DataJobsBasePO extends DataPipelinesBasePO {
    /**
     * ** Returns instance of the page object.
     *
     * @returns {DataJobsBasePO}
     */
    static getPage() {
        return new DataJobsBasePO();
    }

    /**
     * ** Navigate to Data Job Url.
     *
     * @param {'explore'|'manage'} context
     */
    static navigateTo(context) {
        return this.navigateToDataJobUrl(`/${context}/data-jobs`);
    }

    /**
     * ** Navigate to Data Job Url.
     * ** Do not wait for bootstrap and interceptors
     * @param {'explore'|'manage'} context
     */
    static navigateToNoBootstrap(context) {
        return this.navigateToDataJobUrlNoBootstrap(`/${context}/data-jobs`);
    }
    // Selectors

    getDataGridRefreshButton() {
        throw new Error('Method should be overridden by subclasses');
    }

    getDataGrid() {
        return cy.get('clr-datagrid');
    }

    getDataGridSearchInput() {
        return cy.get('[data-test-id=search-input]').first();
    }

    getDataGridClearSearchButton() {
        return cy.get('[data-test-id="clear-search-btn"]').first();
    }

    getQuickFilters() {
        return cy.get('[data-cy=data-pipelines-quick-filters] > span');
    }

    getHeaderColumnJobName() {
        return cy.get('[data-cy=data-pipelines-jobs-name-column]');
    }

    getHeaderColumnTeamName() {
        return cy.get('[data-cy=data-pipelines-jobs-team-column]');
    }

    getHeaderColumnDescriptionName() {
        return cy.get('[data-cy=data-pipelines-jobs-description-column]');
    }

    getDataGridJobNameFilter() {
        return this.getHeaderColumnJobName()
            .should('exist')
            .find('clr-dg-filter button');
    }

    getHeaderColumnJobNameSortBtn() {
        return this.getHeaderColumnJobName()
            .should('exist')
            .find('.datagrid-column-title');
    }

    getDataGridJobTeamFilter() {
        return this.getHeaderColumnTeamName()
            .should('exist')
            .find('clr-dg-filter button');
    }

    getHeaderColumnJobTeamSortBtn() {
        return this.getHeaderColumnTeamName()
            .should('exist')
            .find('.datagrid-column-title');
    }

    getDataGridJobDescriptionFilter() {
        return this.getHeaderColumnDescriptionName()
            .should('exist')
            .find('clr-dg-filter button');
    }

    getDataGridFilterInput() {
        return cy.get('div.datagrid-filter input');
    }

    getDataGridHeaderCell(content) {
        return this.getDataGrid()
            .should('exist')
            .find('clr-dg-column:not(.datagrid-hidden-column)')
            .contains(new RegExp(`${content}`));
    }

    // Rows and Cells

    getDataGridRows() {
        return this.getDataGrid()
            .should('exist')
            .find('clr-dg-row.datagrid-row');
    }

    getDataGridRowByIndex(rowIndex) {
        return this.getDataGridRows()
            .should('have.length.gte', rowIndex - 1)
            .then((rows) => Array.from(rows)[rowIndex - 1]);
    }

    getDataGridRowByName(jobName) {
        return this.getDataGridCell(jobName).parents('clr-dg-row');
    }

    getDataGridCells(rowIndex) {
        return this.getDataGridRowByIndex(rowIndex)
            .should('exist')
            .find('clr-dg-cell.datagrid-cell');
    }

    getDataGridCellByIndex(rowIndex, cellIndex) {
        return this.getDataGridCells(rowIndex)
            .should('have.length.gte', cellIndex - 1)
            .then((cells) => Array.from(cells)[cellIndex - 1]);
    }

    getDataGridCellByIdentifier(rowIndex, identifier) {
        return this.getDataGridRowByIndex(rowIndex)
            .should('exist')
            .find(identifier);
    }

    getDataGridCell(content, timeout) {
        return cy
            .get(
                '[id^="clr-dg-row"] > .datagrid-row-scrollable > .datagrid-scrolling-cells > .ng-star-inserted'
            )
            .contains(new RegExp(`^\\s*${content}\\s*$`), {
                timeout: this.resolveTimeout(timeout)
            });
    }

    getDataGridStatusCells() {
        return this.getDataGrid()
            .should('exist')
            .find('[data-cy=data-pipelines-manage-grid-status-cell]');
    }

    getDataGridStatusIcons() {
        return this.getDataGrid()
            .should('exist')
            .find(
                '[data-cy=data-pipelines-manage-grid-status-cell] clr-icon[data-cy*=data-pipelines-job]'
            );
    }

    getDataGridColumnToggle() {
        return this.getDataGrid()
            .should('exist')
            .find('clr-dg-column-toggle button');
    }

    getDataGridNavigateBtn(team, job) {
        throw new Error('Method should be overridden by subclasses');
    }

    getDataGridColumnShowHidePanel() {
        return cy.get('.column-switch');
    }

    getDataGridColumnShowHideOptions() {
        return this.getDataGridColumnShowHidePanel()
            .should('exist')
            .find('clr-checkbox-wrapper');
    }

    getDataGridColumnShowHideOptionsValues() {
        return this.getDataGridColumnShowHidePanel()
            .should('exist')
            .find('clr-checkbox-wrapper')
            .then((elements) => Array.from(elements).map((el) => el.innerText));
    }

    getDataGridColumnShowHideOption(option) {
        return this.getDataGridColumnShowHideOptions()
            .should('have.length.gt', 0)
            .then((elements) =>
                Array.from(elements).find((el) => el.innerText === option)
            )
            .find('input');
    }

    /**
     * ** Get DataGrid page size selection.
     *
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getDataGridPageSizeSelect() {
        return this.getDataGrid().find(
            'clr-dg-page-size .clr-page-size-select'
        );
    }

    getDataJobPage() {
        return cy.get('[data-cy=data-pipelines-job-page]');
    }

    // Actions

    chooseQuickFilter(filterPosition) {
        this.getQuickFilters()
            .then((filters) => {
                return filters && filters[filterPosition];
            })
            .should('exist')
            .click({ force: true });

        this.waitForGridDataLoad();
    }

    refreshDataGrid() {
        this.getDataGridRefreshButton().should('exist').click({ force: true });

        this.waitForGridDataLoad();
    }

    /**
     * ** Search by job name.
     *
     * @param {string} jobName
     */
    searchByJobName(jobName) {
        this.getDataGridSearchInput().should('exist').type(jobName);

        this.waitForGridDataLoad();
    }

    clearSearchField() {
        this.getDataGridSearchInput().should('exist').clear();

        this.waitForGridDataLoad();
    }

    clearSearchFieldWithButton() {
        this.getDataGridClearSearchButton()
            .should('exist')
            .click({ force: true });

        this.waitForGridDataLoad();
    }

    filterByJobName(jobName) {
        this.getDataGridJobNameFilter().click({ force: true });

        this.getDataGridFilterInput().should('be.visible').type(jobName);

        this.getContentContainer().should('be.visible').click({ force: true });

        this.waitForGridDataLoad();

        this.waitForViewToRenderShort();
    }

    filterByJobDescription(description) {
        this.getDataGridJobDescriptionFilter().click({ force: true });

        this.getDataGridFilterInput().should('be.visible').type(description);

        this.getContentContainer().should('be.visible').click({ force: true });

        this.waitForGridDataLoad();

        this.waitForViewToRenderShort();
    }

    sortByJobName() {
        this.getHeaderColumnJobNameSortBtn()
            .should('exist')
            .click({ force: true });

        this.waitForGridDataLoad();
    }

    filterByJobTeamName(teamName) {
        this.getDataGridJobTeamFilter().click({ force: true });

        this.getDataGridFilterInput().should('be.visible').type(teamName);

        this.getContentContainer().should('be.visible').click({ force: true });

        this.waitForGridDataLoad();
    }

    sortByJobTeamName() {
        this.getHeaderColumnJobTeamSortBtn()
            .should('exist')
            .click({ force: true });

        this.waitForGridDataLoad();
    }

    selectRow(jobName) {
        this.getDataGridRowByName(jobName)
            .find('.datagrid-select input')
            .check({ force: true });

        this.waitForViewToRenderShort();
    }

    openJobDetails(teamName, jobName) {
        this.getDataGridNavigateBtn(teamName, jobName)
            .scrollIntoView()
            .should('exist')
            .click({ force: true });

        this.waitForDataJobsApiGetReqInterceptor(4);

        this.waitForViewToRender();

        this.getDataJobPage().should('be.visible');
    }

    toggleColumnShowHidePanel() {
        this.getDataGridColumnToggle().should('exist').click({ force: true });

        this.waitForClickThinkingTime();
    }

    checkColumnShowHideOption(option) {
        this.getDataGridColumnShowHideOption(option)
            .should('exist')
            .check({ force: true });

        this.waitForViewToRenderShort();
    }

    uncheckColumnShowHideOption(option) {
        this.getDataGridColumnShowHideOption(option)
            .should('exist')
            .uncheck({ force: true });

        this.waitForViewToRenderShort();
    }

    /**
     * ** Change DataGrid page size
     *
     *      - hint options in Clarity are generated with values e.g.
     *        - '0: 25'
     *        - '1: 50'
     *        - '2: 100'
     *
     * @param {string} size
     */
    changePageSize(size) {
        this.getDataGridPageSizeSelect()
            .should('be.visible')
            .then(($element) => {
                return cy.wait(1000).then(() => $element);
            })
            .select(size);

        this.waitForGridDataLoad();
    }
}
