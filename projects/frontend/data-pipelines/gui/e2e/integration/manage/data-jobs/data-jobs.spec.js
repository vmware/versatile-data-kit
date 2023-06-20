/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { DataJobsManagePage } from '../../../support/pages/manage/data-jobs/data-jobs.po';
import { DataJobManageDetailsPage } from '../../../support/pages/manage/data-jobs/details/data-job-details.po';

describe('Data Jobs Manage Page', { tags: ['@dataPipelines', '@manageDataJobs', '@manage'] }, () => {
    const descriptionWordsBeforeTruncate = 12;

    /**
     * @type {DataJobsManagePage}
     */
    let dataJobsManagePage;
    /**
     * @type {Array<{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}>}
     */
    let testJobsFixture;
    /**
     * @type {{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}}
     */
    let additionalTestJobFixture;
    /**
     * @type {{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}}
     */
    let shortLivedTestJobWithDeployFixture;

    before(() => {
        return DataJobsManagePage.recordHarIfSupported()
            .then(() => cy.clearLocalStorageSnapshot('data-jobs-manage'))
            .then(() => DataJobsManagePage.login())
            .then(() => cy.saveLocalStorage('data-jobs-manage'))
            .then(() => DataJobsManagePage.deleteShortLivedTestJobsNoDeploy(true))
            .then(() => DataJobsManagePage.createLongLivedJobs('failing'))
            .then(() => DataJobsManagePage.createShortLivedTestJobWithDeploy('v0'))
            .then(() =>
                DataJobsManagePage.loadShortLivedTestJobFixtureWithDeploy('v0').then((loadedTestJob) => {
                    shortLivedTestJobWithDeployFixture = loadedTestJob;

                    return cy.wrap({
                        context: 'manage::1::data-jobs.int.spec::before()',
                        action: 'continue'
                    });
                })
            )
            .then(() => DataJobsManagePage.createShortLivedTestJobsNoDeploy())
            .then(() =>
                DataJobsManagePage.loadShortLivedTestJobsFixtureNoDeploy().then((fixtures) => {
                    testJobsFixture = [fixtures[0], fixtures[1]];
                    additionalTestJobFixture = fixtures[2];

                    return cy.wrap({
                        context: 'manage::2::data-jobs.int.spec::before()',
                        action: 'continue'
                    });
                })
            );
    });

    after(() => {
        DataJobsManagePage.deleteShortLivedTestJobWithDeploy('v0');
        DataJobsManagePage.deleteShortLivedTestJobsNoDeploy();

        DataJobsManagePage.saveHarIfSupported();
    });

    beforeEach(() => {
        cy.restoreLocalStorage('data-jobs-manage');

        DataJobsManagePage.wireUserSession();
        DataJobsManagePage.initInterceptors();
    });

    describe('smoke', { tags: ['@smoke'] }, () => {
        it('page is loaded and grid contains test jobs', () => {
            dataJobsManagePage = DataJobsManagePage.navigateWithSideMenu();

            dataJobsManagePage.getPageTitle().scrollIntoView().should('be.visible').invoke('text').invoke('trim').should('eq', 'Manage Data Jobs');

            dataJobsManagePage.chooseQuickFilter(0);

            // filter by job name substring because there are a lot of jobs, and it could potentially be on second/third page
            dataJobsManagePage.filterByJobName(testJobsFixture[0].job_name.substring(0, 20));

            dataJobsManagePage.getDataGrid().scrollIntoView().should('be.visible');

            testJobsFixture.forEach((testJob) => {
                cy.log('Fixture for name: ' + testJob.job_name);

                dataJobsManagePage.getDataGridCell(testJob.job_name).scrollIntoView().should('be.visible');
            });
        });

        it('grid filters by job name', () => {
            dataJobsManagePage = DataJobsManagePage.navigateTo();

            dataJobsManagePage.chooseQuickFilter(0);

            // filter by job name substring because there are a lot of jobs, and it could potentially be on second/third page
            dataJobsManagePage.filterByJobName(testJobsFixture[0].job_name);

            dataJobsManagePage.getDataGridCell(testJobsFixture[0].job_name).scrollIntoView().should('be.visible');

            dataJobsManagePage.getDataGridCell(testJobsFixture[1].job_name).should('not.exist');
        });

        it('grid searches by job name', () => {
            dataJobsManagePage = DataJobsManagePage.navigateTo();

            dataJobsManagePage.chooseQuickFilter(0);

            dataJobsManagePage.searchByJobName(testJobsFixture[1].job_name);

            dataJobsManagePage.getDataGridCell(testJobsFixture[0].job_name).should('not.exist');

            dataJobsManagePage.getDataGridCell(testJobsFixture[1].job_name).scrollIntoView().should('be.visible');
        });

        it('disable/enable job', () => {
            dataJobsManagePage = DataJobsManagePage.navigateTo();

            dataJobsManagePage.chooseQuickFilter(0);

            const jobName = shortLivedTestJobWithDeployFixture.job_name;

            // filter by job name substring because there are a lot of jobs, and it could potentially be on second/third page
            dataJobsManagePage.filterByJobName(shortLivedTestJobWithDeployFixture.job_name.substring(0, 20));

            //Toggle job status twice, enable to disable and vice versa.
            dataJobsManagePage.toggleJobStatus(shortLivedTestJobWithDeployFixture.job_name);
            dataJobsManagePage.toggleJobStatus(shortLivedTestJobWithDeployFixture.job_name);
        });
    });

    describe('extended', () => {
        it('grid search parameter goes into URL', () => {
            dataJobsManagePage = DataJobsManagePage.navigateTo();

            dataJobsManagePage.chooseQuickFilter(0);

            // filter by job name substring because there are a lot of jobs, and it could potentially be on second/third page
            dataJobsManagePage.filterByJobName(testJobsFixture[0].job_name.substring(0, 20));

            // verify 2 test rows visible
            dataJobsManagePage.getDataGridCell(testJobsFixture[0].job_name).scrollIntoView().should('be.visible');
            dataJobsManagePage.getDataGridCell(testJobsFixture[1].job_name).scrollIntoView().should('be.visible');

            // do search
            dataJobsManagePage.searchByJobName(testJobsFixture[0].job_name);

            // verify 1 test row visible
            dataJobsManagePage.getDataGridCell(testJobsFixture[0].job_name).scrollIntoView().should('be.visible');
            dataJobsManagePage.getDataGridCell(testJobsFixture[1].job_name).should('not.exist');

            // verify url contains search value
            dataJobsManagePage
                .getCurrentUrlNormalized({
                    includePathSegment: true,
                    includeQueryString: true
                })
                .should('deep.equal', {
                    pathSegment: '/manage/data-jobs',
                    queryParams: {
                        search: testJobsFixture[0].job_name,
                        jobName: testJobsFixture[0].job_name.substring(0, 20),
                        deploymentEnabled: 'all'
                    }
                });

            // clear search with clear() method
            dataJobsManagePage.clearSearchField();

            // verify 2 test rows visible
            dataJobsManagePage.getDataGridCell(testJobsFixture[0].job_name).scrollIntoView().should('be.visible');
            dataJobsManagePage.getDataGridCell(testJobsFixture[1].job_name).scrollIntoView().should('be.visible');

            // verify url does not contain search value
            dataJobsManagePage
                .getCurrentUrlNormalized({
                    includePathSegment: true,
                    includeQueryString: true
                })
                .should('deep.equal', {
                    pathSegment: '/manage/data-jobs',
                    queryParams: {
                        jobName: testJobsFixture[0].job_name.substring(0, 20),
                        deploymentEnabled: 'all'
                    }
                });
        });

        it('grid search perform search when URL contains search parameter', () => {
            // navigate with search value in URL
            dataJobsManagePage = DataJobsManagePage.navigateToDataJobUrl(`/manage/data-jobs?search=${testJobsFixture[1].job_name}`);

            dataJobsManagePage.waitForGridToLoad(null);

            dataJobsManagePage.chooseQuickFilter(0);

            // filter by job name substring because there are a lot of jobs, and it could potentially be on second/third page
            dataJobsManagePage.filterByJobName(testJobsFixture[0].job_name.substring(0, 20));

            // verify url contains search value
            dataJobsManagePage
                .getCurrentUrlNormalized({
                    includePathSegment: true,
                    includeQueryString: true
                })
                .should('deep.equal', {
                    pathSegment: '/manage/data-jobs',
                    queryParams: {
                        search: testJobsFixture[1].job_name,
                        jobName: testJobsFixture[0].job_name.substring(0, 20),
                        deploymentEnabled: 'all'
                    }
                });

            // verify 1 test row visible
            dataJobsManagePage.getDataGridCell(testJobsFixture[0].job_name).should('not.exist');
            dataJobsManagePage.getDataGridCell(testJobsFixture[1].job_name).scrollIntoView().should('be.visible');

            // clear search with button
            dataJobsManagePage.clearSearchFieldWithButton();

            // verify 2 test rows visible
            dataJobsManagePage.getDataGridCell(testJobsFixture[0].job_name).scrollIntoView().should('be.visible');
            dataJobsManagePage.getDataGridCell(testJobsFixture[1].job_name).scrollIntoView().should('be.visible');

            // verify url does not contain search value
            dataJobsManagePage
                .getCurrentUrlNormalized({
                    includePathSegment: true,
                    includeQueryString: true
                })
                .should('deep.equal', {
                    pathSegment: '/manage/data-jobs',
                    queryParams: {
                        jobName: testJobsFixture[0].job_name.substring(0, 20),
                        deploymentEnabled: 'all'
                    }
                });
        });

        it('refresh shows newly created job', () => {
            dataJobsManagePage = DataJobsManagePage.navigateTo();

            dataJobsManagePage.chooseQuickFilter(0);

            // filter by job name substring because there are a lot of jobs, and it could potentially be on second/third page
            dataJobsManagePage.filterByJobName(testJobsFixture[0].job_name.substring(0, 20));

            dataJobsManagePage.getDataGridCell(testJobsFixture[0].job_name).should('have.text', testJobsFixture[0].job_name);

            dataJobsManagePage.getDataGridCell(additionalTestJobFixture.job_name).should('not.exist');

            DataJobsManagePage.createAdditionalShortLivedTestJobsNoDeploy();

            dataJobsManagePage.refreshDataGrid();

            dataJobsManagePage.getDataGridCell(additionalTestJobFixture.job_name).should('have.text', additionalTestJobFixture.job_name);
        });

        it('click on edit button opens new page with Job details', () => {
            dataJobsManagePage = DataJobsManagePage.navigateWithSideMenu();

            dataJobsManagePage.chooseQuickFilter(0);

            // filter by job name substring because there are a lot of jobs, and it could potentially be on second/third page
            dataJobsManagePage.filterByJobName(testJobsFixture[0].job_name.substring(0, 20));

            dataJobsManagePage.openJobDetails(testJobsFixture[0].team, testJobsFixture[0].job_name);

            const dataJobManageDetailsPage = DataJobManageDetailsPage.getPage();

            dataJobManageDetailsPage.getPageTitle().scrollIntoView().should('be.visible').invoke('text').invoke('trim').should('eq', `Data Job: ${testJobsFixture[0].job_name}`);

            dataJobManageDetailsPage.getDescription().scrollIntoView().should('be.visible').should('contain.text', testJobsFixture[0].description.split(' ').slice(0, descriptionWordsBeforeTruncate).join(' '));

            dataJobManageDetailsPage.getSchedule().scrollIntoView().should('be.visible');

            dataJobManageDetailsPage.getDeploymentStatus('not-deployed').scrollIntoView().should('be.visible').should('have.text', 'Not Deployed');
        });

        it('quick filters', () => {
            // Disable data job before test start
            DataJobsManagePage.changeLongLivedJobStatus('failing', true)
                .then(() => DataJobsManagePage.changeShortLivedTestJobWithDeployStatus('v0', false))
                .then(() => {
                    dataJobsManagePage = DataJobsManagePage.navigateTo();

                    dataJobsManagePage.waitForClickThinkingTime();
                    dataJobsManagePage.chooseQuickFilter(0);

                    dataJobsManagePage.getDataGridStatusIcons().then(($icons) => {
                        for (const icon of Array.from($icons)) {
                            cy.wrap(icon).invoke('attr', 'data-cy').should('match', new RegExp('data-pipelines-job-(enabled|disabled|not-deployed)'));
                        }
                    });

                    dataJobsManagePage.waitForClickThinkingTime();
                    dataJobsManagePage.chooseQuickFilter(1);

                    dataJobsManagePage.getDataGridStatusIcons().then(($icons) => {
                        for (const icon of Array.from($icons)) {
                            cy.wrap(icon).should('have.attr', 'data-cy', 'data-pipelines-job-enabled');
                        }
                    });

                    dataJobsManagePage.waitForClickThinkingTime();
                    dataJobsManagePage.chooseQuickFilter(2);

                    dataJobsManagePage.getDataGridStatusIcons().then(($icons) => {
                        for (const icon of Array.from($icons)) {
                            cy.wrap(icon).should('have.attr', 'data-cy', 'data-pipelines-job-disabled');
                        }
                    });

                    dataJobsManagePage.waitForClickThinkingTime();
                    dataJobsManagePage.chooseQuickFilter(3);

                    dataJobsManagePage.getDataGridStatusIcons().then(($icons) => {
                        for (const icon of Array.from($icons)) {
                            cy.wrap(icon).should('have.attr', 'data-cy', 'data-pipelines-job-not-deployed');
                        }
                    });

                    // Enable data job after job end
                    DataJobsManagePage.changeShortLivedTestJobWithDeployStatus('v0', true);
                });
        });

        it('filter description data jobs', () => {
            dataJobsManagePage = DataJobsManagePage.navigateTo();

            dataJobsManagePage.chooseQuickFilter(0);

            // show panel for show/hide columns
            dataJobsManagePage.toggleColumnShowHidePanel();

            // verify column is not checked in toggling menu
            dataJobsManagePage.getDataGridColumnShowHideOption('Description').should('exist').should('not.be.checked');

            // verify header cell for column is not rendered
            dataJobsManagePage.getDataGridHeaderCell('Description').should('have.length', 0);

            // toggle column to render
            dataJobsManagePage.checkColumnShowHideOption('Description');

            // verify column is checked in toggling menu
            dataJobsManagePage.getHeaderColumnDescriptionName().should('exist');

            // filter by job description because
            dataJobsManagePage.filterByJobDescription('Test description 1');

            // verify url contains description value
            dataJobsManagePage.getCurrentUrl().should('match', new RegExp(`\\/manage\\/data-jobs\\?deploymentEnabled=all&description=Test%20description%201$`));

            dataJobsManagePage.getDataGridCell(testJobsFixture[0].job_name).scrollIntoView().should('be.visible');

            dataJobsManagePage.getDataGridCell(testJobsFixture[1].job_name).should('not.exist');
        });

        it('perform filtering by description when URL contains description parameter', () => {
            // navigate with search value in URL
            dataJobsManagePage = DataJobsManagePage.navigateToDataJobUrl(`/manage/data-jobs?deploymentEnabled=enabled&description=Test%20description%201`);

            dataJobsManagePage.chooseQuickFilter(0);
            dataJobsManagePage.waitForGridToLoad(null);

            // show panel for show/hide columns
            dataJobsManagePage.toggleColumnShowHidePanel();

            // toggle column to render
            dataJobsManagePage.checkColumnShowHideOption('Description');

            // verify url contains search value
            dataJobsManagePage
                .getCurrentUrlNormalized({
                    includePathSegment: true,
                    includeQueryString: true
                })
                .should('deep.equal', {
                    pathSegment: '/manage/data-jobs',
                    queryParams: {
                        deploymentEnabled: 'all',
                        description: 'Test%20description%201'
                    }
                });

            // verify 1 test row visible
            dataJobsManagePage.getDataGridCell(testJobsFixture[0].job_name).scrollIntoView().should('be.visible');

            dataJobsManagePage.getDataGridCell(testJobsFixture[1].job_name).should('not.exist');
        });

        it('show/hide column when toggling from menu', () => {
            dataJobsManagePage = DataJobsManagePage.navigateTo();

            // show panel for show/hide columns
            dataJobsManagePage.toggleColumnShowHidePanel();

            // verify correct options are rendered
            dataJobsManagePage.getDataGridColumnShowHideOptionsValues().should('have.length', 10).invoke('join', ',').should('eq', 'Description,Deployment Status,Last Execution Duration,Success rate,Next run (UTC),Last Deployed (UTC),Last Deployed By,Notifications,Source,Logs');

            // verify column is not checked in toggling menu
            dataJobsManagePage.getDataGridColumnShowHideOption('Notifications').should('exist').should('not.be.checked');

            // verify header cell for column is not rendered
            dataJobsManagePage.getDataGridHeaderCell('Notifications').should('have.length', 0);

            // toggle column to render
            dataJobsManagePage.checkColumnShowHideOption('Notifications');

            // verify column is checked in toggling menu
            dataJobsManagePage.getDataGridColumnShowHideOption('Notifications').should('exist').should('be.checked');

            // verify header cell for column is rendered
            dataJobsManagePage.getDataGridHeaderCell('Notifications').should('have.length', 1);

            // toggle column to hide
            dataJobsManagePage.uncheckColumnShowHideOption('Notifications');

            // verify column is not checked in toggling menu
            dataJobsManagePage.getDataGridColumnShowHideOption('Notifications').should('exist').should('not.be.checked');

            // verify header cell for column is not rendered
            dataJobsManagePage.getDataGridHeaderCell('Notifications').should('have.length', 0);

            // hide panel for show/hide columns
            dataJobsManagePage.toggleColumnShowHidePanel();
        });

        it('execute now', () => {
            dataJobsManagePage = DataJobsManagePage.navigateTo();

            dataJobsManagePage.chooseQuickFilter(0);

            // filter by job name substring because there are a lot of jobs, and it could potentially be on second/third page
            dataJobsManagePage.filterByJobName(shortLivedTestJobWithDeployFixture.job_name.substring(0, 20));

            DataJobsManagePage.waitForShortLivedTestJobWithDeployExecutionToComplete('v0');

            dataJobsManagePage.executeDataJob(shortLivedTestJobWithDeployFixture.job_name);

            // TODO better handling toast message. If tests are executed immediately it will return
            // error 409 conflict and it will say that the job is already executing
            dataJobsManagePage
                .getToastTitle(10000) // Wait up to 10 seconds for Toast to show.
                .should('exist')
                .contains(/Data job Queued for execution|Failed, Data job is already executing/);
        });

        it(`execute now is disabled when Job doesn't have deployment`, () => {
            dataJobsManagePage = DataJobsManagePage.navigateTo();

            const jobName = testJobsFixture[0].job_name;

            dataJobsManagePage.chooseQuickFilter(0);

            // filter by job name substring because there are a lot of jobs, and it could potentially be on second/third page
            dataJobsManagePage.filterByJobName(jobName.substring(0, 20));

            dataJobsManagePage.selectRow(jobName);

            dataJobsManagePage.waitForClickThinkingTime();

            dataJobsManagePage.getExecuteNowGridButton().should('be.disabled');
        });
    });
});
