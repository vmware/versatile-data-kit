/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { DataJobsManagePage } from '../../../../support/pages/manage/data-jobs/data-jobs.po';
import { DataJobManageExecutionsPage } from '../../../../support/pages/manage/data-jobs/executions/data-job-executions.po';

describe(
    'Data Job Manage Executions Page',
    { tags: ['@dataPipelines', '@manageDataJobExecutions', '@manage'] },
    () => {
        /**
         * @type {{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}}
         */
        let shortLivedTestJobWithDeployFixture;
        /**
         * @type {{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}}
         */
        let longLivedFailingJobFixture;

        before(() => {
            return DataJobManageExecutionsPage.recordHarIfSupported()
                .then(() =>
                    cy.clearLocalStorageSnapshot('data-job-manage-executions')
                )
                .then(() => DataJobManageExecutionsPage.login())
                .then(() => cy.saveLocalStorage('data-job-manage-executions'))
                .then(() =>
                    DataJobManageExecutionsPage.createLongLivedJobs('failing')
                )
                .then(() =>
                    DataJobManageExecutionsPage.provideExecutionsForLongLivedJobs(
                        'failing'
                    )
                )
                .then(() =>
                    DataJobManageExecutionsPage.loadLongLivedFailingJobFixture().then(
                        (loadedTestJob) => {
                            longLivedFailingJobFixture = loadedTestJob;

                            return cy.wrap({
                                context:
                                    'manage::1::data-job-executions.spec::before()',
                                action: 'continue'
                            });
                        }
                    )
                )
                .then(() =>
                    DataJobManageExecutionsPage.createShortLivedTestJobWithDeploy(
                        'v2'
                    )
                )
                .then(() =>
                    DataJobManageExecutionsPage.provideExecutionsForShortLivedTestJobWithDeploy(
                        'v2'
                    )
                )
                .then(() =>
                    DataJobManageExecutionsPage.loadShortLivedTestJobFixtureWithDeploy(
                        'v2'
                    ).then((loadedTestJob) => {
                        shortLivedTestJobWithDeployFixture = loadedTestJob;

                        return cy.wrap({
                            context:
                                'manage::2::data-job-executions.spec::before()',
                            action: 'continue'
                        });
                    })
                );
        });

        after(() => {
            DataJobManageExecutionsPage.deleteShortLivedTestJobWithDeploy('v2');

            DataJobManageExecutionsPage.saveHarIfSupported();
        });

        beforeEach(() => {
            cy.restoreLocalStorage('data-job-manage-executions');

            DataJobManageExecutionsPage.wireUserSession();
            DataJobManageExecutionsPage.initInterceptors();
        });

        describe('smoke', { tags: ['@smoke'] }, () => {
            it(`should open Details and verify Executions tab is displayed and navigates`, () => {
                cy.log(
                    'Fixture for name: ' + longLivedFailingJobFixture.job_name
                );

                const dataJobsManagePage =
                    DataJobsManagePage.navigateWithSideMenu();

                dataJobsManagePage.chooseQuickFilter(0);

                // filter by job name substring because there are a lot of jobs, and it could potentially be on second/third page
                dataJobsManagePage.filterByJobName(
                    longLivedFailingJobFixture.job_name.substring(0, 20)
                );

                dataJobsManagePage.openJobDetails(
                    longLivedFailingJobFixture.team,
                    longLivedFailingJobFixture.job_name
                );

                const dataJobManageExecutionsPage =
                    DataJobManageExecutionsPage.getPage();

                dataJobManageExecutionsPage
                    .getDetailsTab()
                    .should('exist')
                    .should('have.class', 'active');

                dataJobManageExecutionsPage
                    .getExecutionsTab()
                    .should('exist')
                    .should('not.have.class', 'active');

                dataJobManageExecutionsPage.openExecutionsTab();

                const dataJobExecutionsPage =
                    DataJobManageExecutionsPage.getPage();

                dataJobExecutionsPage
                    .getDetailsTab()
                    .should('exist')
                    .should('not.have.class', 'active');

                dataJobExecutionsPage
                    .getExecutionsTab()
                    .should('exist')
                    .should('have.class', 'active');

                dataJobExecutionsPage.getDataGrid().should('exist');
            });

            it('should verify elements are rendered in DOM', () => {
                const dataJobExecutionsPage =
                    DataJobManageExecutionsPage.navigateTo(
                        longLivedFailingJobFixture.team,
                        longLivedFailingJobFixture.job_name
                    );

                dataJobExecutionsPage
                    .getPageTitle()
                    .scrollIntoView()
                    .should('be.visible')
                    .should(
                        'contains.text',
                        longLivedFailingJobFixture.job_name
                    );

                dataJobExecutionsPage
                    .getDetailsTab()
                    .should('exist')
                    .should('not.have.class', 'active');

                dataJobExecutionsPage
                    .getExecutionsTab()
                    .should('exist')
                    .should('have.class', 'active');

                dataJobExecutionsPage
                    .getExecuteOrCancelButton()
                    .should('exist');

                dataJobExecutionsPage.getActionDropdownBtn().should('exist');

                dataJobExecutionsPage.openActionDropdown();

                dataJobExecutionsPage.getDeleteJobBtn().should('exist');

                dataJobExecutionsPage.clickOnContentContainer();

                dataJobExecutionsPage.waitForSmartDelay();

                dataJobExecutionsPage.getTimePeriod().should('exist');

                dataJobExecutionsPage.getStatusChart().should('exist');

                dataJobExecutionsPage.getDurationChart().should('exist');

                dataJobExecutionsPage.getDataGrid().should('exist');

                dataJobExecutionsPage
                    .getDataGridRows()
                    .should('have.length.gt', 0);
            });

            it('should verify start then cancel execution works', () => {
                const dataJobExecutionsPage =
                    DataJobManageExecutionsPage.navigateTo(
                        shortLivedTestJobWithDeployFixture.team,
                        shortLivedTestJobWithDeployFixture.job_name
                    );

                DataJobManageExecutionsPage.waitForDataJobToNotHaveRunningExecution();

                dataJobExecutionsPage
                    .getExecutionsTab()
                    .should('exist')
                    .should('have.class', 'active');

                // Execute data job and check if the execution status after that is Running or Submitted
                dataJobExecutionsPage.executeNow(true);
                dataJobExecutionsPage
                    .getExecutionStatus()
                    .first()
                    .contains(/Running|Submitted/);

                // Cancel data job execution and check if the status after that is Cancelled
                dataJobExecutionsPage.cancelExecution(true);
                dataJobExecutionsPage
                    .getExecutionStatus()
                    .first()
                    .should('contains.text', 'Canceled');
            });
        });

        describe('extended', () => {
            it('should verify on URL navigate to Executions will open the page', () => {
                const dataJobExecutionsPage =
                    DataJobManageExecutionsPage.navigateTo(
                        longLivedFailingJobFixture.team,
                        longLivedFailingJobFixture.job_name
                    );

                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {}
                    });

                dataJobExecutionsPage
                    .getDetailsTab()
                    .should('exist')
                    .should('not.have.class', 'active');

                dataJobExecutionsPage
                    .getExecutionsTab()
                    .should('exist')
                    .should('have.class', 'active');

                dataJobExecutionsPage.getDataGrid().should('exist');
            });

            it('should verify time period is in correct format', () => {
                const dataJobExecutionsPage =
                    DataJobManageExecutionsPage.navigateTo(
                        longLivedFailingJobFixture.team,
                        longLivedFailingJobFixture.job_name
                    );

                dataJobExecutionsPage
                    .getTimePeriod()
                    .invoke('text')
                    .invoke('trim')
                    .should(
                        'match',
                        new RegExp(
                            `^\\w+\\s\\d+,\\s\\d+,\\s\\d+:\\d+:\\d+\\s(AM|PM)\\sto\\s\\w+\\s\\d+,\\s\\d+,\\s\\d+:\\d+:\\d+\\s(AM|PM)$`
                        )
                    );
            });

            it('should verify refresh button will show spinner and then load data', () => {
                const dataJobExecutionsPage =
                    DataJobManageExecutionsPage.navigateTo(
                        longLivedFailingJobFixture.team,
                        longLivedFailingJobFixture.job_name
                    );

                // verify before
                dataJobExecutionsPage.getDataGrid().should('exist');
                dataJobExecutionsPage
                    .getExecLoadingSpinner()
                    .should('not.exist');
                dataJobExecutionsPage.getDataGridSpinner().should('not.exist');

                // trigger refresh
                dataJobExecutionsPage.waitForActionThinkingTime();
                dataJobExecutionsPage.refreshExecData();

                // verify while refreshing
                dataJobExecutionsPage.getDataGrid().should('exist');
                dataJobExecutionsPage.getExecLoadingSpinner().should('exist');
                dataJobExecutionsPage.getDataGridSpinner().should('exist');

                // wait loading data to finish
                dataJobExecutionsPage.waitForGridDataLoad();

                // verify after refresh
                dataJobExecutionsPage.getDataGrid().should('exist');
                dataJobExecutionsPage
                    .getExecLoadingSpinner()
                    .should('not.exist');
                dataJobExecutionsPage.getDataGridSpinner().should('not.exist');
            });

            describe('DataGrid Filters', () => {
                it('should verify status filter options are rendered', () => {
                    const dataJobExecutionsPage =
                        DataJobManageExecutionsPage.navigateTo(
                            longLivedFailingJobFixture.team,
                            longLivedFailingJobFixture.job_name
                        );

                    // open status filter
                    dataJobExecutionsPage.openStatusFilter();

                    // verify exist
                    dataJobExecutionsPage
                        .getDataGridPopupFilter()
                        .should('exist');
                    dataJobExecutionsPage
                        .getDataGridExecStatusFilters()
                        .then((elements) =>
                            Array.from(elements).map((el) => el.innerText)
                        )
                        .should('deep.equal', [
                            'Success',
                            'Platform Error',
                            'User Error',
                            'Running',
                            'Submitted',
                            'Skipped',
                            'Canceled'
                        ]);

                    // close status filter
                    dataJobExecutionsPage.closeFilter();

                    // verify doesn't exist
                    dataJobExecutionsPage
                        .getDataGridPopupFilter()
                        .should('not.exist');
                });

                it('should verify type filter options are rendered', () => {
                    const dataJobExecutionsPage =
                        DataJobManageExecutionsPage.navigateTo(
                            longLivedFailingJobFixture.team,
                            longLivedFailingJobFixture.job_name
                        );

                    // open type filter
                    dataJobExecutionsPage.openTypeFilter();

                    // verify exist
                    dataJobExecutionsPage
                        .getDataGridPopupFilter()
                        .should('exist');
                    dataJobExecutionsPage
                        .getDataGridExecTypeFilters()
                        .then((elements) =>
                            Array.from(elements).map((el) => el.innerText)
                        )
                        .should('deep.equal', ['Manual', 'Scheduled']);

                    // close type filter
                    dataJobExecutionsPage.closeFilter();

                    // verify doesn't exist
                    dataJobExecutionsPage
                        .getDataGridPopupFilter()
                        .should('not.exist');
                });

                it('should verify id filter render input and filters correctly', () => {
                    const dataJobExecutionsPage =
                        DataJobManageExecutionsPage.navigateTo(
                            longLivedFailingJobFixture.team,
                            longLivedFailingJobFixture.job_name
                        );

                    dataJobExecutionsPage
                        .getDataGridRows()
                        .should('have.length.gt', 0);

                    // open id filter
                    dataJobExecutionsPage.openIDFilter();

                    // verify exist fill with data na verify again
                    dataJobExecutionsPage
                        .getDataGridPopupFilter()
                        .should('exist');
                    dataJobExecutionsPage.typeToFilterInput('xyxyxy');
                    dataJobExecutionsPage
                        .getDataGridRows()
                        .should('have.length', 0);

                    // clear filter and verify
                    dataJobExecutionsPage.clearFilterInput();
                    dataJobExecutionsPage
                        .getDataGridRows()
                        .should('have.length.gt', 0);

                    // close id filter
                    dataJobExecutionsPage.closeFilter();

                    // verify doesn't exist
                    dataJobExecutionsPage
                        .getDataGridPopupFilter()
                        .should('not.exist');
                });

                it('should verify version filter render input and filters correctly', () => {
                    const dataJobExecutionsPage =
                        DataJobManageExecutionsPage.navigateTo(
                            longLivedFailingJobFixture.team,
                            longLivedFailingJobFixture.job_name
                        );

                    dataJobExecutionsPage
                        .getDataGridRows()
                        .should('have.length.gt', 0);

                    // open versino filter
                    dataJobExecutionsPage.openVersionFilter();

                    // verify exist fill with data na verify again
                    dataJobExecutionsPage
                        .getDataGridPopupFilter()
                        .should('exist');
                    dataJobExecutionsPage.typeToFilterInput('xyxyxy');
                    dataJobExecutionsPage
                        .getDataGridRows()
                        .should('have.length', 0);

                    // clear filter and verify
                    dataJobExecutionsPage.clearFilterInput();
                    dataJobExecutionsPage
                        .getDataGridRows()
                        .should('have.length.gt', 0);

                    // close version filter
                    dataJobExecutionsPage.closeFilter();

                    // verify doesn't exist
                    dataJobExecutionsPage
                        .getDataGridPopupFilter()
                        .should('not.exist');
                });
            });

            describe('DataGrid Sort', () => {
                it('should verify duration sort works', () => {
                    const dataJobExecutionsPage =
                        DataJobManageExecutionsPage.navigateTo(
                            longLivedFailingJobFixture.team,
                            longLivedFailingJobFixture.job_name
                        );

                    dataJobExecutionsPage
                        .getDataGridRows()
                        .should('have.length.gt', 0);

                    dataJobExecutionsPage
                        .getDataGridExecDurationHeader()
                        .should('exist')
                        .invoke('attr', 'aria-sort')
                        .should('eq', 'none');

                    dataJobExecutionsPage.sortByExecDuration();

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
                                    return (
                                        dataJobExecutionsPage.convertStringContentToSeconds(
                                            elText1
                                        ) -
                                        dataJobExecutionsPage.convertStringContentToSeconds(
                                            elText2
                                        )
                                    );
                                });
                        })
                        .should('be.lte', 0);

                    dataJobExecutionsPage.sortByExecDuration();

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
                                    return (
                                        dataJobExecutionsPage.convertStringContentToSeconds(
                                            elText1
                                        ) -
                                        dataJobExecutionsPage.convertStringContentToSeconds(
                                            elText2
                                        )
                                    );
                                });
                        })
                        .should('be.gte', 0);
                });

                it('should verify execution start sort works', () => {
                    const dataJobExecutionsPage =
                        DataJobManageExecutionsPage.navigateTo(
                            longLivedFailingJobFixture.team,
                            longLivedFailingJobFixture.job_name
                        );

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
                                    return (
                                        new Date(elText1) - new Date(elText2)
                                    );
                                });
                        })
                        .should('be.gte', 0);

                    dataJobExecutionsPage.sortByExecStart();

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
                                    return (
                                        new Date(elText1) - new Date(elText2)
                                    );
                                });
                        })
                        .should('be.lte', 0);
                });

                it('should verify execution end sort works', () => {
                    const dataJobExecutionsPage =
                        DataJobManageExecutionsPage.navigateTo(
                            longLivedFailingJobFixture.team,
                            longLivedFailingJobFixture.job_name
                        );

                    dataJobExecutionsPage
                        .getDataGridRows()
                        .should('have.length.gt', 0);

                    dataJobExecutionsPage
                        .getDataGridExecEndHeader()
                        .should('exist')
                        .invoke('attr', 'aria-sort')
                        .should('eq', 'none');

                    dataJobExecutionsPage.sortByExecEnd();

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

                                    return d1 - d2;
                                });
                        })
                        .should('be.lte', 0);

                    dataJobExecutionsPage.sortByExecEnd();

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

                                    return d1 - d2;
                                });
                        })
                        .should('be.gte', 0);
                });
            });
        });
    }
);
