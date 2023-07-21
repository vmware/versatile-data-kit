/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { compareDatesASC } from '../../../../../plugins/helpers/job-helpers.plugins';

import { DataJobsManagePage } from '../../../../../support/pages/manage/data-jobs/data-jobs.po';
import { DataJobManageDetailsPage } from '../../../../../support/pages/manage/data-jobs/details/data-job-details.po';

describe(
    'Data Job Manage Details Page',
    { tags: ['@dataPipelines', '@manageDataJobDetails', '@manage'] },
    () => {
        const descriptionWordsBeforeTruncate = 12;

        /**
         * @type {DataJobManageDetailsPage};
         */
        let dataJobManageDetailsPage;
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
        /**
         * @type {{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}}
         */
        let longLivedFailingJobFixture;

        before(() => {
            return DataJobManageDetailsPage.recordHarIfSupported()
                .then(() =>
                    cy.clearLocalStorageSnapshot('data-job-manage-details')
                )
                .then(() => DataJobManageDetailsPage.login())
                .then(() => cy.saveLocalStorage('data-job-manage-details'))
                .then(() =>
                    DataJobManageDetailsPage.deleteShortLivedTestJobsNoDeploy(
                        true
                    )
                )
                .then(() =>
                    DataJobManageDetailsPage.createLongLivedJobs('failing')
                )
                .then(() =>
                    DataJobManageDetailsPage.provideExecutionsForLongLivedJobs({
                        job: 'failing'
                    })
                )
                .then(() =>
                    DataJobManageDetailsPage.loadLongLivedFailingJobFixture().then(
                        (loadedTestJob) => {
                            longLivedFailingJobFixture = loadedTestJob;

                            return cy.wrap({
                                context:
                                    'manage::1::data-job-details.spec::before()',
                                action: 'continue'
                            });
                        }
                    )
                )
                .then(() =>
                    DataJobManageDetailsPage.createShortLivedTestJobWithDeploy(
                        'v1'
                    )
                )
                .then(() =>
                    DataJobManageDetailsPage.loadShortLivedTestJobFixtureWithDeploy(
                        'v1'
                    ).then((loadedTestJob) => {
                        shortLivedTestJobWithDeployFixture = loadedTestJob;

                        return cy.wrap({
                            context:
                                'manage::2::data-job-details.spec::before()',
                            action: 'continue'
                        });
                    })
                )
                .then(() =>
                    DataJobManageDetailsPage.createShortLivedTestJobsNoDeploy()
                )
                .then(() =>
                    DataJobManageDetailsPage.loadShortLivedTestJobsFixtureNoDeploy().then(
                        (fixtures) => {
                            testJobsFixture = [fixtures[0], fixtures[1]];
                            additionalTestJobFixture = fixtures[2];

                            return cy.wrap({
                                context:
                                    'manage::3::data-job-details.spec::before()',
                                action: 'continue'
                            });
                        }
                    )
                );
        });

        after(() => {
            DataJobManageDetailsPage.deleteShortLivedTestJobWithDeploy('v1');
            DataJobManageDetailsPage.deleteShortLivedTestJobsNoDeploy();

            DataJobManageDetailsPage.saveHarIfSupported();
        });

        beforeEach(() => {
            cy.restoreLocalStorage('data-job-manage-details');

            DataJobManageDetailsPage.wireUserSession();
            DataJobManageDetailsPage.initInterceptors();
        });

        describe('smoke', { tags: ['@smoke'] }, () => {
            it('should verify will open job details', () => {
                const dataJobsManagePage =
                    DataJobsManagePage.navigateWithSideMenu();

                dataJobsManagePage.chooseQuickFilter(0);

                // filter by job name substring because there are a lot of jobs, and it could potentially be on second/third page
                dataJobsManagePage.filterByJobName(
                    shortLivedTestJobWithDeployFixture.job_name.substring(0, 20)
                );

                dataJobsManagePage.openJobDetails(
                    shortLivedTestJobWithDeployFixture.team,
                    shortLivedTestJobWithDeployFixture.job_name
                );

                dataJobManageDetailsPage = DataJobManageDetailsPage.getPage();

                dataJobManageDetailsPage
                    .getPageTitle()
                    .invoke('text')
                    .invoke('trim')
                    .should(
                        'eq',
                        `Data Job: ${shortLivedTestJobWithDeployFixture.job_name}`
                    );
            });

            it('disable/enable job', () => {
                dataJobManageDetailsPage = DataJobManageDetailsPage.navigateTo(
                    shortLivedTestJobWithDeployFixture.team,
                    shortLivedTestJobWithDeployFixture.job_name
                );

                //Toggle job status twice, enable to disable and vice versa.
                dataJobManageDetailsPage.toggleJobStatus(
                    shortLivedTestJobWithDeployFixture.job_name
                );
                dataJobManageDetailsPage.toggleJobStatus(
                    shortLivedTestJobWithDeployFixture.job_name
                );
            });

            it('execute now', () => {
                dataJobManageDetailsPage = DataJobManageDetailsPage.navigateTo(
                    shortLivedTestJobWithDeployFixture.team,
                    shortLivedTestJobWithDeployFixture.job_name
                );

                DataJobManageDetailsPage.waitForShortLivedTestJobWithDeployExecutionToComplete(
                    'v1'
                );

                dataJobManageDetailsPage.executeNow();

                dataJobManageDetailsPage
                    .getToastTitle(10000)
                    .should('exist')
                    .contains(
                        /Data job Queued for execution|Failed, Data job is already executing/
                    );
            });

            it('delete job', () => {
                DataJobsManagePage.createAdditionalShortLivedTestJobsNoDeploy();

                dataJobManageDetailsPage = DataJobManageDetailsPage.navigateTo(
                    additionalTestJobFixture.team,
                    additionalTestJobFixture.job_name
                );

                dataJobManageDetailsPage.openActionDropdown();

                dataJobManageDetailsPage.deleteJob();

                dataJobManageDetailsPage
                    .getToastTitle(20000) // Wait up to 20 seconds for the job to be deleted.
                    .should('contain.text', 'Data job delete completed');

                const dataJobsManagePage = DataJobsManagePage.getPage();

                dataJobsManagePage.waitForGridDataLoad();

                dataJobsManagePage.chooseQuickFilter(0);

                dataJobsManagePage
                    .getDataGridCell(additionalTestJobFixture.job_name, 10000) // Wait up to 10 seconds for the jobs list to show.
                    .should('not.exist');
            });
        });

        describe('extended', () => {
            it('edit job description', () => {
                let newDescription =
                    'Test if changing the description is working';

                const dataJobsManagePage =
                    DataJobsManagePage.navigateWithSideMenu();

                dataJobsManagePage.chooseQuickFilter(0);

                // filter by job name substring because there are a lot of jobs, and it could potentially be on second/third page
                dataJobsManagePage.filterByJobName(
                    testJobsFixture[0].job_name.substring(0, 20)
                );

                dataJobsManagePage.openJobDetails(
                    testJobsFixture[0].team,
                    testJobsFixture[0].job_name
                );

                dataJobManageDetailsPage = DataJobManageDetailsPage.getPage();

                dataJobManageDetailsPage.openDescription();

                dataJobManageDetailsPage.enterDescriptionDetails(
                    newDescription
                );

                dataJobManageDetailsPage.saveDescription();

                dataJobManageDetailsPage
                    .getDescription()
                    .scrollIntoView()
                    .should('be.visible')
                    .should(
                        'contain.text',
                        newDescription
                            .split(' ')
                            .slice(0, descriptionWordsBeforeTruncate)
                            .join(' ')
                    );
            });

            it('download job key', () => {
                dataJobManageDetailsPage = DataJobManageDetailsPage.navigateTo(
                    shortLivedTestJobWithDeployFixture.team,
                    shortLivedTestJobWithDeployFixture.job_name
                );

                dataJobManageDetailsPage.openActionDropdown();

                dataJobManageDetailsPage.downloadJobKey();

                dataJobManageDetailsPage
                    .readFile(
                        'downloadsFolder',
                        `${shortLivedTestJobWithDeployFixture.job_name}.keytab`
                    )
                    .should('exist');
            });

            it('executions timeline', () => {
                const jobName = longLivedFailingJobFixture.job_name;
                const teamName = longLivedFailingJobFixture.team;

                dataJobManageDetailsPage = DataJobManageDetailsPage.navigateTo(
                    teamName,
                    jobName
                );

                dataJobManageDetailsPage
                    .waitForGetExecutionsReqInterceptor()
                    .then((interception) => {
                        const executionsResponse = [];
                        const content =
                            interception?.response?.body?.data?.content;

                        if (content) {
                            executionsResponse.push(...content);
                        }

                        const lastExecutions = executionsResponse
                            .sort((left, right) => compareDatesASC(left, right))
                            .slice(
                                executionsResponse.length > 5
                                    ? executionsResponse.length - 5
                                    : 0
                            );

                        const lastExecutionsSize = lastExecutions.length;
                        const lastExecution =
                            lastExecutions[lastExecutionsSize - 1];
                        const timelineSize = lastExecutionsSize + 1; // +1 next execution

                        dataJobManageDetailsPage
                            .getExecutionsSteps()
                            .should('have.length', timelineSize);

                        for (const execution of lastExecutions) {
                            const executionTimelineSelector = `[data-cy=${execution.id}]`;

                            const executionStartedTime =
                                dataJobManageDetailsPage.formatDateTimeFromISOToExecutionsTimeline(
                                    execution.startTime
                                );
                            dataJobManageDetailsPage
                                .getExecutionStepStartedTile(
                                    executionTimelineSelector
                                )
                                .invoke('trim')
                                .should(
                                    'eq',
                                    `Started ${executionStartedTime}`
                                );

                            if (execution?.type?.toLowerCase() === 'manual') {
                                dataJobManageDetailsPage
                                    .getExecutionStepManualTriggerer(
                                        executionTimelineSelector
                                    )
                                    .should('be.visible');
                            }

                            if (
                                execution?.status?.toLowerCase() !==
                                    'running' &&
                                execution?.status?.toLowerCase() !== 'submitted'
                            ) {
                                dataJobManageDetailsPage
                                    .getExecutionStepStatusIcon(
                                        executionTimelineSelector,
                                        execution.status
                                    )
                                    .should('exist');

                                const executionEndTime =
                                    dataJobManageDetailsPage.formatDateTimeFromISOToExecutionsTimeline(
                                        execution.endTime
                                    );
                                dataJobManageDetailsPage
                                    .getExecutionStepEndedTile(
                                        executionTimelineSelector
                                    )
                                    .invoke('trim')
                                    .should('eq', `Ended ${executionEndTime}`);
                            }
                        }
                    });
            });
        });
    }
);
