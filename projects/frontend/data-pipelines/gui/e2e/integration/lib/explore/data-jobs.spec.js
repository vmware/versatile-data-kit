/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />
import { DataJobsExplorePage } from '../../../support/pages/app/lib/explore/data-jobs.po';
import { DataJobExploreDetailsPage } from '../../../support/pages/app/lib/explore/data-job-details.po';
import { applyGlobalEnvSettings } from '../../../support/helpers/commands.helpers';

describe('Data Jobs Explore Page', { tags: ['@dataPipelines', '@exploreDataJobs'] }, () => {
    let dataJobsExplorePage;
    let testJobs;

    before(() => {
        return DataJobsExplorePage.recordHarIfSupported()
                                  .then(() => cy.clearLocalStorageSnapshot('data-jobs-explore'))
                                  .then(() => DataJobsExplorePage.login())
                                  .then(() => cy.saveLocalStorage('data-jobs-explore'))
                                  .then(() => cy.cleanTestJobs())
                                  .then(() => cy.prepareBaseTestJobs())
                                  .then(() => cy.fixture('lib/explore/test-jobs.json'))
                                  .then((loadedTestJobs) => {
                                      testJobs = applyGlobalEnvSettings(loadedTestJobs);

                                      return cy.wrap({ context: 'explore::data-jobs.spec::before()', action: 'continue' });
                                  });
    });

    after(() => {
        cy.cleanTestJobs();

        DataJobsExplorePage.saveHarIfSupported();
    });

    beforeEach(() => {
        cy.restoreLocalStorage('data-jobs-explore');

        DataJobsExplorePage.initBackendRequestInterceptor();
    });

    it('Main Title Component have text: Explore Data Jobs', () => {
        dataJobsExplorePage = DataJobsExplorePage.navigateTo();

        dataJobsExplorePage
            .getMainTitle()
            .should('be.visible')
            .should('have.text', 'Explore Data Jobs');
    });

    it('Data Jobs Explore Page - loaded and shows data jobs', () => {
        dataJobsExplorePage = DataJobsExplorePage.navigateTo();

        dataJobsExplorePage
            .getDataGrid()
            .should('be.visible');

        testJobs.forEach((testJob) => {
            cy.log('Fixture for name: ' + testJob.job_name);

            dataJobsExplorePage
                .getDataGridCell(testJob.job_name)
                .scrollIntoView()
                .should('be.visible');

            dataJobsExplorePage
                .getDataGridCell(testJob.team)
                .should('be.visible');
        })
    });

    it('Data Jobs Explore Page - filters data jobs', () => {
        cy.log('Fixture for name: ' + testJobs[0].job_name);

        dataJobsExplorePage = DataJobsExplorePage.navigateTo();

        dataJobsExplorePage
            .filterByJobName(testJobs[0].job_name);

        dataJobsExplorePage
            .getDataGridCell(testJobs[0].job_name)
            .should('be.visible');

        dataJobsExplorePage
            .getDataGridCell(testJobs[1].job_name)
            .should('not.exist');
    });

    it('Data Jobs Explore Page - refreshes data jobs', () => {
        dataJobsExplorePage = DataJobsExplorePage.navigateTo();

        cy.fixture('lib/explore/additional-test-job.json').then((additionalTestJob) => {
            const normalizedTestJob = applyGlobalEnvSettings(additionalTestJob);

            cy.log('Fixture for name: ' + normalizedTestJob.job_name);

            dataJobsExplorePage
                .getDataGridCell(testJobs[0].job_name)
                .should('have.text', testJobs[0].job_name);

            dataJobsExplorePage
                .getDataGridCell(normalizedTestJob.job_name)
                .should('not.exist');

            cy.prepareAdditionalTestJobs();

            dataJobsExplorePage
                .refreshDataGrid();

            dataJobsExplorePage
                .filterByJobName(normalizedTestJob.job_name);

            dataJobsExplorePage
                .getDataGridCell(normalizedTestJob.job_name)
                .should('have.text', normalizedTestJob.job_name);
        });
    });

    it('Data Jobs Explore Page - searches data jobs', () => {
        cy.log('Fixture for name: ' + testJobs[0].job_name);

        dataJobsExplorePage = DataJobsExplorePage.navigateTo();

        dataJobsExplorePage
            .getDataGridCell(testJobs[1].job_name)
            .should('be.visible');

        dataJobsExplorePage
            .searchByJobName(testJobs[0].job_name);

        dataJobsExplorePage
            .getDataGridCell(testJobs[0].job_name)
            .should('be.visible');

        dataJobsExplorePage
            .getDataGridCell(testJobs[1].job_name)
            .should('not.exist');
    });

    it('Data Jobs Explore Page - searches data jobs, search parameter goes into URL', () => {
        cy.log('Fixture for name: ' + testJobs[0].job_name);

        dataJobsExplorePage = DataJobsExplorePage.navigateTo();

        // verify 2 test rows visible
        dataJobsExplorePage
            .getDataGridCell(testJobs[0].job_name)
            .should('be.visible');
        dataJobsExplorePage
            .getDataGridCell(testJobs[1].job_name)
            .should('be.visible');

        // do search
        dataJobsExplorePage
            .searchByJobName(testJobs[0].job_name);

        // verify 1 test row visible
        dataJobsExplorePage
            .getDataGridCell(testJobs[0].job_name)
            .should('be.visible');
        dataJobsExplorePage
            .getDataGridCell(testJobs[1].job_name)
            .should('not.exist');

        // verify url contains search value
        dataJobsExplorePage
            .getCurrentUrl()
            .should('match', new RegExp(`\\/explore\\/data-jobs\\?search=${ testJobs[0].job_name }$`));

        // clear search with clear() method
        dataJobsExplorePage
            .clearSearchField();

        // verify 2 test rows visible
        dataJobsExplorePage
            .getDataGridCell(testJobs[0].job_name)
            .should('be.visible');
        dataJobsExplorePage
            .getDataGridCell(testJobs[1].job_name)
            .should('be.visible');

        // verify url does not contain search value
        dataJobsExplorePage
            .getCurrentUrl()
            .should('match', new RegExp(`\\/explore\\/data-jobs$`));
    });

    it('Data Jobs Explore Page - searches data jobs, perform search when URL contains search parameter', () => {
        cy.log('Fixture for name: ' + testJobs[1].job_name);

        // navigate with search value in URL
        dataJobsExplorePage = DataJobsExplorePage.navigateToUrl(`/explore/data-jobs?search=${ testJobs[1].job_name }`);

        // verify url contains search value
        dataJobsExplorePage
            .getCurrentUrl()
            .should('match', new RegExp(`\\/explore\\/data-jobs\\?search=${ testJobs[1].job_name }$`));

        // verify 1 test row visible
        dataJobsExplorePage
            .getDataGridCell(testJobs[0].job_name)
            .should('not.exist');
        dataJobsExplorePage
            .getDataGridCell(testJobs[1].job_name)
            .should('be.visible');

        // clear search with button
        dataJobsExplorePage
            .clearSearchFieldWithButton();

        // verify 2 test rows visible
        dataJobsExplorePage
            .getDataGridCell(testJobs[0].job_name)
            .should('be.visible');
        dataJobsExplorePage
            .getDataGridCell(testJobs[1].job_name)
            .should('be.visible');

        // verify url does not contain search value
        dataJobsExplorePage
            .getCurrentUrl()
            .should('match', new RegExp(`\\/explore\\/data-jobs$`));
    });

    it('Data Jobs Explore Page - show/hide column when toggling from menu', () => {
        dataJobsExplorePage = DataJobsExplorePage.navigateTo();

        // show panel for show/hide columns
        dataJobsExplorePage
            .toggleColumnShowHidePanel();

        // verify correct options are rendered
        dataJobsExplorePage
            .getDataGridColumnShowHideOptionsValues()
            .should('have.length', 9)
            .invoke('join', ',')
            .should('eq', 'Description,Deployment Status,Last Execution Duration,Success rate,Next run (UTC),Last Deployed (UTC),Last Deployed By,Source,Logs');

        // verify column is not checked in toggling menu
        dataJobsExplorePage
            .getDataGridColumnShowHideOption('Last Execution Duration')
            .should('exist')
            .should('not.be.checked');

        // verify header cell for column is not rendered
        dataJobsExplorePage
            .getDataGridHeaderCell('Last Execution Duration')
            .should('have.length', 0);

        // toggle column to render
        dataJobsExplorePage
            .checkColumnShowHideOption('Last Execution Duration');

        // verify column is checked in toggling menu
        dataJobsExplorePage
            .getDataGridColumnShowHideOption('Last Execution Duration')
            .should('exist')
            .should('be.checked');

        // verify header cell for column is rendered
        dataJobsExplorePage
            .getDataGridHeaderCell('Last Execution Duration')
            .should('have.length', 1);

        // toggle column to hide
        dataJobsExplorePage
            .uncheckColumnShowHideOption('Last Execution Duration');

        // verify column is not checked in toggling menu
        dataJobsExplorePage
            .getDataGridColumnShowHideOption('Last Execution Duration')
            .should('exist')
            .should('not.be.checked');

        // verify header cell for column is not rendered
        dataJobsExplorePage
            .getDataGridHeaderCell('Last Execution Duration')
            .should('have.length', 0);

        // hide panel for show/hide columns
        dataJobsExplorePage
            .toggleColumnShowHidePanel();
    });

    it('Data Jobs Explore Page - navigates to data job', () => {
        cy.log('Fixture for name: ' + testJobs[0].job_name);

        dataJobsExplorePage = DataJobsExplorePage.navigateTo();

        dataJobsExplorePage
            .openJobDetails(testJobs[0].team, testJobs[0].job_name);

        const dataJobExploreDetailsPage = DataJobExploreDetailsPage
            .getPage();

        dataJobExploreDetailsPage
            .getMainTitle()
            .should('be.visible')
            .should('contains.text', testJobs[0].job_name);

        dataJobExploreDetailsPage
            .getDescriptionField()
            .should('be.visible')
            .should('contain.text', testJobs[0].description);
    });
});
