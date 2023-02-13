/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />
// Contain tests on this page: http://localhost.vmware.com:4200/manage/data-jobs
// 1. Is search working
// When you click on details does a modal pop-up?

import { DataJobsManagePage } from '../../../support/pages/app/lib/manage/data-jobs.po';
import { DataJobManageDetailsPage } from '../../../support/pages/app/lib/manage/data-job-details.po';
import { applyGlobalEnvSettings } from '../../../support/helpers/commands.helpers';

describe('Data Jobs Manage Page', { tags: ['@dataPipelines', '@manageDataJobs'] }, () => {
    const descriptionWordsBeforeTruncate = 12;

    /**
     * @type {DataJobsManagePage}
     */
    let dataJobsManagePage;
    let testJobs;
    let longLivedTestJob;
    let longLivedFailingTestJob;

    before(() => {
        return DataJobsManagePage.recordHarIfSupported()
                                 .then(() => cy.clearLocalStorageSnapshot('data-jobs-manage'))
                                 .then(() => DataJobsManagePage.login())
                                 .then(() => cy.saveLocalStorage('data-jobs-manage'))
                                 .then(() => cy.cleanTestJobs())
                                 .then(() => cy.prepareBaseTestJobs())
                                 .then(() => cy.prepareLongLivedTestJob())
                                 .then(() => cy.createTwoExecutionsLongLivedTestJob())
                                 .then(() => cy.prepareLongLivedFailingTestJob())
                                 .then(() =>
                                     cy.fixture('lib/explore/test-jobs.json')
                                       .then((loadedTestJobs) => {
                                           testJobs = applyGlobalEnvSettings(loadedTestJobs);

                                           return cy.wrap({ context: 'manage::1::data-jobs.int.spec::before()', action: 'continue' });
                                       })
                                 )
                                 .then(() =>
                                     cy.fixture('lib/manage/e2e-cypress-dp-test.json')
                                       .then((loadedTestJob) => {
                                           longLivedTestJob = applyGlobalEnvSettings(loadedTestJob);

                                           return cy.wrap({ context: 'manage::2::data-jobs.int.spec::before()', action: 'continue' });
                                       })
                                 )
                                 .then(() =>
                                     cy.fixture('e2e-cy-dp-failing.job.json')
                                       .then((failingTestJob) => {
                                           longLivedFailingTestJob = applyGlobalEnvSettings(failingTestJob);

                                           return cy.wrap({ context: 'manage::3::data-jobs.int.spec::before()', action: 'continue' });
                                       })
                                 )
                                 .then(() =>
                                     // Enable data job after job end
                                     DataJobsManagePage.changeJobStatus(longLivedTestJob.team, longLivedTestJob.job_name, true)
                                 );
    });

    beforeEach(() => {
        cy.restoreLocalStorage('data-jobs-manage');

        DataJobsManagePage.initBackendRequestInterceptor();

        dataJobsManagePage = DataJobsManagePage.navigateTo();
    });

    after(() => {
        cy.cleanTestJobs();

        // Enable data job after job end
        DataJobsManagePage.changeJobStatus(longLivedTestJob.team, longLivedTestJob.job_name, true)

        DataJobsManagePage.saveHarIfSupported();
    });

    it('Data Jobs Manage Page - loads title', () => {
        dataJobsManagePage
            .getPageTitle()
            .should('be.visible');
    });

    it('Data Jobs Manage Page - grid contains test jobs', () => {
        dataJobsManagePage
            .chooseQuickFilter(0);

        dataJobsManagePage
            .sortByJobName();

        dataJobsManagePage
            .getDataGrid()
            .should('be.visible');

        testJobs.forEach((testJob) => {
            cy.log('Fixture for name: ' + testJob.job_name);

            dataJobsManagePage
                .getDataGridCell(testJob.job_name)
                .scrollIntoView()
                .should('be.visible');
        })
    });

    it('Data Jobs Manage Page - grid filter by job name', { tags: '@integration' }, () => {
        dataJobsManagePage
            .chooseQuickFilter(0);

        dataJobsManagePage
            .filterByJobName(testJobs[0].job_name);

        dataJobsManagePage
            .getDataGridCell(testJobs[0].job_name)
            .should('be.visible');

        dataJobsManagePage
            .getDataGridCell(testJobs[1].job_name)
            .should('not.exist');
    });

    it('Data Jobs Manage Page - grid search by job name', { tags: '@integration' }, () => {
        dataJobsManagePage
            .clickOnContentContainer();

        dataJobsManagePage
            .chooseQuickFilter(0);

        dataJobsManagePage
            .searchByJobName(testJobs[1].job_name);

        dataJobsManagePage
            .getDataGridCell(testJobs[0].job_name)
            .should('not.exist');

        dataJobsManagePage
            .getDataGridCell(testJobs[1].job_name)
            .should('be.visible');
    });

    it('Data Jobs Manage Page - grid search parameter goes into URL', () => {
        dataJobsManagePage
            .chooseQuickFilter(0);

        dataJobsManagePage
            .sortByJobName();

        // verify 2 test rows visible
        dataJobsManagePage
            .getDataGridCell(testJobs[0].job_name)
            .scrollIntoView()
            .should('be.visible');
        dataJobsManagePage
            .getDataGridCell(testJobs[1].job_name)
            .scrollIntoView()
            .should('be.visible');

        // do search
        dataJobsManagePage
            .searchByJobName(testJobs[0].job_name);

        dataJobsManagePage
            .waitForViewToRender();

        // verify 1 test row visible
        dataJobsManagePage
            .getDataGridCell(testJobs[0].job_name)
            .scrollIntoView()
            .should('be.visible');
        dataJobsManagePage
            .getDataGridCell(testJobs[1].job_name)
            .should('not.exist');

        // verify url contains search value
        dataJobsManagePage
            .getCurrentUrl()
            .should('match', new RegExp(`\\/manage\\/data-jobs\\?search=${ testJobs[0].job_name }$`));

        // clear search with clear() method
        dataJobsManagePage
            .clearSearchField();

        dataJobsManagePage
            .waitForViewToRender();

        // verify 2 test rows visible
        dataJobsManagePage
            .getDataGridCell(testJobs[0].job_name)
            .scrollIntoView()
            .should('be.visible');
        dataJobsManagePage
            .getDataGridCell(testJobs[1].job_name)
            .scrollIntoView()
            .should('be.visible');

        // verify url does not contain search value
        dataJobsManagePage
            .getCurrentUrl()
            .should('match', new RegExp(`\\/manage\\/data-jobs$`));
    });

    it('Data Jobs Manage Page - grid search perform search when URL contains search parameter', () => {
        // navigate with search value in URL
        dataJobsManagePage = DataJobsManagePage.navigateToUrl(`/manage/data-jobs?search=${ testJobs[1].job_name }`);

        dataJobsManagePage
            .chooseQuickFilter(0);

        dataJobsManagePage
            .sortByJobName();

        // verify url contains search value
        dataJobsManagePage
            .getCurrentUrl()
            .should('match', new RegExp(`\\/manage\\/data-jobs\\?search=${ testJobs[1].job_name }$`));

        // verify 1 test row visible
        dataJobsManagePage
            .getDataGridCell(testJobs[0].job_name)
            .should('not.exist');
        dataJobsManagePage
            .getDataGridCell(testJobs[1].job_name)
            .scrollIntoView()
            .should('be.visible');

        // clear search with button
        dataJobsManagePage
            .clearSearchFieldWithButton();

        // verify 2 test rows visible
        dataJobsManagePage
            .getDataGridCell(testJobs[0].job_name)
            .scrollIntoView()
            .should('be.visible');
        dataJobsManagePage
            .getDataGridCell(testJobs[1].job_name)
            .scrollIntoView()
            .should('be.visible');

        // verify url does not contain search value
        dataJobsManagePage
            .getCurrentUrl()
            .should('match', new RegExp(`\\/manage\\/data-jobs$`));
    });

    it('Data Jobs Manage Page - refresh shows newly created job', () => {
        cy.fixture('lib/explore/additional-test-job.json').then((additionalTestJob) => {
            const normalizedTestJob = applyGlobalEnvSettings(additionalTestJob);

            cy.log('Fixture for name: ' + normalizedTestJob.job_name);

            dataJobsManagePage
                .chooseQuickFilter(0);

            dataJobsManagePage
                .sortByJobName();

            dataJobsManagePage
                .getDataGridCell(testJobs[0].job_name)
                .should('have.text', testJobs[0].job_name);

            dataJobsManagePage
                .getDataGridCell(normalizedTestJob.job_name)
                .should('not.exist');

            dataJobsManagePage
                .prepareAdditionalTestJob();

            dataJobsManagePage
                .refreshDataGrid();

            dataJobsManagePage
                .filterByJobName(normalizedTestJob.job_name);

            dataJobsManagePage
                .getDataGridCell(normalizedTestJob.job_name)
                .should('have.text', normalizedTestJob.job_name);
        });
    });

    it('Data Jobs Manage Page - click on edit button opens new page with Job details', { tags: '@integration' }, () => {
        dataJobsManagePage
            .clickOnContentContainer();

        dataJobsManagePage
            .chooseQuickFilter(0);

        dataJobsManagePage
            .sortByJobName();

        dataJobsManagePage
            .openJobDetails(testJobs[0].team, testJobs[0].job_name);

        const dataJobManageDetailsPage = DataJobManageDetailsPage
            .getPage();

        dataJobManageDetailsPage
            .getMainTitle()
            .should('be.visible')
            .should('contains.text', testJobs[0].job_name);

        dataJobManageDetailsPage
            .getDescription()
            .should('be.visible')
            .should('contain.text', testJobs[0].description.split(' ').slice(0, descriptionWordsBeforeTruncate).join(' '))

        dataJobManageDetailsPage
            .getSchedule()
            .should('be.visible');

        dataJobManageDetailsPage
            .getDeploymentStatus('not-deployed')
            .should('be.visible')
            .should('have.text', 'Not Deployed');
    });

    it('Data Jobs Manage Page - disable/enable job', { tags: '@integration' }, () => {
        dataJobsManagePage
            .clickOnContentContainer();

        dataJobsManagePage
            .chooseQuickFilter(0);

        const jobName = longLivedTestJob.job_name;
        const team = longLivedTestJob.team;

        dataJobsManagePage
            .searchByJobName(jobName);

        //Toggle job status twice, enable to disable and vice versa.
        dataJobsManagePage.toggleJobStatus(longLivedTestJob.job_name);
        dataJobsManagePage.toggleJobStatus(longLivedTestJob.job_name);
    });

    it('Data Jobs Manage Page - quick filters', { tags: '@integration' }, () => {
        // Disable data job before test start
        DataJobsManagePage
            .changeJobStatus(longLivedFailingTestJob.team, longLivedFailingTestJob.job_name, true)
            .then(() =>
                DataJobsManagePage.changeJobStatus(longLivedTestJob.team, longLivedTestJob.job_name, false)
            )
            .then(() => {
                dataJobsManagePage
                    .clickOnContentContainer();

                dataJobsManagePage
                    .waitForClickThinkingTime();
                dataJobsManagePage
                    .chooseQuickFilter(0);
                dataJobsManagePage
                    .waitForViewToRender();

                dataJobsManagePage
                    .getDataGridStatusIcons()
                    .then(($icons) => {
                        for (const icon of Array.from($icons)) {
                            cy.wrap(icon).invoke('attr', 'data-cy')
                              .should('match', new RegExp('data-pipelines-job-(enabled|disabled|not-deployed)'));
                        }
                    });

                dataJobsManagePage
                    .waitForClickThinkingTime();
                dataJobsManagePage
                    .chooseQuickFilter(1);
                dataJobsManagePage
                    .waitForViewToRender();

                dataJobsManagePage
                    .getDataGridStatusIcons()
                    .then(($icons) => {
                        for (const icon of Array.from($icons)) {
                            cy.wrap(icon).should('have.attr', 'data-cy', 'data-pipelines-job-enabled');
                        }
                    });

                dataJobsManagePage
                    .waitForClickThinkingTime();
                dataJobsManagePage
                    .chooseQuickFilter(2);
                dataJobsManagePage
                    .waitForViewToRender();

                dataJobsManagePage
                    .getDataGridStatusIcons()
                    .then(($icons) => {
                        for (const icon of Array.from($icons)) {
                            cy.wrap(icon).should('have.attr', 'data-cy', 'data-pipelines-job-disabled');
                        }
                    });

                dataJobsManagePage
                    .waitForClickThinkingTime();
                dataJobsManagePage
                    .chooseQuickFilter(3);
                dataJobsManagePage
                    .waitForViewToRender();

                dataJobsManagePage
                    .getDataGridStatusIcons()
                    .then(($icons) => {
                        for (const icon of Array.from($icons)) {
                            cy.wrap(icon).should('have.attr', 'data-cy', 'data-pipelines-job-not-deployed');
                        }
                    });

                // Enable data job after job end
                DataJobsManagePage.changeJobStatus(longLivedTestJob.team, longLivedTestJob.job_name, true);
            });
    });

    it('Data Jobs Manage Page - show/hide column when toggling from menu', () => {
        // show panel for show/hide columns
        dataJobsManagePage
            .toggleColumnShowHidePanel();

        // verify correct options are rendered
        dataJobsManagePage
            .getDataGridColumnShowHideOptionsValues()
            .should('have.length', 10)
            .invoke('join', ',')
            .should('eq', 'Description,Deployment Status,Last Execution Duration,Success rate,Next run (UTC),Last Deployed (UTC),Last Deployed By,Notifications,Source,Logs');

        // verify column is not checked in toggling menu
        dataJobsManagePage
            .getDataGridColumnShowHideOption('Notifications')
            .should('exist')
            .should('not.be.checked');

        // verify header cell for column is not rendered
        dataJobsManagePage
            .getDataGridHeaderCell('Notifications')
            .should('have.length', 0);

        // toggle column to render
        dataJobsManagePage
            .checkColumnShowHideOption('Notifications');

        // verify column is checked in toggling menu
        dataJobsManagePage
            .getDataGridColumnShowHideOption('Notifications')
            .should('exist')
            .should('be.checked');

        // verify header cell for column is rendered
        dataJobsManagePage
            .getDataGridHeaderCell('Notifications')
            .should('have.length', 1);

        // toggle column to hide
        dataJobsManagePage
            .uncheckColumnShowHideOption('Notifications');

        // verify column is not checked in toggling menu
        dataJobsManagePage
            .getDataGridColumnShowHideOption('Notifications')
            .should('exist')
            .should('not.be.checked');

        // verify header cell for column is not rendered
        dataJobsManagePage
            .getDataGridHeaderCell('Notifications')
            .should('have.length', 0);

        // hide panel for show/hide columns
        dataJobsManagePage
            .toggleColumnShowHidePanel();
    });

    it('Data Jobs Manage Page - execute now', { tags: '@integration' }, () => {
        const jobName = longLivedTestJob.job_name;
        const team = longLivedTestJob.team;

        dataJobsManagePage
            .chooseQuickFilter(0);

        dataJobsManagePage
            .sortByJobName();

        dataJobsManagePage
            .executeDataJob(jobName);

        // TODO better handling toast message. If tests are executed immediately it will return
        // error 409 conflict and it will say that the job is already executing
        dataJobsManagePage
            .getToastTitle(10000) // Wait up to 10 seconds for Toast to show.
            .should('exist')
            .contains(/Data job Queued for execution|Failed, Data job is already executing/);
    });
});
