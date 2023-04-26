/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { DataJobsBasePO } from '../../base/data-pipelines/data-jobs-base.po';

export class DataJobsExplorePage extends DataJobsBasePO {
    /**
     * ** Returns instance of the page object.
     *
     * @returns {DataJobsExplorePage}
     */
    static getPage() {
        return new DataJobsExplorePage();
    }

    /**
     * @inheritDoc
     * @return {DataJobsExplorePage}
     */
    static navigateWithSideMenu() {
        return super.navigateWithSideMenu(
            'navLinkExploreDataJobs',
            'openExplore',
            {
                before: () => {
                    this.waitForApplicationBootstrap();
                    this.waitForDataJobsApiGetReqInterceptor(3);
                },
                after: () => {
                    this.waitForDataJobsApiGetReqInterceptor();

                    const page = this.getPage();
                    page.waitForGridToLoad(null);
                    page.waitForViewToRenderShort();
                }
            }
        );
    }

    /**
     * ** Navigate to Explore Data Jobs.
     *
     * @return {DataJobsExplorePage}
     */
    static navigateTo() {
        /**
         * @type {DataJobsExplorePage}
         */
        const page = super.navigateTo('explore');
        page.waitForGridToLoad(null);
        page.waitForViewToRenderShort();

        return page;
    }

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
            'data-pipelines-explore-data-jobs',
            timeout
        );
    }

    // Selectors

    getDataGrid() {
        return cy.get('[data-cy=data-pipelines-explore-grid]');
    }

    getDataGridNavigateBtn(team, job) {
        return cy.get(
            '[data-cy=data-pipelines-explore-grid-details-link][data-job-params="' +
                team +
                ';' +
                job +
                '"]'
        );
    }

    getDataGridRefreshButton() {
        return cy.get('[data-cy=data-pipelines-explore-refresh-btn]');
    }
}
