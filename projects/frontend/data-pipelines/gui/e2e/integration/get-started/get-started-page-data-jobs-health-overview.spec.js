/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { TEAM_VDK_DATA_JOB_FAILING } from '../../support/helpers/constants.support';

import { GetStartedDataJobsHealthOverviewWidgetPO } from '../../support/pages/get-started/get-started-page-data-jobs-health-overview.po';
import { DataJobManageDetailsPage } from '../../support/pages/manage/data-jobs/details/data-job-details.po';
import { DataJobManageExecutionsPage } from '../../support/pages/manage/data-jobs/executions/data-job-executions.po';

describe('Get Started Page: Data Jobs Health Overview Widget', { tags: ['@dataPipelines', '@healthOverviewWidget', '@getStarted'] }, () => {
    /**
     * @type {{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}}
     */
    let longLivedFailingJobFixture;
    /**
     * @type {GetStartedDataJobsHealthOverviewWidgetPO}
     */
    let getStartedPage;

    before(() => {
        return GetStartedDataJobsHealthOverviewWidgetPO.recordHarIfSupported()
            .then(() => cy.clearLocalStorageSnapshot('get-started-page-data-jobs-health'))
            .then(() => GetStartedDataJobsHealthOverviewWidgetPO.login())
            .then(() => cy.saveLocalStorage('get-started-page-data-jobs-health'))
            .then(() => GetStartedDataJobsHealthOverviewWidgetPO.createLongLivedJobs('failing'))
            .then(() => GetStartedDataJobsHealthOverviewWidgetPO.provideExecutionsForLongLivedJobs('failing'))
            .then(() =>
                GetStartedDataJobsHealthOverviewWidgetPO.loadLongLivedFailingJobFixture().then((loadedTestJob) => {
                    longLivedFailingJobFixture = loadedTestJob;

                    return cy.wrap({
                        context: 'get-started::1::get-started-page-data-jobs-health-overview.spec::before()',
                        action: 'continue'
                    });
                })
            )
            .then(() => {
                return cy.wrap({
                    context: 'get-started::2::get-started-page-data-jobs-health-overview.spec::before()',
                    action: 'continue'
                });
            });
    });

    after(() => {
        return GetStartedDataJobsHealthOverviewWidgetPO.saveHarIfSupported().then(() =>
            cy.wrap({
                context: 'get-started::get-started-page-data-jobs-health-overview.spec::after()',
                action: 'continue'
            })
        );
    });

    beforeEach(() => {
        cy.restoreLocalStorage('get-started-page-data-jobs-health');

        GetStartedDataJobsHealthOverviewWidgetPO.wireUserSession();
        GetStartedDataJobsHealthOverviewWidgetPO.initInterceptors();

        getStartedPage = GetStartedDataJobsHealthOverviewWidgetPO.navigateTo();
    });

    describe('smoke', { tags: ['@smoke'] }, () => {
        it('Validate Data Jobs Health Overview panel when switching Teams', () => {
            getStartedPage.getPageTitle().should('contain.text', 'Get Started with Data Pipelines');

            getStartedPage.getDataJobsHealthPanel().scrollIntoView();

            getStartedPage.getNumberOfFailedExecutions().should('be.gt', 0);
            getStartedPage
                .getAllFailingJobs()
                .then((elements) => elements.filter((_index, el) => el.innerText.includes(TEAM_VDK_DATA_JOB_FAILING)))
                .should('have.length.gt', 0);
            getStartedPage
                .getAllMostRecentFailingJobs()
                .then((elements) => elements.filter((_index, el) => el.innerText.includes(TEAM_VDK_DATA_JOB_FAILING)))
                .should('have.length.gt', 0);
        });
    });

    describe('extended', () => {
        it('Verify Widgets rendered correct data and failing jobs navigates correctly', () => {
            getStartedPage.getDataJobsHealthPanel().scrollIntoView();

            getStartedPage.getExecutionsSuccessPercentage().should('be.gte', 0).should('be.lte', 100);
            getStartedPage.getNumberOfFailedExecutions().should('be.gte', 2);
            getStartedPage.getExecutionsTotal().should('be.gte', 2);

            getStartedPage.getAllFailingJobs().should('have.length.gte', 1);

            getStartedPage.getAllMostRecentFailingJobsLinks().should('have.length.gte', 1);

            // navigate to failing job details
            getStartedPage.navigateToFailingJobDetails(longLivedFailingJobFixture.job_name);

            const dataJobManageDetailsPage = DataJobManageDetailsPage.getPage();
            dataJobManageDetailsPage.getPageTitle().should('contain.text', `Data Job: ${longLivedFailingJobFixture.job_name}`);
            dataJobManageDetailsPage.getDetailsTab().should('be.visible').should('have.class', 'active');
            dataJobManageDetailsPage.getExecutionsTab().should('exist').should('not.have.class', 'active');
            dataJobManageDetailsPage.showMoreDescription().getDescriptionFull().should('contain.text', longLivedFailingJobFixture.description);
        });

        it('Verify most recent failing executions Widget navigates correctly', () => {
            getStartedPage.getDataJobsHealthPanel().scrollIntoView();

            getStartedPage.getAllMostRecentFailingJobsLinks().should('have.length.gte', 1);

            // navigate to most recent failing job executions
            getStartedPage.navigateToMostRecentFailingJobExecutions(longLivedFailingJobFixture.job_name);

            const dataJobManageExecutionsPage = DataJobManageExecutionsPage.getPage();
            dataJobManageExecutionsPage.getPageTitle().should('contain.text', `Data Job: ${longLivedFailingJobFixture.job_name}`);
            dataJobManageExecutionsPage.getDetailsTab().should('be.visible').should('not.have.class', 'active');
            dataJobManageExecutionsPage.getExecutionsTab().should('be.visible').should('have.class', 'active');
            dataJobManageExecutionsPage.getDataGridRows().should('have.length.gte', 2);
        });
    });
});
