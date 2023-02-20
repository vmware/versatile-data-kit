/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { DataJobBasePO } from '../../../support/application/data-job-base.po';
import { DataJobsManagePage } from '../../../support/pages/app/lib/manage/data-jobs.po';
import { DataJobManageExecutionsPage } from '../../../support/pages/app/lib/manage/data-job-executions.po';
import { applyGlobalEnvSettings } from '../../../support/helpers/commands.helpers';

describe('Data Job Manage Executions Page', { tags: ['@dataPipelines', '@manageDataJobExecutions'] }, () => {
    let longLivedTestJob;

    before(() => {
        return DataJobManageExecutionsPage.recordHarIfSupported()
                                          .then(() => cy.clearLocalStorageSnapshot('data-job-manage-executions'))
                                          .then(() => DataJobManageExecutionsPage.login())
                                          .then(() => cy.saveLocalStorage('data-job-manage-executions'))
                                          .then(() => cy.prepareLongLivedTestJob())
                                          .then(() => cy.createTwoExecutionsLongLivedTestJob())
                                          .then(() => cy.fixture('lib/manage/e2e-cypress-dp-test.json'))
                                          .then((loadedTestJob) => {
                                              longLivedTestJob = applyGlobalEnvSettings(loadedTestJob);

                                              return cy.wrap({ context: 'manage::data-job-executions.spec::before()', action: 'continue' });
                                          });
    });

    after(() => {
        DataJobManageExecutionsPage.saveHarIfSupported();
    });

    beforeEach(() => {
        cy.restoreLocalStorage('data-job-manage-executions');

        DataJobManageExecutionsPage.initBackendRequestInterceptor();
    });

    describe('Sanity', { tags: '@integration' }, () => {
        it(`Data Job Manage Executions Page - should open Details and verify Executions tab is displayed and navigates`, () => {
            cy.log('Fixture for name: ' + longLivedTestJob.job_name);

            const dataJobsManagePage = DataJobsManagePage.navigateTo();

            dataJobsManagePage
                .clickOnContentContainer();

            dataJobsManagePage
                .chooseQuickFilter(0);

            dataJobsManagePage
                .openJobDetails(longLivedTestJob.team, longLivedTestJob.job_name);

            const dataJobBasePage = DataJobBasePO
                .getPage();

            dataJobBasePage
                .getDetailsTab()
                .should('exist')
                .should('have.class', 'active');

            dataJobBasePage
                .getExecutionsTab()
                .should('exist')
                .should('not.have.class', 'active');

            dataJobBasePage
                .openExecutionsTab();

            const dataJobExecutionsPage = DataJobManageExecutionsPage
                .getPage();

            dataJobExecutionsPage
                .getDetailsTab()
                .should('exist')
                .should('not.have.class', 'active');

            dataJobExecutionsPage
                .getExecutionsTab()
                .should('exist')
                .should('have.class', 'active');

            dataJobExecutionsPage
                .getDataGrid()
                .should('exist');
        });

        it('Data Job Manage Executions Page - should verify on URL navigate to Executions will open the page', () => {
            const dataJobExecutionsPage = DataJobManageExecutionsPage
                .navigateTo(longLivedTestJob.team, longLivedTestJob.job_name);

            dataJobExecutionsPage
                .getCurrentUrl()
                .should('match', new RegExp(`\\/manage\\/data-jobs\\/${longLivedTestJob.team}\\/${longLivedTestJob.job_name}\\/executions$`));

            dataJobExecutionsPage
                .getDetailsTab()
                .should('exist')
                .should('not.have.class', 'active');

            dataJobExecutionsPage
                .getExecutionsTab()
                .should('exist')
                .should('have.class', 'active');

            dataJobExecutionsPage
                .getDataGrid()
                .should('exist');
        });

        it('Data Job Manage Executions Page - should verify elements are rendered in DOM', () => {
            const dataJobExecutionsPage = DataJobManageExecutionsPage
                .navigateTo(longLivedTestJob.team, longLivedTestJob.job_name);

            dataJobExecutionsPage
                .getMainTitle()
                .should('be.visible')
                .should('contains.text', longLivedTestJob.job_name);

            dataJobExecutionsPage
                .getDetailsTab()
                .should('exist')
                .should('not.have.class', 'active');

            dataJobExecutionsPage
                .getExecutionsTab()
                .should('exist')
                .should('have.class', 'active');

            dataJobExecutionsPage
                .getExecuteNowButton()
                .should('exist');

            dataJobExecutionsPage
                .getActionDropdownBtn()
                .should('exist');

            dataJobExecutionsPage
                .openActionDropdown();

            dataJobExecutionsPage
                .getDeleteJobBtn()
                .should('exist');

            dataJobExecutionsPage
                .clickOnContentContainer();

            dataJobExecutionsPage
                .waitForSmartDelay();

            dataJobExecutionsPage
                .getTimePeriod()
                .should('exist');

            dataJobExecutionsPage
                .getStatusChart()
                .should('exist');

            dataJobExecutionsPage
                .getDurationChart()
                .should('exist');

            dataJobExecutionsPage
                .getDataGrid()
                .should('exist');

            dataJobExecutionsPage
                .getDataGridRows()
                .should('have.length.gt', 0);
        });

        it('Data Job Manage Executions Page - should verify cancel execution button works properly', () => {
            const dataJobExecutionsPage = DataJobManageExecutionsPage
                .navigateTo(longLivedTestJob.team, longLivedTestJob.job_name);

            dataJobExecutionsPage
                .initPostExecutionInterceptor();
            dataJobExecutionsPage
                .initDeleteExecutionInterceptor();
            dataJobExecutionsPage
                .initGetExecutionInterceptor();
            dataJobExecutionsPage
                .initGetExecutionsInterceptor();

            dataJobExecutionsPage
                .getExecutionsTab()
                .should('exist')
                .should('have.class', 'active');

            // Execute data job and check if the execution status after that is Running or Submitted
            dataJobExecutionsPage
                .getExecuteNowButton()
                .should('exist');
            dataJobExecutionsPage
                .executeNow();
            dataJobExecutionsPage
                .getConfirmDialogButton()
                .should('exist')
                .click({ force: true });
            dataJobExecutionsPage
                .waitForPostExecutionCompletion();
            dataJobExecutionsPage
                .waitForDataJobStartExecute();

            dataJobExecutionsPage
                .waitForViewToRenderShort();

            dataJobExecutionsPage
                .getExecutionStatus()
                .first()
                .contains(/Running|Submitted/);

            // Cancel data job execution and check if the status after that is Cancelled
            dataJobExecutionsPage
                .getCancelExecutionButton()
                .should('exist')
                .click({ force: true })
            dataJobExecutionsPage
                .getConfirmDialogButton()
                .should('exist')
                .click({ force: true });
            dataJobExecutionsPage
                .waitForDeleteExecutionCompletion();
            dataJobExecutionsPage
                .waitForDataJobStopExecute();

            dataJobExecutionsPage
                .waitForViewToRenderShort();

            dataJobExecutionsPage
                .getExecutionStatus()
                .first()
                .should('contains.text', 'Canceled');
        });
    });

    it('Data Job Manage Executions Page - should verify time period is in correct format', () => {
        const dataJobExecutionsPage = DataJobManageExecutionsPage
            .navigateTo(longLivedTestJob.team, longLivedTestJob.job_name);

        dataJobExecutionsPage
            .getTimePeriod()
            .invoke('text')
            .invoke('trim')
            .should('match', new RegExp(`^\\w+\\s\\d+,\\s\\d+,\\s\\d+:\\d+:\\d+\\s(AM|PM)\\sto\\s\\w+\\s\\d+,\\s\\d+,\\s\\d+:\\d+:\\d+\\s(AM|PM)$`));
    });

    it('Data Job Manage Executions Page - should verify refresh button will show spinner and then load data', () => {
        const dataJobExecutionsPage = DataJobManageExecutionsPage
            .navigateTo(longLivedTestJob.team, longLivedTestJob.job_name);

        dataJobExecutionsPage
            .getDataGrid()
            .should('exist');

        dataJobExecutionsPage
            .getExecLoadingSpinner()
            .should('not.exist');

        dataJobExecutionsPage
            .getDataGridSpinner()
            .should('not.exist');

        dataJobExecutionsPage
            .waitForActionThinkingTime();

        dataJobExecutionsPage
            .refreshExecData();

        dataJobExecutionsPage
            .getDataGrid()
            .should('exist');

        dataJobExecutionsPage
            .getExecLoadingSpinner()
            .should('exist');

        dataJobExecutionsPage
            .getDataGridSpinner()
            .should('exist');

        dataJobExecutionsPage
            .waitForBackendRequestCompletion();

        dataJobExecutionsPage
            .waitForViewToRender();

        dataJobExecutionsPage
            .getDataGrid()
            .should('exist');

        dataJobExecutionsPage
            .getExecLoadingSpinner()
            .should('not.exist');

        dataJobExecutionsPage
            .getDataGridSpinner()
            .should('not.exist');
    });

    describe('DataGrid Filters', () => {
        it('Data Job Manage Executions Page - should verify status filter options are rendered', () => {
            const dataJobExecutionsPage = DataJobManageExecutionsPage
                .navigateTo(longLivedTestJob.team, longLivedTestJob.job_name);

            dataJobExecutionsPage
                .openStatusFilter();

            dataJobExecutionsPage
                .getDataGridPopupFilter()
                .should('exist');

            dataJobExecutionsPage
                .getDataGridExecStatusFilters()
                .then((elements) => Array.from(elements).map((el) => el.innerText))
                .should('deep.equal', ['Success', 'Platform Error', 'User Error', 'Running', 'Submitted', 'Skipped', 'Canceled']);

            dataJobExecutionsPage
                .closeFilter();

            dataJobExecutionsPage
                .getDataGridPopupFilter()
                .should('not.exist');
        });

        it('Data Job Manage Executions Page - should verify type filter options are rendered', () => {
            const dataJobExecutionsPage = DataJobManageExecutionsPage
                .navigateTo(longLivedTestJob.team, longLivedTestJob.job_name);

            dataJobExecutionsPage
                .openTypeFilter();

            dataJobExecutionsPage
                .getDataGridPopupFilter()
                .should('exist');

            dataJobExecutionsPage
                .getDataGridExecTypeFilters()
                .then((elements) => Array.from(elements).map((el) => el.innerText))
                .should('deep.equal', ['Manual', 'Scheduled']);

            dataJobExecutionsPage
                .closeFilter();

            dataJobExecutionsPage
                .getDataGridPopupFilter()
                .should('not.exist');
        });

        it('Data Job Manage Executions Page - should verify id filter render input and filters correctly', () => {
            const dataJobExecutionsPage = DataJobManageExecutionsPage
                .navigateTo(longLivedTestJob.team, longLivedTestJob.job_name);

            dataJobExecutionsPage
                .getDataGridRows()
                .should('have.length.gt', 0);

            dataJobExecutionsPage
                .openIDFilter();

            dataJobExecutionsPage
                .getDataGridPopupFilter()
                .should('exist');

            dataJobExecutionsPage
                .typeToFilterInput('xyxyxy');

            dataJobExecutionsPage
                .getDataGridRows()
                .should('have.length', 0);

            dataJobExecutionsPage
                .clearFilterInput();

            dataJobExecutionsPage
                .getDataGridRows()
                .should('have.length.gt', 0);

            dataJobExecutionsPage
                .closeFilter();

            dataJobExecutionsPage
                .getDataGridPopupFilter()
                .should('not.exist');
        });

        it('Data Job Manage Executions Page - should verify version filter render input and filters correctly', () => {
            const dataJobExecutionsPage = DataJobManageExecutionsPage
                .navigateTo(longLivedTestJob.team, longLivedTestJob.job_name);

            dataJobExecutionsPage
                .getDataGridRows()
                .should('have.length.gt', 0);

            dataJobExecutionsPage
                .openVersionFilter();

            dataJobExecutionsPage
                .getDataGridPopupFilter()
                .should('exist');

            dataJobExecutionsPage
                .typeToFilterInput('xyxyxy');

            dataJobExecutionsPage
                .getDataGridRows()
                .should('have.length', 0);

            dataJobExecutionsPage
                .clearFilterInput();

            dataJobExecutionsPage
                .getDataGridRows()
                .should('have.length.gt', 0);

            dataJobExecutionsPage
                .closeFilter();

            dataJobExecutionsPage
                .getDataGridPopupFilter()
                .should('not.exist');
        });
    });

    describe('DataGrid Sort', () => {
        it('Data Job Manage Executions Page - should verify duration sort works', () => {
            const dataJobExecutionsPage = DataJobManageExecutionsPage
                .navigateTo(longLivedTestJob.team, longLivedTestJob.job_name);

            dataJobExecutionsPage
                .getDataGridRows()
                .should('have.length.gt', 0);

            dataJobExecutionsPage
                .getDataGridExecDurationHeader()
                .should('exist')
                .invoke('attr', 'aria-sort')
                .should('eq', 'none');

            dataJobExecutionsPage
                .sortByExecDuration();

            dataJobExecutionsPage
                .getDataGridExecDurationHeader()
                .should('exist')
                .invoke('attr', 'aria-sort')
                .should('eq', 'ascending');

            dataJobExecutionsPage
                .getDataGridRows()
                .should('have.length.gt', 0);

            dataJobExecutionsPage
                .getDataGridExecDurationCell(1)
                .invoke('text')
                .invoke('trim')
                .then((elText1) => {
                    return dataJobExecutionsPage
                        .getDataGridExecDurationCell(2)
                        .invoke('text')
                        .invoke('trim')
                        .then((elText2) => {
                            return dataJobExecutionsPage.convertStringContentToSeconds(elText1) -
                                dataJobExecutionsPage.convertStringContentToSeconds(elText2);
                        });
                })
                .should('be.lte', 0);

            dataJobExecutionsPage
                .sortByExecDuration();

            dataJobExecutionsPage
                .getDataGridExecDurationHeader()
                .should('exist')
                .invoke('attr', 'aria-sort')
                .should('eq', 'descending');

            dataJobExecutionsPage
                .getDataGridRows()
                .should('have.length.gt', 0);

            dataJobExecutionsPage
                .getDataGridExecDurationCell(1)
                .invoke('text')
                .invoke('trim')
                .then((elText1) => {
                    return dataJobExecutionsPage
                        .getDataGridExecDurationCell(2)
                        .invoke('text')
                        .invoke('trim')
                        .then((elText2) => {
                            return dataJobExecutionsPage.convertStringContentToSeconds(elText1) -
                                dataJobExecutionsPage.convertStringContentToSeconds(elText2);
                        });
                })
                .should('be.gte', 0);
        });

        it('Data Job Manage Executions Page - should verify execution start sort works', () => {
            const dataJobExecutionsPage = DataJobManageExecutionsPage
                .navigateTo(longLivedTestJob.team, longLivedTestJob.job_name);

            dataJobExecutionsPage
                .getDataGridRows()
                .should('have.length.gt', 0);

            dataJobExecutionsPage
                .getDataGridExecStartHeader()
                .should('exist')
                .invoke('attr', 'aria-sort')
                .should('eq', 'descending');

            dataJobExecutionsPage
                .getDataGridExecStartCell(1)
                .invoke('text')
                .invoke('trim')
                .then((elText1) => {
                    return dataJobExecutionsPage
                        .getDataGridExecStartCell(2)
                        .invoke('text')
                        .invoke('trim')
                        .then((elText2) => {
                            return new Date(elText1) - new Date(elText2)
                        });
                })
                .should('be.gte', 0);

            dataJobExecutionsPage
                .sortByExecStart();

            dataJobExecutionsPage
                .getDataGridExecStartHeader()
                .should('exist')
                .invoke('attr', 'aria-sort')
                .should('eq', 'ascending');

            dataJobExecutionsPage
                .getDataGridRows()
                .should('have.length.gt', 0);

            dataJobExecutionsPage
                .getDataGridExecStartCell(1)
                .invoke('text')
                .invoke('trim')
                .then((elText1) => {
                    return dataJobExecutionsPage
                        .getDataGridExecStartCell(2)
                        .invoke('text')
                        .invoke('trim')
                        .then((elText2) => {
                            return new Date(elText1) - new Date(elText2)
                        });
                })
                .should('be.lte', 0);
        });

        it('Data Job Manage Executions Page - should verify execution end sort works', () => {
            const dataJobExecutionsPage = DataJobManageExecutionsPage
                .navigateTo(longLivedTestJob.team, longLivedTestJob.job_name);

            dataJobExecutionsPage
                .getDataGridRows()
                .should('have.length.gt', 0);

            dataJobExecutionsPage
                .getDataGridExecEndHeader()
                .should('exist')
                .invoke('attr', 'aria-sort')
                .should('eq', 'none');

            dataJobExecutionsPage
                .sortByExecEnd();

            dataJobExecutionsPage
                .getDataGridExecEndHeader()
                .should('exist')
                .invoke('attr', 'aria-sort')
                .should('eq', 'ascending');

            dataJobExecutionsPage
                .getDataGridRows()
                .should('have.length.gt', 0);

            dataJobExecutionsPage
                .getDataGridExecEndCell(1)
                .invoke('text')
                .invoke('trim')
                .then((elText1) => {
                    return dataJobExecutionsPage
                        .getDataGridExecEndCell(2)
                        .invoke('text')
                        .invoke('trim')
                        .then((elText2) => {
                            const d1 = elText1
                                ? new Date(elText1)
                                : new Date();
                            const d2 = elText2
                                ? new Date(elText2)
                                : new Date();

                            return d1 - d2
                        });
                })
                .should('be.lte', 0);

            dataJobExecutionsPage
                .sortByExecEnd();

            dataJobExecutionsPage
                .getDataGridExecEndHeader()
                .should('exist')
                .invoke('attr', 'aria-sort')
                .should('eq', 'descending');

            dataJobExecutionsPage
                .getDataGridRows()
                .should('have.length.gt', 0);

            dataJobExecutionsPage
                .getDataGridExecEndCell(1)
                .invoke('text')
                .invoke('trim')
                .then((elText1) => {
                    return dataJobExecutionsPage
                        .getDataGridExecEndCell(2)
                        .invoke('text')
                        .invoke('trim')
                        .then((elText2) => {
                            const d1 = elText1
                                ? new Date(elText1)
                                : new Date();
                            const d2 = elText2
                                ? new Date(elText2)
                                : new Date();

                            return d1 - d2
                        });
                })
                .should('be.gte', 0);
        });
    });
});
