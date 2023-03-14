/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { compareDatesASC } from "../../../plugins/helpers/job-helpers.plugins";
import { DataJobManageDetailsPage } from "../../../support/pages/app/lib/manage/data-job-details.po";
import { DataJobsManagePage } from "../../../support/pages/app/lib/manage/data-jobs.po";

describe(
    "Data Job Manage Details Page",
    { tags: ["@dataPipelines", "@manageDataJobDetails"] },
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
        let longLivedTestJobFixture;

        before(() => {
            return DataJobManageDetailsPage.recordHarIfSupported()
                .then(() =>
                    cy.clearLocalStorageSnapshot("data-job-manage-details"),
                )
                .then(() => DataJobManageDetailsPage.login())
                .then(() => cy.saveLocalStorage("data-job-manage-details"))
                .then(() => DataJobManageDetailsPage.createTeam())
                .then(() => DataJobManageDetailsPage.deleteShortLivedTestJobs())
                .then(() =>
                    DataJobManageDetailsPage.createLongLivedJobs("test"),
                )
                .then(() =>
                    DataJobManageDetailsPage.provideExecutionsForLongLivedJobs(
                        "test",
                    ),
                )
                .then(() => DataJobManageDetailsPage.createShortLivedTestJobs())
                .then(() =>
                    DataJobManageDetailsPage.loadShortLivedTestJobsFixture().then(
                        (fixtures) => {
                            testJobsFixture = [fixtures[0], fixtures[1]];
                            additionalTestJobFixture = fixtures[2];

                            return cy.wrap({
                                context:
                                    "manage::data-job-details.spec::1::before()",
                                action: "continue",
                            });
                        },
                    ),
                )
                .then(() =>
                    DataJobManageDetailsPage.loadLongLivedTestJobFixture().then(
                        (loadedTestJob) => {
                            longLivedTestJobFixture = loadedTestJob;

                            return cy.wrap({
                                context:
                                    "manage::data-job-details.spec::2::before()",
                                action: "continue",
                            });
                        },
                    ),
                );
        });

        after(() => {
            DataJobManageDetailsPage.deleteShortLivedTestJobs();

            DataJobManageDetailsPage.saveHarIfSupported();
        });

        beforeEach(() => {
            cy.restoreLocalStorage("data-job-manage-details");

            DataJobManageDetailsPage.wireUserSession();
            DataJobManageDetailsPage.initInterceptors();
        });

        it(
            "Data Job Manage Details Page - disable/enable job",
            { tags: "@integration" },
            () => {
                dataJobManageDetailsPage = DataJobManageDetailsPage.navigateTo(
                    longLivedTestJobFixture.team,
                    longLivedTestJobFixture.job_name,
                );

                dataJobManageDetailsPage.clickOnContentContainer();

                //Toggle job status twice, enable to disable and vice versa.
                dataJobManageDetailsPage.toggleJobStatus(
                    longLivedTestJobFixture.job_name,
                );
                dataJobManageDetailsPage.toggleJobStatus(
                    longLivedTestJobFixture.job_name,
                );
            },
        );

        it(
            "Data Job Manage Details Page - edit job description",
            { tags: "@integration" },
            () => {
                let newDescription =
                    "Test if changing the description is working";

                dataJobManageDetailsPage = DataJobManageDetailsPage.navigateTo(
                    testJobsFixture[0].team,
                    testJobsFixture[0].job_name,
                );

                dataJobManageDetailsPage.clickOnContentContainer();

                dataJobManageDetailsPage.openDescription();

                dataJobManageDetailsPage.enterDescriptionDetails(
                    newDescription,
                );

                dataJobManageDetailsPage.saveDescription();

                dataJobManageDetailsPage
                    .getDescription()
                    .scrollIntoView()
                    .should("be.visible")
                    .should(
                        "contain.text",
                        newDescription
                            .split(" ")
                            .slice(0, descriptionWordsBeforeTruncate)
                            .join(" "),
                    );
            },
        );

        it("Data Job Manage Details Page - execute now", () => {
            dataJobManageDetailsPage = DataJobManageDetailsPage.navigateTo(
                longLivedTestJobFixture.team,
                longLivedTestJobFixture.job_name,
            );

            DataJobManageDetailsPage.waitForTestJobExecutionToComplete();

            dataJobManageDetailsPage.executeNow();

            dataJobManageDetailsPage.confirmInConfirmDialog();

            dataJobManageDetailsPage
                .getToastTitle(10000)
                .should("exist")
                .contains(
                    /Data job Queued for execution|Failed, Data job is already executing/,
                );
        });

        it("Data Job Manage Details Page - download job key", () => {
            dataJobManageDetailsPage = DataJobManageDetailsPage.navigateTo(
                longLivedTestJobFixture.team,
                longLivedTestJobFixture.job_name,
            );

            dataJobManageDetailsPage.openActionDropdown();

            dataJobManageDetailsPage.downloadJobKey();

            dataJobManageDetailsPage
                .readFile(
                    "downloadsFolder",
                    `${longLivedTestJobFixture.job_name}.keytab`,
                )
                .should("exist");
        });

        it(
            "Data Job Manage Details Page - delete job",
            { tags: "@integration" },
            () => {
                DataJobsManagePage.createAdditionalShortLivedTestJobs();

                dataJobManageDetailsPage = DataJobManageDetailsPage.navigateTo(
                    additionalTestJobFixture.team,
                    additionalTestJobFixture.job_name,
                );

                dataJobManageDetailsPage.clickOnContentContainer();

                dataJobManageDetailsPage.openActionDropdown();

                dataJobManageDetailsPage.deleteJob();

                dataJobManageDetailsPage.confirmDeleteJob();

                dataJobManageDetailsPage
                    .getToastTitle(20000) // Wait up to 20 seconds for the job to be deleted.
                    .should("contain.text", "Data job delete completed");

                dataJobManageDetailsPage.waitForBackendRequestCompletion();

                const dataJobsManagePage = DataJobsManagePage.getPage();

                dataJobsManagePage
                    .getDataGridCell(additionalTestJobFixture.job_name, 10000) // Wait up to 10 seconds for the jobs list to show.
                    .should("not.exist");
            },
        );

        //TODO: Double-check and enable this test
        it.skip("Data Job Manage Details Page - executions timeline", () => {
            const jobName = longLivedTestJobFixture.job_name;
            const team = longLivedTestJobFixture.team;

            cy.intercept({
                method: "GET",
                url: `/data-jobs/for-team/${team}/jobs/${jobName}/executions`,
            }).as("executionApiCall");

            dataJobManageDetailsPage = DataJobManageDetailsPage.navigateTo(
                team,
                jobName,
            );

            cy.wait("@executionApiCall").then((interception) => {
                const response = interception.response.body;
                const lastExecutions = response
                    .sort((left, right) => compareDatesAsc(left, right))
                    .slice(response.length > 5 ? response.length - 5 : 0);

                const lastExecutionsSize = lastExecutions.length;
                const lastExecution = lastExecutions.at(-1);

                cy.get(".clr-timeline-step").should(
                    "have.length",
                    lastExecutionsSize + 1,
                ); // +1 next execution

                cy.get(`[data-cy=${lastExecution.id}]`).as("lastExecution");

                let statusIconMap = [];
                statusIconMap["cancelled"] = "times-circle";
                statusIconMap["skipped"] = "circle-arrow";
                statusIconMap["submitted"] = "circle";
                statusIconMap["finished"] = "success-standard";
                statusIconMap["failed"] = "error-standard";

                if (lastExecution.type !== "manual") {
                    cy.get("@lastExecution")
                        .find(".manual-execution-label")
                        .scrollIntoView()
                        .should("be.visible");
                }

                if (lastExecution.status !== "running") {
                    cy.get("@lastExecution")
                        .find(`[shape=${statusIconMap[lastExecution.status]}]`)
                        .should("exist");
                }

                cy.get("@lastExecution")
                    .find(".clr-timeline-step-header")
                    .invoke("attr", "title")
                    .should("contain", "Started ");

                if (lastExecution.status !== "running") {
                    cy.get("@lastExecution")
                        .find("u")
                        .last()
                        .invoke("attr", "title")
                        .should("contain", "Ended ");
                }
            });
        });
    },
);
