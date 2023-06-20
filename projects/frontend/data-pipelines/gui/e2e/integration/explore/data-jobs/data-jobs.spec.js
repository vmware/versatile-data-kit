/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { DataJobsExplorePage } from '../../../support/pages/explore/data-jobs/data-jobs.po';
import { DataJobExploreDetailsPage } from '../../../support/pages/explore/data-jobs/details/data-job-details.po';

describe('Data Jobs Explore Page', { tags: ['@dataPipelines', '@exploreDataJobs', '@explore'] }, () => {
    /**
     * @type {DataJobsExplorePage}
     */
    let dataJobsExplorePage;
    /**
     * @type {Array<{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}>}
     */
    let testJobsFixture;
    /**
     * @type {{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}}
     */
    let additionalTestJobFixture;

    before(() => {
        return DataJobsExplorePage.recordHarIfSupported()
            .then(() => cy.clearLocalStorageSnapshot('data-jobs-explore'))
            .then(() => DataJobsExplorePage.login())
            .then(() => cy.saveLocalStorage('data-jobs-explore'))
            .then(() => DataJobsExplorePage.deleteShortLivedTestJobsNoDeploy(true))
            .then(() => DataJobsExplorePage.createShortLivedTestJobsNoDeploy())
            .then(() =>
                DataJobsExplorePage.loadShortLivedTestJobsFixtureNoDeploy().then((fixtures) => {
                    testJobsFixture = [fixtures[0], fixtures[1]];
                    additionalTestJobFixture = fixtures[2];

                    return cy.wrap({
                        context: 'explore::data-jobs.spec::before()',
                        action: 'continue'
                    });
                })
            );
    });

    after(() => {
        DataJobsExplorePage.deleteShortLivedTestJobsNoDeploy();

        DataJobsExplorePage.saveHarIfSupported();
    });

    beforeEach(() => {
        cy.restoreLocalStorage('data-jobs-explore');

        DataJobsExplorePage.wireUserSession();
        DataJobsExplorePage.initInterceptors();
    });

    describe('smoke', { tags: ['@smoke'] }, () => {
        it('page is loaded and shows data jobs', () => {
            dataJobsExplorePage = DataJobsExplorePage.navigateWithSideMenu();

            dataJobsExplorePage.getPageTitle().scrollIntoView().should('be.visible').invoke('text').invoke('trim').should('eq', 'Explore Data Jobs');

            dataJobsExplorePage.getDataGrid().scrollIntoView().should('be.visible');

            // filter by job name substring because there are a lot of jobs, and it could potentially be on second/third page
            dataJobsExplorePage.filterByJobName(testJobsFixture[0].job_name.substring(0, 20));

            testJobsFixture.forEach((testJob) => {
                cy.log('Fixture for name: ' + testJob.job_name);

                dataJobsExplorePage.getDataGridCell(testJob.job_name).scrollIntoView().should('be.visible');
            });
        });

        it('navigates to data job', () => {
            cy.log('Fixture for name: ' + testJobsFixture[0].job_name);

            dataJobsExplorePage = DataJobsExplorePage.navigateTo();

            // filter by job name substring because there are a lot of jobs, and it could potentially be on second/third page
            dataJobsExplorePage.filterByJobName(testJobsFixture[0].job_name.substring(0, 20));

            dataJobsExplorePage.openJobDetails(testJobsFixture[0].team, testJobsFixture[0].job_name);

            const dataJobExploreDetailsPage = DataJobExploreDetailsPage.getPage();

            dataJobExploreDetailsPage.getPageTitle().scrollIntoView().should('be.visible').should('contains.text', testJobsFixture[0].job_name);

            dataJobExploreDetailsPage.getDescriptionField().scrollIntoView().should('be.visible').should('contain.text', testJobsFixture[0].description);
        });
    });

    describe('extended', () => {
        it('refresh load newly created data jobs', () => {
            dataJobsExplorePage = DataJobsExplorePage.navigateTo();

            // filter by job name substring because there are a lot of jobs, and it could potentially be on second/third page
            dataJobsExplorePage.filterByJobName(testJobsFixture[0].job_name.substring(0, 20));

            dataJobsExplorePage.getDataGridCell(testJobsFixture[0].job_name).invoke('text').invoke('trim').should('eq', testJobsFixture[0].job_name);

            dataJobsExplorePage.getDataGridCell(additionalTestJobFixture.job_name).should('not.exist');

            DataJobsExplorePage.createAdditionalShortLivedTestJobsNoDeploy();

            dataJobsExplorePage.refreshDataGrid();

            dataJobsExplorePage.getDataGridCell(additionalTestJobFixture.job_name).invoke('text').invoke('trim').should('eq', additionalTestJobFixture.job_name);
        });

        it('filters data jobs', () => {
            cy.log('Fixture for name: ' + testJobsFixture[0].job_name);

            dataJobsExplorePage = DataJobsExplorePage.navigateTo();

            dataJobsExplorePage.filterByJobName(testJobsFixture[0].job_name);

            dataJobsExplorePage.getDataGridCell(testJobsFixture[0].job_name).scrollIntoView().should('be.visible');

            dataJobsExplorePage.getDataGridCell(testJobsFixture[1].job_name).should('not.exist');
        });

        it('searches data jobs', () => {
            cy.log('Fixture for name: ' + testJobsFixture[0].job_name);

            dataJobsExplorePage = DataJobsExplorePage.navigateTo();

            // filter by job name substring because there are a lot of jobs, and it could potentially be on second/third page
            dataJobsExplorePage.filterByJobName(testJobsFixture[1].job_name.substring(0, 20));

            dataJobsExplorePage.getDataGridCell(testJobsFixture[1].job_name).scrollIntoView().should('be.visible');

            // verify url contains jobName value
            dataJobsExplorePage.getCurrentUrl().should('match', new RegExp(`\\/explore\\/data-jobs\\?jobName=${testJobsFixture[1].job_name.substring(0, 20)}$`));

            dataJobsExplorePage.searchByJobName(testJobsFixture[0].job_name);

            dataJobsExplorePage.getDataGridCell(testJobsFixture[0].job_name).scrollIntoView().should('be.visible');

            dataJobsExplorePage.getDataGridCell(testJobsFixture[1].job_name).should('not.exist');
        });

        it('searches data jobs, search parameter goes into URL', () => {
            cy.log('Fixture for name: ' + testJobsFixture[0].job_name);

            dataJobsExplorePage = DataJobsExplorePage.navigateTo();

            // filter by job name substring because there are a lot of jobs, and it could potentially be on second/third page
            dataJobsExplorePage.filterByJobName(testJobsFixture[0].job_name.substring(0, 20));

            // verify 2 test rows visible
            dataJobsExplorePage.getDataGridCell(testJobsFixture[0].job_name).scrollIntoView().should('be.visible');
            dataJobsExplorePage.getDataGridCell(testJobsFixture[1].job_name).scrollIntoView().should('be.visible');

            // do search
            dataJobsExplorePage.searchByJobName(testJobsFixture[0].job_name);

            // verify 1 test row visible
            dataJobsExplorePage.getDataGridCell(testJobsFixture[0].job_name).scrollIntoView().should('be.visible');
            dataJobsExplorePage.getDataGridCell(testJobsFixture[1].job_name).should('not.exist');

            // verify url contains search value
            dataJobsExplorePage.getCurrentUrl().should('match', new RegExp(`\\/explore\\/data-jobs\\?jobName=${testJobsFixture[0].job_name.substring(0, 20)}&search=${testJobsFixture[0].job_name}$`));

            // clear search with clear() method
            dataJobsExplorePage.clearSearchField();

            // verify 2 test rows visible
            dataJobsExplorePage.getDataGridCell(testJobsFixture[0].job_name).scrollIntoView().should('be.visible');
            dataJobsExplorePage.getDataGridCell(testJobsFixture[1].job_name).scrollIntoView().should('be.visible');

            // verify url does not contain search value
            dataJobsExplorePage.getCurrentUrl().should('match', new RegExp(`\\/explore\\/data-jobs\\?jobName=${testJobsFixture[0].job_name.substring(0, 20)}$`));
        });

        it('searches data jobs, perform search when URL contains search parameter', () => {
            cy.log('Fixture for name: ' + testJobsFixture[1].job_name);

            // navigate with search value in URL
            dataJobsExplorePage = DataJobsExplorePage.navigateToDataJobUrl(`/explore/data-jobs?search=${testJobsFixture[1].job_name}`);

            dataJobsExplorePage.waitForGridToLoad(null);

            // verify url contains search value
            dataJobsExplorePage
                .getCurrentUrlNormalized({
                    includePathSegment: true,
                    includeQueryString: true
                })
                .should('deep.equal', {
                    pathSegment: '/explore/data-jobs',
                    queryParams: {
                        search: testJobsFixture[1].job_name
                    }
                });

            // verify 1 test row visible
            dataJobsExplorePage.getDataGridCell(testJobsFixture[0].job_name).should('not.exist');
            dataJobsExplorePage.getDataGridCell(testJobsFixture[1].job_name).scrollIntoView().should('be.visible');

            // clear search with button
            dataJobsExplorePage.clearSearchFieldWithButton();

            // filter by job name substring because there are a lot of jobs, and it could potentially be on second/third page
            dataJobsExplorePage.filterByJobName(testJobsFixture[0].job_name.substring(0, 20));

            // verify 2 test rows visible
            dataJobsExplorePage.getDataGridCell(testJobsFixture[0].job_name).scrollIntoView().should('be.visible');
            dataJobsExplorePage.getDataGridCell(testJobsFixture[1].job_name).scrollIntoView().should('be.visible');

            // verify url does not contain search value
            dataJobsExplorePage
                .getCurrentUrlNormalized({
                    includePathSegment: true,
                    includeQueryString: true
                })
                .should('deep.equal', {
                    pathSegment: '/explore/data-jobs',
                    queryParams: {
                        jobName: testJobsFixture[0].job_name.substring(0, 20)
                    }
                });
        });

        it('filter description data jobs', () => {
            dataJobsExplorePage = DataJobsExplorePage.navigateTo();

            // show panel for show/hide columns
            dataJobsExplorePage.toggleColumnShowHidePanel();

            // verify column is not checked in toggling menu
            dataJobsExplorePage.getDataGridColumnShowHideOption('Description').should('exist').should('not.be.checked');

            // verify header cell for column is not rendered
            dataJobsExplorePage.getDataGridHeaderCell('Description').should('have.length', 0);

            // toggle column to render
            dataJobsExplorePage.checkColumnShowHideOption('Description');

            // verify column is checked in toggling menu
            dataJobsExplorePage.getHeaderColumnDescriptionName().should('exist');

            // filter by job description
            dataJobsExplorePage.filterByJobDescription('Test description 1');

            // verify url contains description value
            dataJobsExplorePage.getCurrentUrl().should('match', new RegExp(`\\/explore\\/data-jobs\\?description=Test%20description%201$`));

            dataJobsExplorePage.getDataGridCell(testJobsFixture[0].job_name).scrollIntoView().should('be.visible');

            dataJobsExplorePage.getDataGridCell(testJobsFixture[1].job_name).should('not.exist');
        });

        it('perform filtering by description when URL contains description parameter', () => {
            // navigate with description value in URL
            dataJobsExplorePage = DataJobsExplorePage.navigateToDataJobUrl(`/explore/data-jobs?description=Test%20description%201`);

            dataJobsExplorePage.waitForGridToLoad(null);

            // show panel for show/hide columns
            dataJobsExplorePage.toggleColumnShowHidePanel();

            // toggle column to render
            dataJobsExplorePage.checkColumnShowHideOption('Description');

            // verify url contains description value
            dataJobsExplorePage
                .getCurrentUrlNormalized({
                    includePathSegment: true,
                    includeQueryString: true
                })
                .should('deep.equal', {
                    pathSegment: '/explore/data-jobs',
                    queryParams: {
                        description: 'Test%20description%201'
                    }
                });

            // verify 1 test row visible
            dataJobsExplorePage.getDataGridCell(testJobsFixture[0].job_name).scrollIntoView().should('be.visible');

            dataJobsExplorePage.getDataGridCell(testJobsFixture[1].job_name).should('not.exist');
        });

        it('show/hide column when toggling from menu', () => {
            dataJobsExplorePage = DataJobsExplorePage.navigateTo();

            // show panel for show/hide columns
            dataJobsExplorePage.toggleColumnShowHidePanel();

            // verify correct options are rendered
            dataJobsExplorePage.getDataGridColumnShowHideOptionsValues().should('have.length', 9).invoke('join', ',').should('eq', 'Description,Deployment Status,Last Execution Duration,Success rate,Next run (UTC),Last Deployed (UTC),Last Deployed By,Source,Logs');

            // verify column is not checked in toggling menu
            dataJobsExplorePage.getDataGridColumnShowHideOption('Last Execution Duration').should('exist').should('not.be.checked');

            // verify header cell for column is not rendered
            dataJobsExplorePage.getDataGridHeaderCell('Last Execution Duration').should('have.length', 0);

            // toggle column to render
            dataJobsExplorePage.checkColumnShowHideOption('Last Execution Duration');

            // verify column is checked in toggling menu
            dataJobsExplorePage.getDataGridColumnShowHideOption('Last Execution Duration').should('exist').should('be.checked');

            // verify header cell for column is rendered
            dataJobsExplorePage.getDataGridHeaderCell('Last Execution Duration').should('have.length', 1);

            // toggle column to hide
            dataJobsExplorePage.uncheckColumnShowHideOption('Last Execution Duration');

            // verify column is not checked in toggling menu
            dataJobsExplorePage.getDataGridColumnShowHideOption('Last Execution Duration').should('exist').should('not.be.checked');

            // verify header cell for column is not rendered
            dataJobsExplorePage.getDataGridHeaderCell('Last Execution Duration').should('have.length', 0);

            // hide panel for show/hide columns
            dataJobsExplorePage.toggleColumnShowHidePanel();
        });
    });
});
