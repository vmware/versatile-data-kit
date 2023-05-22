/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { DataJobsManagePage } from '../../../../support/pages/manage/data-jobs/data-jobs.po';
import { DataJobManageExecutionsPage } from '../../../../support/pages/manage/data-jobs/executions/data-job-executions.po';

describe('Data Job Manage Executions Page', { tags: ['@dataPipelines', '@manageDataJobExecutions', '@manage'] }, () => {
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
            .then(() => cy.clearLocalStorageSnapshot('data-job-manage-executions'))
            .then(() => DataJobManageExecutionsPage.login())
            .then(() => cy.saveLocalStorage('data-job-manage-executions'))
            .then(() => DataJobManageExecutionsPage.createLongLivedJobs('failing'))
            .then(() => DataJobManageExecutionsPage.provideExecutionsForLongLivedJobs('failing'))
            .then(() =>
                DataJobManageExecutionsPage.loadLongLivedFailingJobFixture().then((loadedTestJob) => {
                    longLivedFailingJobFixture = loadedTestJob;

                    return cy.wrap({
                        context: 'manage::1::data-job-executions.spec::before()',
                        action: 'continue'
                    });
                })
            )
            .then(() => DataJobManageExecutionsPage.createShortLivedTestJobWithDeploy('v2'))
            .then(() => DataJobManageExecutionsPage.provideExecutionsForShortLivedTestJobWithDeploy('v2'))
            .then(() =>
                DataJobManageExecutionsPage.loadShortLivedTestJobFixtureWithDeploy('v2').then((loadedTestJob) => {
                    shortLivedTestJobWithDeployFixture = loadedTestJob;

                    return cy.wrap({
                        context: 'manage::2::data-job-executions.spec::before()',
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
            cy.log('Fixture for name: ' + longLivedFailingJobFixture.job_name);

            const dataJobsManagePage = DataJobsManagePage.navigateWithSideMenu();

            dataJobsManagePage.chooseQuickFilter(0);

            // filter by job name substring because there are a lot of jobs, and it could potentially be on second/third page
            dataJobsManagePage.filterByJobName(longLivedFailingJobFixture.job_name.substring(0, 20));

            dataJobsManagePage.openJobDetails(longLivedFailingJobFixture.team, longLivedFailingJobFixture.job_name);

            const dataJobManageExecutionsPage = DataJobManageExecutionsPage.getPage();

            dataJobManageExecutionsPage.getDetailsTab().should('exist').should('have.class', 'active');

            dataJobManageExecutionsPage.getExecutionsTab().should('exist').should('not.have.class', 'active');

            dataJobManageExecutionsPage.openExecutionsTab();

            const dataJobExecutionsPage = DataJobManageExecutionsPage.getPage();

            dataJobExecutionsPage.getDetailsTab().should('exist').should('not.have.class', 'active');

            dataJobExecutionsPage.getExecutionsTab().should('exist').should('have.class', 'active');

            dataJobExecutionsPage.getDataGrid().should('exist');
        });

        it('should verify elements are rendered in DOM', () => {
            const dataJobExecutionsPage = DataJobManageExecutionsPage.navigateTo(longLivedFailingJobFixture.team, longLivedFailingJobFixture.job_name);

            dataJobExecutionsPage.getPageTitle().scrollIntoView().should('be.visible').should('contains.text', longLivedFailingJobFixture.job_name);

            dataJobExecutionsPage.getDetailsTab().should('exist').should('not.have.class', 'active');

            dataJobExecutionsPage.getExecutionsTab().should('exist').should('have.class', 'active');

            dataJobExecutionsPage.getExecuteOrCancelButton().should('exist');

            dataJobExecutionsPage.getActionDropdownBtn().should('exist');

            dataJobExecutionsPage.openActionDropdown();

            dataJobExecutionsPage.getDeleteJobBtn().should('exist');

            dataJobExecutionsPage.clickOnContentContainer();

            dataJobExecutionsPage.waitForSmartDelay();

            dataJobExecutionsPage.getTimePeriod().should('exist');

            dataJobExecutionsPage.getStatusChart().should('exist');

            dataJobExecutionsPage.getDurationChart().should('exist');

            dataJobExecutionsPage.getDataGrid().should('exist');

            dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);
        });

        it('should verify start then cancel execution works', () => {
            const dataJobExecutionsPage = DataJobManageExecutionsPage.navigateTo(shortLivedTestJobWithDeployFixture.team, shortLivedTestJobWithDeployFixture.job_name);

            DataJobManageExecutionsPage.waitForDataJobToNotHaveRunningExecution();

            dataJobExecutionsPage.getExecutionsTab().should('exist').should('have.class', 'active');

            // Execute data job and check if the execution status after that is Running or Submitted
            dataJobExecutionsPage.executeNow(true);
            dataJobExecutionsPage
                .getExecutionStatus()
                .first()
                .contains(/Running|Submitted/);

            // Cancel data job execution and check if the status after that is Cancelled
            dataJobExecutionsPage.cancelExecution(true);
            dataJobExecutionsPage.getExecutionStatus().first().should('contains.text', 'Canceled');
        });
    });

    describe('extended', () => {
        it('should verify on URL navigate to Executions will open the page', () => {
            const dataJobExecutionsPage = DataJobManageExecutionsPage.navigateTo(longLivedFailingJobFixture.team, longLivedFailingJobFixture.job_name);

            dataJobExecutionsPage
                .getCurrentUrlNormalized({
                    includePathSegment: true,
                    includeQueryString: true,
                    decodeQueryString: true
                })
                .should('deep.equal', {
                    pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                    queryParams: {
                        sort: '{"startTime":-1}'
                    }
                });

            dataJobExecutionsPage.getDetailsTab().should('exist').should('not.have.class', 'active');

            dataJobExecutionsPage.getExecutionsTab().should('exist').should('have.class', 'active');

            dataJobExecutionsPage.getDataGrid().should('exist');
        });

        it('should verify time period is in correct format', () => {
            const dataJobExecutionsPage = DataJobManageExecutionsPage.navigateTo(longLivedFailingJobFixture.team, longLivedFailingJobFixture.job_name);

            dataJobExecutionsPage.getTimePeriod().invoke('text').invoke('trim').should('match', new RegExp(`^\\w+\\s\\d+,\\s\\d+,\\s\\d+:\\d+:\\d+\\s(AM|PM)\\sto\\s\\w+\\s\\d+,\\s\\d+,\\s\\d+:\\d+:\\d+\\s(AM|PM)$`));
        });

        it('should verify refresh button will show spinner and then load data', () => {
            const dataJobExecutionsPage = DataJobManageExecutionsPage.navigateTo(longLivedFailingJobFixture.team, longLivedFailingJobFixture.job_name);

            // verify before
            dataJobExecutionsPage.getDataGrid().should('exist');
            dataJobExecutionsPage.getExecLoadingSpinner().should('not.exist');
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
            dataJobExecutionsPage.getExecLoadingSpinner().should('not.exist');
            dataJobExecutionsPage.getDataGridSpinner().should('not.exist');
        });

        describe('DataGrid Filters', () => {
            it('should verify status filter options are rendered and behaves correctly', () => {
                const dataJobExecutionsPage = DataJobManageExecutionsPage.navigateTo(longLivedFailingJobFixture.team, longLivedFailingJobFixture.job_name);

                // open status filter
                dataJobExecutionsPage.openStatusFilter();

                // verify exist
                dataJobExecutionsPage.getDataGridPopupFilter().should('exist');
                dataJobExecutionsPage
                    .getDataGridExecStatusFilters()
                    .then((elements) => Array.from(elements).map((el) => el.innerText))
                    .should('deep.equal', ['Success', 'Platform Error', 'User Error', 'Running', 'Submitted', 'Skipped', 'Canceled']);

                // close status filter
                dataJobExecutionsPage.closeFilter();

                // verify doesn't exist
                dataJobExecutionsPage.getDataGridPopupFilter().should('not.exist');

                // verify current URL has appended default sort by startTime descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}'
                        }
                    });

                // open status filter and select all available values and close the filter
                dataJobExecutionsPage.openStatusFilter();
                dataJobExecutionsPage.filterByStatus('user_error');
                dataJobExecutionsPage.filterByStatus('platform_error');
                dataJobExecutionsPage.filterByStatus('succeeded');
                dataJobExecutionsPage.filterByStatus('running');
                dataJobExecutionsPage.filterByStatus('skipped');
                dataJobExecutionsPage.filterByStatus('submitted');
                dataJobExecutionsPage.filterByStatus('cancelled');
                dataJobExecutionsPage.closeFilter();

                // verify current URL has appended all execution statuses and sort by status ascending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}',
                            filter: '{"status":"user_error,platform_error,succeeded,running,skipped,submitted,cancelled"}'
                        }
                    });

                // open status filter and unselect statuses: platform_error, skipped, submitted, cancelled and close the filter
                dataJobExecutionsPage.openStatusFilter();
                dataJobExecutionsPage.clearFilterByStatus('platform_error');
                dataJobExecutionsPage.clearFilterByStatus('skipped');
                dataJobExecutionsPage.clearFilterByStatus('submitted');
                dataJobExecutionsPage.clearFilterByStatus('cancelled');
                dataJobExecutionsPage.closeFilter();

                // verify current URL has appended execution statuses user_error, succeeded, running and sort by status ascending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}',
                            filter: '{"status":"user_error,succeeded,running"}'
                        }
                    });

                // open status filter and unselect left statuses and close the filter
                dataJobExecutionsPage.openStatusFilter();
                dataJobExecutionsPage.clearFilterByStatus('user_error');
                dataJobExecutionsPage.clearFilterByStatus('succeeded');
                dataJobExecutionsPage.clearFilterByStatus('running');
                dataJobExecutionsPage.closeFilter();

                // verify current URL has appended only sort by status descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}'
                        }
                    });
            });

            it('should verify type filter options are rendered and behaves correctly', () => {
                const dataJobExecutionsPage = DataJobManageExecutionsPage.navigateTo(longLivedFailingJobFixture.team, longLivedFailingJobFixture.job_name);

                // open type filter
                dataJobExecutionsPage.openTypeFilter();

                // verify exist
                dataJobExecutionsPage.getDataGridPopupFilter().should('exist');
                dataJobExecutionsPage.getDataGridExecTypeFilterLabel('manual').should('exist').should('have.text', 'Manual');
                dataJobExecutionsPage.getDataGridExecTypeFilterLabel('scheduled').should('exist').should('have.text', 'Scheduled');

                // close type filter
                dataJobExecutionsPage.closeFilter();

                // verify doesn't exist
                dataJobExecutionsPage.getDataGridPopupFilter().should('not.exist');

                // verify current URL has appended default sort by startTime descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}'
                        }
                    });

                // open type filter and select manual execution trigger and close
                dataJobExecutionsPage.openTypeFilter();
                dataJobExecutionsPage.filterByType('manual');
                dataJobExecutionsPage.closeFilter();

                // verify cell elements
                dataJobExecutionsPage.getDataGridExecTypeContainers('scheduled').should('have.length', 0);

                // verify current URL has appended manual execution trigger and sort by type ascending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}',
                            filter: '{"type":"manual"}'
                        }
                    });

                // open type filter and select scheduled execution trigger and close
                dataJobExecutionsPage.openTypeFilter();
                dataJobExecutionsPage.filterByType('scheduled');
                dataJobExecutionsPage.closeFilter();

                // verify cell elements
                dataJobExecutionsPage.getDataGridExecTypeContainers('manual').should('have.length', 0);

                // verify current URL has appended manual and scheduled execution trigger and sort by type ascending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}',
                            filter: '{"type":"manual,scheduled"}'
                        }
                    });

                // open type filter and unselect scheduled and manual execution triggers and close filter
                dataJobExecutionsPage.openTypeFilter();
                dataJobExecutionsPage.clearFilterByType('scheduled');
                dataJobExecutionsPage.clearFilterByType('manual');
                dataJobExecutionsPage.closeFilter();

                // verify cell elements
                dataJobExecutionsPage.getDataGridExecTypeContainers('manual').should('have.length.gte', 0);
                dataJobExecutionsPage.getDataGridExecTypeContainers('scheduled').should('have.length.gte', 0);

                // verify current URL has appended only sort by type descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}'
                        }
                    });
            });

            it('should verify duration filter render input and filters correctly', () => {
                const dataJobExecutionsPage = DataJobManageExecutionsPage.navigateTo(longLivedFailingJobFixture.team, longLivedFailingJobFixture.job_name);

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                // verify current URL has appended default sort by startTime descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}'
                        }
                    });

                // open duration filter
                dataJobExecutionsPage.openDurationFilter();

                // verify exist fill with data na verify again
                dataJobExecutionsPage.getDataGridPopupFilter().should('exist');
                dataJobExecutionsPage.typeToTextFilterInput('100s');
                dataJobExecutionsPage.getDataGridRows().should('have.length', 0);

                // verify current URL has appended default sort by startTime descending and new value for id xyxyxy
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}',
                            filter: '{"duration":"100s"}'
                        }
                    });

                // clear filter and verify
                dataJobExecutionsPage.clearTextFilterInput();
                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                // close id filter
                dataJobExecutionsPage.closeFilter();

                // verify doesn't exist
                dataJobExecutionsPage.getDataGridPopupFilter().should('not.exist');

                // verify current URL has appended default sort by startTime descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}'
                        }
                    });
            });

            it('should verify execution start time filter render input and filters correctly', () => {
                const dataJobExecutionsPage = DataJobManageExecutionsPage.navigateTo(longLivedFailingJobFixture.team, longLivedFailingJobFixture.job_name);

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                // verify current URL has appended default sort by startTime descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}'
                        }
                    });

                // open exec start time filter
                dataJobExecutionsPage.openExecStartFilter();

                // verify exist fill with data na verify again
                dataJobExecutionsPage.getDataGridPopupFilter().should('exist');
                dataJobExecutionsPage.generateExecStartFilterValue().then((filterValue) => {
                    // type generated filter value
                    dataJobExecutionsPage.typeToTextFilterInput(filterValue);

                    // verify only cells that match the value are rendered
                    dataJobExecutionsPage
                        .getDataGridExecStartCells()
                        .then(($cells) => {
                            const foundCells = Array.from($cells).map((cell) => new RegExp(`${filterValue}$`).test(`${cell.innerText?.trim()}`));

                            return foundCells.length;
                        })
                        .should('gt', 0);

                    // verify current URL has appended default sort by startTime descending and new value for startTime ${filterValue}
                    dataJobExecutionsPage
                        .getCurrentUrlNormalized({
                            includePathSegment: true,
                            includeQueryString: true,
                            decodeQueryString: true
                        })
                        .should('deep.equal', {
                            pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                            queryParams: {
                                sort: '{"startTime":-1}',
                                filter: `{"startTimeFormatted":"${filterValue}"}`
                            }
                        });
                });

                // clear filter and verify
                dataJobExecutionsPage.clearTextFilterInput();
                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                // close start time filter
                dataJobExecutionsPage.closeFilter();

                // verify doesn't exist
                dataJobExecutionsPage.getDataGridPopupFilter().should('not.exist');

                // verify current URL has appended default sort by startTime descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}'
                        }
                    });
            });

            it('should verify execution end time filter render input and filters correctly', () => {
                const dataJobExecutionsPage = DataJobManageExecutionsPage.navigateTo(longLivedFailingJobFixture.team, longLivedFailingJobFixture.job_name);

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                // verify current URL has appended default sort by startTime descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}'
                        }
                    });

                // open exec end time filter
                dataJobExecutionsPage.openExecEndFilter();

                // verify exist fill with data na verify again
                dataJobExecutionsPage.getDataGridPopupFilter().should('exist');
                dataJobExecutionsPage.generateExecEndFilterValue().then((filterValue) => {
                    // type generated filter value
                    dataJobExecutionsPage.typeToTextFilterInput(filterValue);

                    // verify only cells that match the value are rendered
                    dataJobExecutionsPage
                        .getDataGridExecEndCells()
                        .then(($cells) => {
                            const foundCells = Array.from($cells).map((cell) => new RegExp(`${filterValue}$`).test(`${cell.innerText?.trim()}`));

                            return foundCells.length;
                        })
                        .should('gt', 0);

                    // verify current URL has appended default sort by startTime descending and new value for endTime ${filterValue}
                    dataJobExecutionsPage
                        .getCurrentUrlNormalized({
                            includePathSegment: true,
                            includeQueryString: true,
                            decodeQueryString: true
                        })
                        .should('deep.equal', {
                            pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                            queryParams: {
                                sort: '{"startTime":-1}',
                                filter: `{"endTimeFormatted":"${filterValue}"}`
                            }
                        });
                });

                // clear filter and verify
                dataJobExecutionsPage.clearTextFilterInput();
                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                // close start time filter
                dataJobExecutionsPage.closeFilter();

                // verify doesn't exist
                dataJobExecutionsPage.getDataGridPopupFilter().should('not.exist');

                // verify current URL has appended default sort by startTime descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}'
                        }
                    });
            });

            it('should verify execution id filter render input and filters correctly', () => {
                const dataJobExecutionsPage = DataJobManageExecutionsPage.navigateTo(longLivedFailingJobFixture.team, longLivedFailingJobFixture.job_name);

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                // verify current URL has appended default sort by startTime descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}'
                        }
                    });

                // open exec ID filter
                dataJobExecutionsPage.openIDFilter();

                // verify exist fill with data na verify again
                dataJobExecutionsPage.getDataGridPopupFilter().should('exist');
                // type job name as filter value
                dataJobExecutionsPage.typeToTextFilterInput(longLivedFailingJobFixture.job_name);

                // verify only cells that match the value are rendered
                dataJobExecutionsPage
                    .getDataGridExecIDCells()
                    .then(($cells) => {
                        const foundCells = Array.from($cells).map((cell) => new RegExp(`^${longLivedFailingJobFixture.job_name}-\d+$`).test(`${cell.innerText?.trim()}`));

                        return foundCells.length;
                    })
                    .should('gt', 0);

                // verify current URL has appended default sort by startTime descending and new value for endTime ${filterValue}
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}',
                            filter: `{"id":"${longLivedFailingJobFixture.job_name}"}`
                        }
                    });

                // clear filter and type random text then verify
                dataJobExecutionsPage.clearTextFilterInput();
                dataJobExecutionsPage.typeToTextFilterInput('xyxyxy');
                dataJobExecutionsPage.getDataGridRows().should('have.length', 0);

                // verify current URL has appended default sort by startTime descending and new value for id xyxyxy
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}',
                            filter: '{"id":"xyxyxy"}'
                        }
                    });

                // clear filter and verify
                dataJobExecutionsPage.clearTextFilterInput();
                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                // close start time filter
                dataJobExecutionsPage.closeFilter();

                // verify doesn't exist
                dataJobExecutionsPage.getDataGridPopupFilter().should('not.exist');

                // verify current URL has appended default sort by startTime descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}'
                        }
                    });
            });

            it('should verify version filter render input and filters correctly', () => {
                const dataJobExecutionsPage = DataJobManageExecutionsPage.navigateTo(longLivedFailingJobFixture.team, longLivedFailingJobFixture.job_name);

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                // verify current URL has appended default sort by startTime descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}'
                        }
                    });

                // open version filter
                dataJobExecutionsPage.openVersionFilter();

                // verify exist fill with data na verify again
                dataJobExecutionsPage.getDataGridPopupFilter().should('exist');
                dataJobExecutionsPage.typeToTextFilterInput('xyxyxy');
                dataJobExecutionsPage.getDataGridRows().should('have.length', 0);

                // verify current URL has appended default sort by startTime descending and new value for jobVersion xyxyxy
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}',
                            filter: '{"jobVersion":"xyxyxy"}'
                        }
                    });

                // clear filter and verify
                dataJobExecutionsPage.clearTextFilterInput();
                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                // close version filter
                dataJobExecutionsPage.closeFilter();

                // verify doesn't exist
                dataJobExecutionsPage.getDataGridPopupFilter().should('not.exist');

                // verify current URL has appended default sort by startTime descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}'
                        }
                    });
            });
        });

        describe('DataGrid Sort', () => {
            it('should verify status sort behaves correctly', () => {
                const dataJobExecutionsPage = DataJobManageExecutionsPage.navigateTo(longLivedFailingJobFixture.team, longLivedFailingJobFixture.job_name);

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                dataJobExecutionsPage.getDataGridExecStatusHeader().should('exist').invoke('attr', 'aria-sort').should('eq', 'none');

                // verify current URL has appended default sort by startTime descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}'
                        }
                    });

                // sort by status ascending
                dataJobExecutionsPage.sortByExecStatus();

                // verify sort by status is ascending
                dataJobExecutionsPage.getDataGridExecStatusHeader().should('exist').invoke('attr', 'aria-sort').should('eq', 'ascending');

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                // verify current URL has appended sort by status ascending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"status":1}'
                        }
                    });

                // sort by status descending
                dataJobExecutionsPage.sortByExecStatus();

                // verify sort by status is descending
                dataJobExecutionsPage.getDataGridExecStatusHeader().should('exist').invoke('attr', 'aria-sort').should('eq', 'descending');

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                // verify current URL has appended sort by status descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"status":-1}'
                        }
                    });
            });

            it('should verify type sort behaves correctly', () => {
                const dataJobExecutionsPage = DataJobManageExecutionsPage.navigateTo(longLivedFailingJobFixture.team, longLivedFailingJobFixture.job_name);

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                dataJobExecutionsPage.getDataGridExecTypeHeader().should('exist').invoke('attr', 'aria-sort').should('eq', 'none');

                // verify current URL has appended default sort by startTime descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}'
                        }
                    });

                // sort by type ascending
                dataJobExecutionsPage.sortByExecType();

                // verify sort is ascending
                dataJobExecutionsPage.getDataGridExecTypeHeader().should('exist').invoke('attr', 'aria-sort').should('eq', 'ascending');

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                // verify current URL has appended sort by type ascending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"type":1}'
                        }
                    });

                // sort by type descending
                dataJobExecutionsPage.sortByExecType();

                // verify sort is descending
                dataJobExecutionsPage.getDataGridExecTypeHeader().should('exist').invoke('attr', 'aria-sort').should('eq', 'descending');

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                // verify current URL has appended sort by type descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"type":-1}'
                        }
                    });
            });

            it('should verify duration sort works', () => {
                const dataJobExecutionsPage = DataJobManageExecutionsPage.navigateTo(longLivedFailingJobFixture.team, longLivedFailingJobFixture.job_name);

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                dataJobExecutionsPage.getDataGridExecDurationHeader().should('exist').invoke('attr', 'aria-sort').should('eq', 'none');

                // verify current URL has appended default sort by startTime descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}'
                        }
                    });

                // sort by duration ascending
                dataJobExecutionsPage.sortByExecDuration();

                dataJobExecutionsPage.getDataGridExecDurationHeader().should('exist').invoke('attr', 'aria-sort').should('eq', 'ascending');

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

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
                                return dataJobExecutionsPage.convertStringContentToSeconds(elText1) - dataJobExecutionsPage.convertStringContentToSeconds(elText2);
                            });
                    })
                    .should('be.lte', 0);

                // verify current URL has appended sort by duration ascending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"duration":1}'
                        }
                    });

                // sort by duration descending
                dataJobExecutionsPage.sortByExecDuration();

                dataJobExecutionsPage.getDataGridExecDurationHeader().should('exist').invoke('attr', 'aria-sort').should('eq', 'descending');

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

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
                                return dataJobExecutionsPage.convertStringContentToSeconds(elText1) - dataJobExecutionsPage.convertStringContentToSeconds(elText2);
                            });
                    })
                    .should('be.gte', 0);

                // verify current URL has appended sort by duration descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"duration":-1}'
                        }
                    });
            });

            it('should verify execution start time sort works', () => {
                const dataJobExecutionsPage = DataJobManageExecutionsPage.navigateTo(longLivedFailingJobFixture.team, longLivedFailingJobFixture.job_name);

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                dataJobExecutionsPage.getDataGridExecStartHeader().should('exist').invoke('attr', 'aria-sort').should('eq', 'descending');

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
                                return new Date(elText1) - new Date(elText2);
                            });
                    })
                    .should('be.gte', 0);

                // verify current URL has appended default sort by startTime descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}'
                        }
                    });

                // sort by exec start ascending
                dataJobExecutionsPage.sortByExecStart();

                dataJobExecutionsPage.getDataGridExecStartHeader().should('exist').invoke('attr', 'aria-sort').should('eq', 'ascending');

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

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
                                return new Date(elText1) - new Date(elText2);
                            });
                    })
                    .should('be.lte', 0);

                // verify current URL has appended sort by duration ascending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":1}'
                        }
                    });
            });

            it('should verify execution end time sort works', () => {
                const dataJobExecutionsPage = DataJobManageExecutionsPage.navigateTo(longLivedFailingJobFixture.team, longLivedFailingJobFixture.job_name);

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                dataJobExecutionsPage.getDataGridExecEndHeader().should('exist').invoke('attr', 'aria-sort').should('eq', 'none');

                // verify current URL has appended default sort by startTime descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}'
                        }
                    });

                // sort by exec end ascending
                dataJobExecutionsPage.sortByExecEnd();

                dataJobExecutionsPage.getDataGridExecEndHeader().should('exist').invoke('attr', 'aria-sort').should('eq', 'ascending');

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

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
                                const d1 = elText1 ? new Date(elText1) : new Date();
                                const d2 = elText2 ? new Date(elText2) : new Date();

                                return d1 - d2;
                            });
                    })
                    .should('be.lte', 0);

                // verify current URL has appended sort by endTime ascending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"endTime":1}'
                        }
                    });

                // sort by exec end time descending
                dataJobExecutionsPage.sortByExecEnd();

                dataJobExecutionsPage.getDataGridExecEndHeader().should('exist').invoke('attr', 'aria-sort').should('eq', 'descending');

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

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
                                const d1 = elText1 ? new Date(elText1) : new Date();
                                const d2 = elText2 ? new Date(elText2) : new Date();

                                return d1 - d2;
                            });
                    })
                    .should('be.gte', 0);

                // verify current URL has appended sort by endTime descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"endTime":-1}'
                        }
                    });
            });

            it('should verify execution ID sort works', () => {
                const dataJobExecutionsPage = DataJobManageExecutionsPage.navigateTo(longLivedFailingJobFixture.team, longLivedFailingJobFixture.job_name);

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                dataJobExecutionsPage.getDataGridExecIDHeader().should('exist').invoke('attr', 'aria-sort').should('eq', 'none');

                // verify current URL has appended default sort by startTime descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}'
                        }
                    });

                // sort by ID ascending
                dataJobExecutionsPage.sortByExecID();

                dataJobExecutionsPage.getDataGridExecIDHeader().should('exist').invoke('attr', 'aria-sort').should('eq', 'ascending');

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                dataJobExecutionsPage
                    .getDataGridExecIDCell(1)
                    .invoke('text')
                    .invoke('trim')
                    .then((elText1) => {
                        return dataJobExecutionsPage
                            .getDataGridExecIDCell(2)
                            .invoke('text')
                            .invoke('trim')
                            .then((elText2) => {
                                return elText2 > elText1;
                            });
                    })
                    .should('be.true');

                // verify current URL has appended sort by id ascending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"id":1}'
                        }
                    });

                // sort by ID descending
                dataJobExecutionsPage.sortByExecID();

                dataJobExecutionsPage.getDataGridExecIDHeader().should('exist').invoke('attr', 'aria-sort').should('eq', 'descending');

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                dataJobExecutionsPage
                    .getDataGridExecIDCell(1)
                    .invoke('text')
                    .invoke('trim')
                    .then((elText1) => {
                        return dataJobExecutionsPage
                            .getDataGridExecIDCell(2)
                            .invoke('text')
                            .invoke('trim')
                            .then((elText2) => {
                                return elText1 > elText2;
                            });
                    })
                    .should('be.true');

                // verify current URL has appended sort by id descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"id":-1}'
                        }
                    });
            });

            it('should verify execution version sort works', () => {
                const dataJobExecutionsPage = DataJobManageExecutionsPage.navigateTo(longLivedFailingJobFixture.team, longLivedFailingJobFixture.job_name);

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                dataJobExecutionsPage.getDataGridExecVersionHeader().should('exist').invoke('attr', 'aria-sort').should('eq', 'none');

                // verify current URL has appended default sort by startTime descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}'
                        }
                    });

                // sort by version ascending
                dataJobExecutionsPage.sortByExecVersion();

                dataJobExecutionsPage.getDataGridExecVersionHeader().should('exist').invoke('attr', 'aria-sort').should('eq', 'ascending');

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                dataJobExecutionsPage
                    .getDataGridExecVersionCell(1)
                    .invoke('text')
                    .invoke('trim')
                    .then((elText1) => {
                        return dataJobExecutionsPage
                            .getDataGridExecVersionCell(2)
                            .invoke('text')
                            .invoke('trim')
                            .then((elText2) => {
                                return elText2 >= elText1;
                            });
                    })
                    .should('be.true');

                // verify current URL has appended sort by job version ascending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"jobVersion":1}'
                        }
                    });

                // sort by version descending
                dataJobExecutionsPage.sortByExecVersion();

                dataJobExecutionsPage.getDataGridExecVersionHeader().should('exist').invoke('attr', 'aria-sort').should('eq', 'descending');

                dataJobExecutionsPage.getDataGridRows().should('have.length.gt', 0);

                dataJobExecutionsPage
                    .getDataGridExecVersionCell(1)
                    .invoke('text')
                    .invoke('trim')
                    .then((elText1) => {
                        return dataJobExecutionsPage
                            .getDataGridExecVersionCell(2)
                            .invoke('text')
                            .invoke('trim')
                            .then((elText2) => {
                                return elText1 >= elText2;
                            });
                    })
                    .should('be.true');

                // verify current URL has appended sort by job version descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"jobVersion":-1}'
                        }
                    });
            });
        });

        // !!! important tests order is very important, because generated url from 1st test is used in the second
        describe('DataGrid Filters and Sort to URL', () => {
            // value is assigned at the end of the 1st test and used in the 2nd test
            let navigationUrlWithFiltersAndSort = '';

            it('should verify multiple filters and sort are appended to URL', () => {
                const dataJobExecutionsPage = DataJobManageExecutionsPage.navigateTo(longLivedFailingJobFixture.team, longLivedFailingJobFixture.job_name);

                // verify current URL has appended default sort by startTime descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}'
                        }
                    });

                // open status filter and select user_error and close the filter
                dataJobExecutionsPage.openStatusFilter();
                dataJobExecutionsPage.filterByStatus('user_error');
                dataJobExecutionsPage.closeFilter();

                // verify current URL has appended filters execution status: user_error and sort by startTime descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}',
                            filter: '{"status":"user_error"}'
                        }
                    });

                // open type filter and select manual execution trigger and close
                dataJobExecutionsPage.openTypeFilter();
                dataJobExecutionsPage.filterByType('manual');
                dataJobExecutionsPage.getDataGridExecTypeContainers('scheduled').should('have.length', 0);
                dataJobExecutionsPage.closeFilter();

                // verify current URL has appended filters execution status: user_error, trigger type: manual, and sort by startTime descending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"startTime":-1}',
                            filter: '{"status":"user_error","type":"manual"}'
                        }
                    });

                // sort by exec ID ascending
                dataJobExecutionsPage.sortByExecID();

                // open exec ID filter
                dataJobExecutionsPage.openIDFilter();
                // type job name as filter value
                dataJobExecutionsPage.typeToTextFilterInput(longLivedFailingJobFixture.job_name);
                // verify only cells that match the value are rendered
                dataJobExecutionsPage
                    .getDataGridExecIDCells()
                    .then(($cells) => {
                        const foundCells = Array.from($cells).map((cell) => new RegExp(`^${longLivedFailingJobFixture.job_name}-\d+$`).test(`${cell.innerText?.trim()}`));

                        return foundCells.length;
                    })
                    .should('gt', 0);
                // verify current URL has appended filters execution status: user_error, trigger type: manual, id: long_lived_job_name and sort by id ascending
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .should('deep.equal', {
                        pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                        queryParams: {
                            sort: '{"id":1}',
                            filter: `{"status":"user_error","type":"manual","id":"${longLivedFailingJobFixture.job_name}"}`
                        }
                    });

                // open exec start time filter and type generated filterValue and close
                dataJobExecutionsPage.openExecStartFilter();
                dataJobExecutionsPage.generateExecStartFilterValue().then((filterValue) => {
                    // type generated filter value
                    dataJobExecutionsPage.typeToTextFilterInput(filterValue);

                    // verify only cells that match the value are rendered
                    dataJobExecutionsPage
                        .getDataGridExecStartCells()
                        .then(($cells) => {
                            const foundCells = Array.from($cells).map((cell) => new RegExp(`${filterValue}$`).test(`${cell.innerText?.trim()}`));

                            return foundCells.length;
                        })
                        .should('gt', 0);

                    // verify current URL has appended filters execution status: user_error, trigger type: manual, id: long_lived_job_name, startTimeFormatted: ${filterValue} and sort by id ascending
                    dataJobExecutionsPage
                        .getCurrentUrlNormalized({
                            includePathSegment: true,
                            includeQueryString: true,
                            decodeQueryString: true
                        })
                        .should('deep.equal', {
                            pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                            queryParams: {
                                sort: '{"id":1}',
                                filter: `{"status":"user_error","type":"manual","id":"${longLivedFailingJobFixture.job_name}","startTimeFormatted":"${filterValue}"}`
                            }
                        });
                });
                dataJobExecutionsPage.closeFilter();

                // open exec end time filter and type generated filterValue and close
                dataJobExecutionsPage.openExecEndFilter();
                dataJobExecutionsPage.generateExecEndFilterValue().then((filterValue) => {
                    // type generated filter value
                    dataJobExecutionsPage.typeToTextFilterInput(filterValue);

                    // verify only cells that match the value are rendered
                    dataJobExecutionsPage
                        .getDataGridExecEndCells()
                        .then(($cells) => {
                            const foundCells = Array.from($cells).map((cell) => new RegExp(`${filterValue}$`).test(`${cell.innerText?.trim()}`));

                            return foundCells.length;
                        })
                        .should('gt', 0);

                    // verify current URL has appended filters execution status: user_error, trigger type: manual, id: long_lived_job_name, startTimeFormatted: ${filterValue}, endTimeFormatted: ${filterValue} and sort by id ascending
                    dataJobExecutionsPage
                        .getCurrentUrlNormalized({
                            includePathSegment: true,
                            includeQueryString: true,
                            decodeQueryString: true
                        })
                        .should('deep.equal', {
                            pathSegment: `/manage/data-jobs/${longLivedFailingJobFixture.team}/${longLivedFailingJobFixture.job_name}/executions`,
                            queryParams: {
                                sort: '{"id":1}',
                                filter: `{"status":"user_error","type":"manual","id":"${longLivedFailingJobFixture.job_name}","startTimeFormatted":"${filterValue}","endTimeFormatted":"${filterValue}"}`
                            }
                        });
                });
                dataJobExecutionsPage.closeFilter();

                // extract current url for next test
                dataJobExecutionsPage
                    .getCurrentUrlNormalized({
                        includePathSegment: true,
                        includeQueryString: true,
                        decodeQueryString: true
                    })
                    .then((urlNormalized) => {
                        const pathSegment = urlNormalized.pathSegment;
                        const queryParamsSerialized = Object.entries(urlNormalized.queryParams)
                            .map((keyValuePair) => keyValuePair.join('='))
                            .join('&');
                        navigationUrlWithFiltersAndSort = `${pathSegment}?${queryParamsSerialized}`;

                        cy.log(navigationUrlWithFiltersAndSort);
                        console.log(navigationUrlWithFiltersAndSort);
                    });
            });

            it('should verify URL navigation with filters and sort will prefill everything and filter accordingly', () => {
                const dataJobExecutionsPage = DataJobManageExecutionsPage.navigateToExecutionsWithUrl(navigationUrlWithFiltersAndSort);

                // open status filter, verify then close
                dataJobExecutionsPage.openStatusFilter();
                dataJobExecutionsPage.getDataGridExecStatusFilterCheckboxesStatuses().should('deep.equal', [
                    ['succeeded', false],
                    ['platform_error', false],
                    ['user_error', true],
                    ['running', false],
                    ['submitted', false],
                    ['skipped', false],
                    ['cancelled', false]
                ]);
                dataJobExecutionsPage.closeFilter();

                // open type filter, verify then close
                dataJobExecutionsPage.openTypeFilter();
                dataJobExecutionsPage.getDataGridExecTypeFilterCheckboxesStatuses().should('deep.equal', [
                    ['manual', true],
                    ['scheduled', false]
                ]);
                dataJobExecutionsPage.getDataGridExecTypeContainers('scheduled').should('have.length', 0);
                dataJobExecutionsPage.closeFilter();

                // verify sort by id ascending
                dataJobExecutionsPage.getDataGridExecIDHeader().should('exist').invoke('attr', 'aria-sort').should('eq', 'ascending');
                dataJobExecutionsPage
                    .getDataGridExecIDCell(1)
                    .invoke('text')
                    .invoke('trim')
                    .then((elText1) => {
                        return dataJobExecutionsPage
                            .getDataGridExecIDCell(2)
                            .invoke('text')
                            .invoke('trim')
                            .then((elText2) => {
                                return elText2 > elText1;
                            });
                    })
                    .should('be.true');

                // open id filter, verify then close
                dataJobExecutionsPage.openIDFilter();
                dataJobExecutionsPage.getDataGridInputFilter().should('exist').should('have.value', longLivedFailingJobFixture.job_name);
                // verify only cells that match the value are rendered
                dataJobExecutionsPage
                    .getDataGridExecIDCells()
                    .then(($cells) => {
                        const foundCells = Array.from($cells).map((cell) => new RegExp(`^${longLivedFailingJobFixture.job_name}-\d+$`).test(`${cell.innerText?.trim()}`));

                        return foundCells.length;
                    })
                    .should('gt', 0);
                dataJobExecutionsPage.closeFilter();

                // open exec start time filter, verify then close
                dataJobExecutionsPage.openExecStartFilter();
                dataJobExecutionsPage.generateExecStartFilterValue().then((filterValue) => {
                    // verify generated value prefilled in input field
                    dataJobExecutionsPage.getDataGridInputFilter().should('exist').should('have.value', filterValue);

                    // verify only cells that match the value are rendered
                    dataJobExecutionsPage
                        .getDataGridExecStartCells()
                        .then(($cells) => {
                            const foundCells = Array.from($cells).map((cell) => new RegExp(`${filterValue}$`).test(`${cell.innerText?.trim()}`));

                            return foundCells.length;
                        })
                        .should('gt', 0);
                });
                dataJobExecutionsPage.closeFilter();

                // open exec end time filter, verify then close
                dataJobExecutionsPage.openExecEndFilter();
                dataJobExecutionsPage.generateExecEndFilterValue().then((filterValue) => {
                    // verify generated value prefilled in input field
                    dataJobExecutionsPage.getDataGridInputFilter().should('exist').should('have.value', filterValue);

                    // verify only cells that match the value are rendered
                    dataJobExecutionsPage
                        .getDataGridExecEndCells()
                        .then(($cells) => {
                            const foundCells = Array.from($cells).map((cell) => new RegExp(`${filterValue}$`).test(`${cell.innerText?.trim()}`));

                            return foundCells.length;
                        })
                        .should('gt', 0);
                });
                dataJobExecutionsPage.closeFilter();
            });
        });
    });
});
