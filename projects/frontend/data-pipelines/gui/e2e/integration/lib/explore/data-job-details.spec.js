/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />
import { DataJobsExplorePage } from '../../../support/pages/app/lib/explore/data-jobs.po';
import { DataJobExploreDetailsPage } from '../../../support/pages/app/lib/explore/data-job-details.po';
import { applyGlobalEnvSettings } from '../../../support/helpers/commands.helpers';

describe('Data Job Explore Details Page', { tags: ['@dataPipelines', '@exploreDataJobDetails'] }, () => {
    let dataJobExploreDetailsPage;
    let testJobs;

    before(() => {
        return DataJobExploreDetailsPage.recordHarIfSupported()
                                        .then(() => cy.clearLocalStorageSnapshot('data-job-explore-details'))
                                        .then(() => DataJobExploreDetailsPage.login())
                                        .then(() => cy.saveLocalStorage('data-job-explore-details'))
                                        .then(() => cy.cleanTestJobs())
                                        .then(() => cy.prepareBaseTestJobs())
                                        .then(() => cy.fixture('lib/explore/test-jobs.json'))
                                        .then((loadedTestJobs) => {
                                            testJobs = applyGlobalEnvSettings(loadedTestJobs);

                                            return cy.wrap({ context: 'explore::data-job-details.spec::before()', action: 'continue' });
                                        });
    });

    after(() => {
        cy.cleanTestJobs();

        DataJobExploreDetailsPage.saveHarIfSupported();
    });

    beforeEach(() => {
        cy.restoreLocalStorage('data-job-explore-details');

        DataJobExploreDetailsPage.initBackendRequestInterceptor();
    });

    it('Data Job Explore Details Page - should load and show job details', () => {
        cy.log('Fixture for name: ' + testJobs[0].job_name);

        const dataJobsExplorePage = DataJobsExplorePage.navigateTo();

        dataJobsExplorePage
            .openJobDetails(testJobs[0].team, testJobs[0].job_name);

        dataJobExploreDetailsPage = DataJobExploreDetailsPage
            .getPage();

        dataJobExploreDetailsPage
            .getDetailsTab()
            .should('be.visible');

        dataJobExploreDetailsPage
            .getMainTitle()
            .should('be.visible')
            .should('contains.text', testJobs[0].job_name);

        dataJobExploreDetailsPage
            .getStatusField()
            .should('be.visible')
            // TODO: do the right assertion (once it gets implemented)
            .should('have.text', 'Not Deployed');

        dataJobExploreDetailsPage
            .getDescriptionField()
            .should('be.visible')
            .should('contain.text', testJobs[0].description);

        dataJobExploreDetailsPage
            .getTeamField()
            .should('be.visible')
            .should('have.text', testJobs[0].team);

        dataJobExploreDetailsPage
            .getScheduleField()
            .should('be.visible')
            .should('contains.text', 'At 12:00 AM, on day 01 of the month, and on Friday');

        // DISABLED Because there is no Source at the moment.
        // dataJobExploreDetailsPage
        // .getSourceField()
        // .should('be.visible')
        // // TODO: do the right assertion (once it gets implemented)
        // .should('contains.text', 'http://host/data-jobs/' + testJobs[0].job_name)
        // .should("have.attr", "href", 'http://host/data-jobs/' + testJobs[0].job_name);

        dataJobExploreDetailsPage
            .getOnDeployedField()
            .should('be.visible')
            .should('contains.text', testJobs[0].config.contacts.notified_on_job_deploy);

        dataJobExploreDetailsPage
            .getOnPlatformErrorField()
            .should('be.visible')
            .should('contains.text', testJobs[0].config.contacts.notified_on_job_failure_platform_error);

        dataJobExploreDetailsPage
            .getOnUserErrorField()
            .should('be.visible')
            .should('contains.text', testJobs[0].config.contacts.notified_on_job_failure_user_error);

        dataJobExploreDetailsPage
            .getOnSuccessField()
            .should('be.visible')
            .should('contains.text', testJobs[0].config.contacts.notified_on_job_success);
    });

    it('Data Job Explore Details Page - should verify Details tab is visible and active', () => {
        cy.log('Fixture for name: ' + testJobs[0].job_name);

        const dataJobsExplorePage = DataJobsExplorePage.navigateTo();

        dataJobsExplorePage
            .openJobDetails(testJobs[0].team, testJobs[0].job_name);

        const dataJobExploreDetailsPage = DataJobExploreDetailsPage
            .getPage();

        dataJobExploreDetailsPage
            .getMainTitle()
            .should('be.visible')
            .should('contains.text', testJobs[0].job_name);

        dataJobExploreDetailsPage
            .getDetailsTab()
            .should('be.visible')
            .should('have.class', 'active');
    });

    it('Data Job Explore Details Page - should verify Action buttons are not displayed', () => {
        cy.log('Fixture for name: ' + testJobs[0].job_name);

        const dataJobsExplorePage = DataJobsExplorePage.navigateTo();

        dataJobsExplorePage
            .openJobDetails(testJobs[0].team, testJobs[0].job_name);

        const dataJobExploreDetailsPage = DataJobExploreDetailsPage
            .getPage();

        dataJobExploreDetailsPage
            .getMainTitle()
            .should('be.visible')
            .should('contains.text', testJobs[0].job_name);

        dataJobExploreDetailsPage
            .getExecuteNowButton()
            .should('not.exist');

        dataJobExploreDetailsPage
            .getActionDropdownBtn()
            .should('not.exist');
    });
});
