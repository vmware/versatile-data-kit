/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { DataJobManageDetailsPage } from "../../../support/pages/app/lib/manage/data-job-details.po";
import { DataJobsManagePage } from "../../../support/pages/app/lib/manage/data-jobs.po";
import { applyGlobalEnvSettings } from "../../../support/helpers/commands.helpers";

describe(
    "Data Job Manage Details Page",
    { tags: ["@dataPipelines", "@manageDataJobDetails"] },
    () => {
        const descriptionWordsBeforeTruncate = 12;

        let dataJobManageDetailsPage;
        let testJobs;
        let longLivedTestJob;

        before(() => {
            return DataJobManageDetailsPage.recordHarIfSupported()
                .then(() =>
                    cy.clearLocalStorageSnapshot("data-job-manage-details"),
                )
                .then(() => DataJobManageDetailsPage.login())
                .then(() => cy.saveLocalStorage("data-job-manage-details"))
                .then(() => cy.cleanTestJobs())
                .then(() => cy.prepareLongLivedTestJob())
                .then(() => cy.createTwoExecutionsLongLivedTestJob())
                .then(() => cy.prepareBaseTestJobs())
                .then(() => cy.fixture("lib/explore/test-jobs.json"))
                .then((loadedTestJobs) => {
                    testJobs = applyGlobalEnvSettings(loadedTestJobs);

                    return cy.wrap({
                        context: "manage::data-job-details.spec::1::before()",
                        action: "continue",
                    });
                })
                .then(() => cy.fixture("lib/manage/e2e-cypress-dp-test.json"))
                .then((loadedTestJob) => {
                    longLivedTestJob = applyGlobalEnvSettings(loadedTestJob);

                    return cy.wrap({
                        context: "manage::data-job-details.spec::2::before()",
                        action: "continue",
                    });
                });
        });

        after(() => {
            cy.cleanTestJobs();

            DataJobManageDetailsPage.saveHarIfSupported();
        });

        beforeEach(() => {
            cy.restoreLocalStorage("data-job-manage-details");

            DataJobManageDetailsPage.initBackendRequestInterceptor();
        });

        it(
            "Data Job Manage Details Page - disable/enable job",
            { tags: "@integration" },
            () => {
                dataJobManageDetailsPage = DataJobManageDetailsPage.navigateTo(
                    longLivedTestJob.team,
                    longLivedTestJob.job_name,
                );

                dataJobManageDetailsPage.clickOnContentContainer();

                //Toggle job status twice, enable to disable and vice versa.
                dataJobManageDetailsPage.toggleJobStatus(
                    longLivedTestJob.job_name,
                );
                dataJobManageDetailsPage.toggleJobStatus(
                    longLivedTestJob.job_name,
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
                    testJobs[0].team,
                    testJobs[0].job_name,
                );

                dataJobManageDetailsPage.clickOnContentContainer();

                dataJobManageDetailsPage.openDescription();

                dataJobManageDetailsPage.enterDescriptionDetails(
                    newDescription,
                );

                dataJobManageDetailsPage.saveDescription();

                dataJobManageDetailsPage
                    .getDescription()
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
                longLivedTestJob.team,
                longLivedTestJob.job_name,
            );

            dataJobManageDetailsPage.waitForTestJobExecutionCompletion();

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
                longLivedTestJob.team,
                longLivedTestJob.job_name,
            );

            dataJobManageDetailsPage.openActionDropdown();

            dataJobManageDetailsPage.downloadJobKey();

            dataJobManageDetailsPage
                .readFile(
                    "downloadsFolder",
                    `${longLivedTestJob.job_name}.keytab`,
                )
                .should("exist");
        });

        it(
            "Data Job Manage Details Page - delete job",
            { tags: "@integration" },
            () => {
                cy.fixture("lib/explore/additional-test-job.json").then(
                    (additionalTestJob) => {
                        const normalizedTestJob =
                            applyGlobalEnvSettings(additionalTestJob);

                        cy.prepareAdditionalTestJobs();

                        dataJobManageDetailsPage =
                            DataJobManageDetailsPage.navigateTo(
                                normalizedTestJob.team,
                                normalizedTestJob.job_name,
                            );

                        dataJobManageDetailsPage.clickOnContentContainer();

                        dataJobManageDetailsPage.openActionDropdown();

                        dataJobManageDetailsPage.deleteJob();

                        dataJobManageDetailsPage.confirmDeleteJob();

                        dataJobManageDetailsPage
                            .getToastTitle(20000) // Wait up to 20 seconds for the job to be deleted.
                            .should(
                                "contain.text",
                                "Data job delete completed",
                            );

                        dataJobManageDetailsPage.waitForBackendRequestCompletion();

                        const dataJobsManagePage = DataJobsManagePage.getPage();

                        dataJobsManagePage
                            .getDataGridCell(normalizedTestJob.job_name, 10000) // Wait up to 10 seconds for the jobs list to show.
                            .should("not.exist");
                    },
                );
            },
        );

        //TODO: Double-check and enable this test
        it.skip("Data Job Manage Details Page - executions timeline", () => {
            const jobName = longLivedTestJob.job_name;
            const team = longLivedTestJob.team;

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
