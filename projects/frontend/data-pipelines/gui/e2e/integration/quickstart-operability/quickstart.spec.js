/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { GetStartedPagePO } from '../../support/pages/get-started/get-started-page.po';
import { DataJobsManagePage } from '../../support/pages/manage/data-jobs/data-jobs.po';
import { BasePagePO } from '../../support/pages/base/base-page.po';

describe('Check if quickstart-vdk frontend is operational', () => {
    describe('smoke', { tags: ['@smoke'] }, () => {
        it('navigates to root page and the page loads correctly', () => {
            const getStartedPage = BasePagePO.navigateToNoBootstrap();
            getStartedPage.getPageTitle().invoke('text').invoke('trim').should('eq', 'Get Started with Data Pipelines');
        });

        it('navigates to get-started page and the page loads correctly', () => {
            const getStartedPage = GetStartedPagePO.navigateToNoBootstrap();
            getStartedPage.getPageTitle().invoke('text').invoke('trim').should('eq', 'Get Started with Data Pipelines');
        });

        it('navigates to manage page and the page loads correctly', () => {
            const dataJobsManagePage = DataJobsManagePage.navigateToNoBootstrap();

            dataJobsManagePage.getPageTitle().scrollIntoView().should('be.visible').invoke('text').invoke('trim').should('eq', 'Manage Data Jobs');

            dataJobsManagePage.getDataGrid().scrollIntoView().should('be.visible');
        });
    });
});
