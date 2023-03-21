/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { DataJobsBasePO } from "../../../../application/data-jobs-base.po";

export class DataJobsExplorePage extends DataJobsBasePO {
    static getPage() {
        return new DataJobsExplorePage();
    }

    static navigateTo() {
        return super.navigateTo("[data-cy=navigation-link-explore-datajobs]");
    }

    // Selectors

    getMainTitle() {
        return cy.get("[data-cy=data-pipelines-explore-page-main-title]");
    }

    getDataGrid() {
        return cy.get("[data-cy=data-pipelines-explore-grid]");
    }

    getDataGridCell(content) {
        return cy
            .get(
                '[id^="clr-dg-row"] > .datagrid-row-scrollable > .datagrid-scrolling-cells > .ng-star-inserted',
            )
            .contains(new RegExp(`^\\s*${content}\\s*$`));
    }

    getDataGridNavigateBtn(team, job) {
        return cy.get(
            '[data-cy=data-pipelines-explore-grid-details-link][data-job-params="' +
                team +
                ";" +
                job +
                '"]',
        );
    }

    getDataGridNameFilter() {
        return this.getHeaderColumnJobName()
            .should("exist")
            .find("clr-dg-filter button");
    }

    getDataGridNameFilterInput() {
        return cy.get("div.datagrid-filter input");
    }

    getDataGridRefreshButton() {
        return cy.get("[data-cy=data-pipelines-explore-refresh-btn]");
    }

    getDataGridSearchInput() {
        return cy.get("[data-test-id=search-input]");
    }

    getDataGridClearSearchButton() {
        return cy.get('[data-test-id="clear-search-btn"]').first();
    }

    // Actions

    refreshDataGrid() {
        this.getDataGridRefreshButton()
            .should("be.visible")
            .click({ force: true });

        this.waitForBackendRequestCompletion();

        this.waitForViewToRender();
    }

    searchByJobName(jobName) {
        this.getDataGridSearchInput().should("be.visible").type(jobName);

        this.waitForBackendRequestCompletion();

        this.waitForViewToRender();
    }

    clearSearchField() {
        this.getDataGridSearchInput().should("be.visible").clear();

        this.waitForBackendRequestCompletion();

        this.waitForViewToRender();
    }

    clearSearchFieldWithButton() {
        this.getDataGridClearSearchButton()
            .should("be.visible")
            .click({ force: true });

        this.waitForBackendRequestCompletion();

        this.waitForViewToRender();
    }

    filterByJobName(jobName) {
        this.getDataGridNameFilter().click({ force: true });

        this.getDataGridNameFilterInput().should("be.visible").type(jobName);

        this.getMainTitle().should("be.visible").click({ force: true });

        this.waitForBackendRequestCompletion();

        this.waitForViewToRender();
    }

    openJobDetails(team, jobName) {
        this.getDataGridNavigateBtn(team, jobName)
            .scrollIntoView()
            .should("exist")
            .click({ force: true });

        this.waitForBackendRequestCompletion();

        this.waitForViewToRenderShort();
    }
}
