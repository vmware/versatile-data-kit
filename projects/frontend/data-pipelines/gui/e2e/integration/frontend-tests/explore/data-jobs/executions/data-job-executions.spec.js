/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { DataJobDetailsBasePO } from '../../../../../support/pages/base/data-pipelines/data-job-details-base.po';

import { DataJobsExplorePage } from '../../../../../support/pages/explore/data-jobs/data-jobs.po';
import { DataJobExploreExecutionsPage } from '../../../../../support/pages/explore/data-jobs/executions/data-job-executions.po';

describe('Data Job Explore Executions Page', { tags: ['@dataPipelines', '@exploreDataJobExecutions', '@explore'] }, () => {
    /**
     * @type {Array<{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}>}
     */
    let testJobsFixture;

    before(() => {
        return DataJobExploreExecutionsPage.recordHarIfSupported()
            .then(() => cy.clearLocalStorageSnapshot('data-job-explore-executions'))
            .then(() => DataJobExploreExecutionsPage.login())
            .then(() => cy.saveLocalStorage('data-job-explore-executions'))
            .then(() => DataJobExploreExecutionsPage.deleteShortLivedTestJobsNoDeploy(true))
            .then(() => DataJobExploreExecutionsPage.createShortLivedTestJobsNoDeploy())
            .then(() =>
                DataJobExploreExecutionsPage.loadShortLivedTestJobsFixtureNoDeploy().then((fixtures) => {
                    testJobsFixture = [fixtures[0], fixtures[1]];

                    return cy.wrap({
                        context: 'explore::data-job-executions.spec::before()',
                        action: 'continue'
                    });
                })
            );
    });

    after(() => {
        DataJobExploreExecutionsPage.deleteShortLivedTestJobsNoDeploy();

        DataJobExploreExecutionsPage.saveHarIfSupported();
    });

    beforeEach(() => {
        cy.restoreLocalStorage('data-job-explore-executions');

        DataJobExploreExecutionsPage.wireUserSession();
        DataJobExploreExecutionsPage.initInterceptors();
    });

    describe('smoke', { tags: ['@smoke'] }, () => {
        it(`should open Details and verify Executions tab is not displayed`, () => {
            cy.log('Fixture for name: ' + testJobsFixture[0].job_name);

            /**
             * @type {DataJobsExplorePage}
             */
            const dataJobsExplorePage = DataJobsExplorePage.navigateWithSideMenu();

            // filter by job name substring because there are a lot of jobs, and it could potentially be on second/third page
            dataJobsExplorePage.filterByJobName(testJobsFixture[0].job_name.substring(0, 20));

            dataJobsExplorePage.openJobDetails(testJobsFixture[0].team, testJobsFixture[0].job_name);

            const dataJobDetailsBasePage = DataJobDetailsBasePO.getPage();

            dataJobDetailsBasePage.getPageTitle().scrollIntoView().should('be.visible').should('contains.text', testJobsFixture[0].job_name);

            dataJobDetailsBasePage.getDetailsTab().should('have.class', 'active');

            dataJobDetailsBasePage.getExecutionsTab().should('not.exist');
        });
    });

    describe('extended', () => {
        it('should verify on URL navigate to Executions will redirect to Details', () => {
            /**
             * @type {DataJobExploreExecutionsPage}
             */
            const dataJobBasePage = DataJobExploreExecutionsPage.navigateTo(testJobsFixture[0].team, testJobsFixture[0].job_name);

            dataJobBasePage.getPageTitle().scrollIntoView().should('be.visible').should('contains.text', testJobsFixture[0].job_name);

            dataJobBasePage
                .getCurrentUrlNormalized({
                    includePathSegment: true,
                    includeQueryString: true
                })
                .should('deep.equal', {
                    pathSegment: `/explore/data-jobs/${testJobsFixture[0].team}/${testJobsFixture[0].job_name}/details`,
                    queryParams: {}
                });

            dataJobBasePage.getDetailsTab().should('have.class', 'active');
        });
    });
});
