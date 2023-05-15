/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { DataJobsExplorePage } from '../../../../support/pages/explore/data-jobs/data-jobs.po';
import { DataJobExploreDetailsPage } from '../../../../support/pages/explore/data-jobs/details/data-job-details.po';

describe('Data Job Explore Details Page', { tags: ['@dataPipelines', '@exploreDataJobDetails', '@explore'] }, () => {
    /**
     * @type {DataJobExploreDetailsPage}
     */
    let dataJobExploreDetailsPage;
    /**
     * @type {Array<{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}>}
     */
    let testJobsFixture;
    /**
     * @type {DataJobsExplorePage}
     */
    let dataJobsExplorePage;

    before(() => {
        return DataJobExploreDetailsPage.recordHarIfSupported()
            .then(() => cy.clearLocalStorageSnapshot('data-job-explore-details'))
            .then(() => DataJobExploreDetailsPage.login())
            .then(() => cy.saveLocalStorage('data-job-explore-details'))
            .then(() => DataJobExploreDetailsPage.deleteShortLivedTestJobsNoDeploy(true))
            .then(() => DataJobExploreDetailsPage.createShortLivedTestJobsNoDeploy())
            .then(() =>
                DataJobExploreDetailsPage.loadShortLivedTestJobsFixtureNoDeploy().then((fixtures) => {
                    testJobsFixture = [fixtures[0], fixtures[1]];

                    return cy.wrap({
                        context: 'explore::data-job-details.spec::before()',
                        action: 'continue'
                    });
                })
            );
    });

    after(() => {
        DataJobExploreDetailsPage.deleteShortLivedTestJobsNoDeploy();

        DataJobExploreDetailsPage.saveHarIfSupported();
    });

    beforeEach(() => {
        cy.restoreLocalStorage('data-job-explore-details');

        DataJobExploreDetailsPage.wireUserSession();
        DataJobExploreDetailsPage.initInterceptors();
    });

    describe('smoke', { tags: ['@smoke'] }, () => {
        it('should load and show job details', () => {
            dataJobsExplorePage = DataJobsExplorePage.navigateWithSideMenu();

            // filter by job name substring because there are a lot of jobs, and it could potentially be on second/third page
            dataJobsExplorePage.filterByJobName(testJobsFixture[0].job_name.substring(0, 20));

            dataJobsExplorePage.openJobDetails(testJobsFixture[0].team, testJobsFixture[0].job_name);

            dataJobExploreDetailsPage = DataJobExploreDetailsPage.getPage();

            dataJobExploreDetailsPage.getDetailsTab().scrollIntoView().should('be.visible');

            dataJobExploreDetailsPage.getPageTitle().scrollIntoView().should('be.visible').should('contains.text', testJobsFixture[0].job_name);

            dataJobExploreDetailsPage.getStatusField().scrollIntoView().should('be.visible').should('have.text', 'Not Deployed');

            dataJobExploreDetailsPage.getDescriptionField().scrollIntoView().should('be.visible').should('contain.text', testJobsFixture[0].description);

            dataJobExploreDetailsPage.getTeamField().scrollIntoView().should('be.visible').should('have.text', testJobsFixture[0].team);

            dataJobExploreDetailsPage.getScheduleField().scrollIntoView().should('be.visible').should('contains.text', 'At 12:00 AM, on day 01 of the month, and on Friday');

            dataJobExploreDetailsPage.getOnDeployedField().scrollIntoView().should('be.visible').should('contains.text', testJobsFixture[0].config.contacts.notified_on_job_deploy);

            dataJobExploreDetailsPage.getOnPlatformErrorField().scrollIntoView().should('be.visible').should('contains.text', testJobsFixture[0].config.contacts.notified_on_job_failure_platform_error);

            dataJobExploreDetailsPage.getOnUserErrorField().scrollIntoView().should('be.visible').should('contains.text', testJobsFixture[0].config.contacts.notified_on_job_failure_user_error);

            dataJobExploreDetailsPage.getOnSuccessField().scrollIntoView().should('be.visible').should('contains.text', testJobsFixture[0].config.contacts.notified_on_job_success);
        });

        it('should verify Details tab is visible and active', () => {
            dataJobsExplorePage = DataJobsExplorePage.navigateTo();

            // filter by job name substring because there are a lot of jobs, and it could potentially be on second/third page
            dataJobsExplorePage.filterByJobName(testJobsFixture[0].job_name.substring(0, 20));

            dataJobsExplorePage.openJobDetails(testJobsFixture[0].team, testJobsFixture[0].job_name);

            const dataJobExploreDetailsPage = DataJobExploreDetailsPage.getPage();

            dataJobExploreDetailsPage.getPageTitle().scrollIntoView().should('be.visible').should('contains.text', testJobsFixture[0].job_name);

            dataJobExploreDetailsPage.getDetailsTab().scrollIntoView().should('be.visible').should('have.class', 'active');
        });
    });

    describe('extended', () => {
        it('should verify Action buttons are not displayed', () => {
            dataJobsExplorePage = DataJobsExplorePage.navigateTo();

            // filter by job name substring because there are a lot of jobs, and it could potentially be on second/third page
            dataJobsExplorePage.filterByJobName(testJobsFixture[0].job_name.substring(0, 20));

            dataJobsExplorePage.openJobDetails(testJobsFixture[0].team, testJobsFixture[0].job_name);

            const dataJobExploreDetailsPage = DataJobExploreDetailsPage.getPage();

            dataJobExploreDetailsPage.getPageTitle().scrollIntoView().should('be.visible').should('contains.text', testJobsFixture[0].job_name);

            dataJobExploreDetailsPage.getExecuteNowButton().should('not.exist');

            dataJobExploreDetailsPage.getActionDropdownBtn().should('not.exist');
        });
    });
});
