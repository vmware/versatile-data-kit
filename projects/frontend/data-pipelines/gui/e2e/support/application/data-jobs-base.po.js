/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { DataPipelinesBasePO } from './data-pipelines-base.po';

export class DataJobsBasePO extends DataPipelinesBasePO {
    static getPage() {
        return new DataJobsExplorePage();
    }

    static navigateTo(linkSelector) {
        cy.visit('/');

        cy.wait(DataJobsBasePO.INITIAL_PAGE_LOAD_WAIT_TIME);

        cy.get(linkSelector).click({ force: true });

        this.waitForBackendRequestCompletion();

        cy.wait(DataJobsBasePO.VIEW_RENDER_WAIT_TIME);

        return this.getPage();
    }

    /* Selectors */

    getDataGrid() {
        return cy.get('clr-datagrid');
    }

    getQuickFilters() {
        return cy.get('[data-cy=data-pipelines-quick-filters] > span');
    }

    getHeaderColumnJobName() {
        return cy.get('[data-cy=data-pipelines-jobs-name-column]');
    }

    getHeaderColumnJobNameSortBtn() {
        return this.getHeaderColumnJobName()
            .should('exist')
            .find('.datagrid-column-title');
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
        return this.getDataGridCells(rowIndex)
            .should('have.length.gte', cellIndex - 1)
            .then((cells) => Array.from(cells)[cellIndex - 1]);
    }

    getDataGridCellByIdentifier(rowIndex, identifier) {
        return this.getDataGridRow(rowIndex).should('exist').find(identifier);
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

    /* Actions */

    chooseQuickFilter(filterPosition) {
        this.getQuickFilters()
            .then((filters) => {
                return filters && filters[filterPosition];
            })
            .should('exist')
            .click({ force: true });

        this.waitForBackendRequestCompletion();

        this.waitForViewToRender();
    }

    sortByJobName() {
        this.getHeaderColumnJobNameSortBtn()
            .should('exist')
            .click({ force: true });

        this.waitForBackendRequestCompletion();

        this.waitForSmartDelay();
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
}
