/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />
// Contain tests on this page: http://localhost.vmware.com:4200/manage/data-jobs
// 1. Is search working
// When you click on details does a modal pop-up?

import { DataJobsManagePage } from "../../../support/pages/app/lib/manage/data-jobs.po";
import { DataJobManageDetailsPage } from "../../../support/pages/app/lib/manage/data-job-details.po";

describe(
    "Data Jobs Manage Page",
    { tags: ["@dataPipelines", "@manageDataJobs"] },
    () => {
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
        let longLivedTestJobFixture;

        before(() => {
            return DataJobsManagePage.recordHarIfSupported()
                .then(() => cy.clearLocalStorageSnapshot("data-jobs-manage"))
                .then(() => DataJobsManagePage.login())
                .then(() => cy.saveLocalStorage("data-jobs-manage"))
                .then(() => DataJobsManagePage.createTeam())
                .then(() => DataJobsManagePage.deleteShortLivedTestJobs())
                .then(() =>
                    DataJobsManagePage.createLongLivedJobs("test", "failing"),
                )
                .then(() =>
                    DataJobsManagePage.provideExecutionsForLongLivedJobs(
                        "test",
                    ),
                )
                .then(() => DataJobsManagePage.createShortLivedTestJobs())
                .then(() =>
                    DataJobsManagePage.loadShortLivedTestJobsFixture().then(
                        (fixtures) => {
                            testJobsFixture = [fixtures[0], fixtures[1]];
                            additionalTestJobFixture = fixtures[2];

                            return cy.wrap({
                                context:
                                    "manage::1::data-jobs.int.spec::before()",
                                action: "continue",
                            });
                        },
                    ),
                )
                .then(() =>
                    DataJobsManagePage.loadLongLivedTestJobFixture().then(
                        (loadedTestJob) => {
                            longLivedTestJobFixture = loadedTestJob;

                            return cy.wrap({
                                context:
                                    "manage::2::data-jobs.int.spec::before()",
                                action: "continue",
                            });
                        },
                    ),
                )
                .then(() =>
                    // Enable data job at the end of before suite
                    DataJobsManagePage.changeLongLivedJobStatus("test", true),
                )
                .then(() => DataJobsManagePage.waitBeforeSuiteState())
                .then(() =>
                    cy.wrap({
                        context: "manage::3::data-jobs.int.spec::before()",
                        action: "continue",
                    }),
                );
        });

        after(() => {
            DataJobsManagePage.deleteShortLivedTestJobs();

            // Enable data job after tests suites end
            DataJobsManagePage.changeLongLivedJobStatus("test", true);

            DataJobsManagePage.saveHarIfSupported();
        });

        beforeEach(() => {
            cy.restoreLocalStorage("data-jobs-manage");

            DataJobsManagePage.wireUserSession();
            DataJobsManagePage.initInterceptors();

            dataJobsManagePage = DataJobsManagePage.navigateTo();
        });

        it("Data Jobs Manage Page - loads title", () => {
            dataJobsManagePage
                .getPageTitle()
                .scrollIntoView()
                .should("be.visible");
        });

        it("Data Jobs Manage Page - grid contains test jobs", () => {
            dataJobsManagePage.chooseQuickFilter(0);

            dataJobsManagePage.filterByJobName(
                testJobsFixture[0].job_name.substring(0, 14),
            );

            dataJobsManagePage
                .getDataGrid()
                .scrollIntoView()
                .should("be.visible");

            testJobsFixture.forEach((testJob) => {
                cy.log("Fixture for name: " + testJob.job_name);

                dataJobsManagePage
                    .getDataGridCell(testJob.job_name)
                    .scrollIntoView()
                    .should("be.visible");
            });
        });

        it(
            "Data Jobs Manage Page - grid filter by job name",
            { tags: "@integration" },
            () => {
                dataJobsManagePage.chooseQuickFilter(0);

                dataJobsManagePage.filterByJobName(testJobsFixture[0].job_name);

                dataJobsManagePage
                    .getDataGridCell(testJobsFixture[0].job_name)
                    .scrollIntoView()
                    .should("be.visible");

                dataJobsManagePage
                    .getDataGridCell(testJobsFixture[1].job_name)
                    .should("not.exist");
            },
        );

        it(
            "Data Jobs Manage Page - grid search by job name",
            { tags: "@integration" },
            () => {
                dataJobsManagePage.clickOnContentContainer();

                dataJobsManagePage.chooseQuickFilter(0);

                dataJobsManagePage.searchByJobName(testJobsFixture[1].job_name);

                dataJobsManagePage
                    .getDataGridCell(testJobsFixture[0].job_name)
                    .should("not.exist");

                dataJobsManagePage
                    .getDataGridCell(testJobsFixture[1].job_name)
                    .scrollIntoView()
                    .should("be.visible");
            },
        );

        it("Data Jobs Manage Page - grid search parameter goes into URL", () => {
            dataJobsManagePage.chooseQuickFilter(0);

            dataJobsManagePage.filterByJobName(
                testJobsFixture[0].job_name.substring(0, 14),
            );

            // verify 2 test rows visible
            dataJobsManagePage
                .getDataGridCell(testJobsFixture[0].job_name)
                .scrollIntoView()
                .should("be.visible");
            dataJobsManagePage
                .getDataGridCell(testJobsFixture[1].job_name)
                .scrollIntoView()
                .should("be.visible");

            // do search
            dataJobsManagePage.searchByJobName(testJobsFixture[0].job_name);

            dataJobsManagePage.waitForViewToRender();

            // verify 1 test row visible
            dataJobsManagePage
                .getDataGridCell(testJobsFixture[0].job_name)
                .scrollIntoView()
                .should("be.visible");
            dataJobsManagePage
                .getDataGridCell(testJobsFixture[1].job_name)
                .should("not.exist");

            // verify url contains search value
            dataJobsManagePage
                .getCurrentUrl()
                .should(
                    "match",
                    new RegExp(
                        `\\/manage\\/data-jobs\\?search=${testJobsFixture[0].job_name}$`,
                    ),
                );

            // clear search with clear() method
            dataJobsManagePage.clearSearchField();

            dataJobsManagePage.waitForViewToRender();

            // verify 2 test rows visible
            dataJobsManagePage
                .getDataGridCell(testJobsFixture[0].job_name)
                .scrollIntoView()
                .should("be.visible");
            dataJobsManagePage
                .getDataGridCell(testJobsFixture[1].job_name)
                .scrollIntoView()
                .should("be.visible");

            // verify url does not contain search value
            dataJobsManagePage
                .getCurrentUrl()
                .should("match", new RegExp(`\\/manage\\/data-jobs$`));
        });

        it("Data Jobs Manage Page - grid search perform search when URL contains search parameter", () => {
            // navigate with search value in URL
            dataJobsManagePage = DataJobsManagePage.navigateToUrl(
                `/manage/data-jobs?search=${testJobsFixture[1].job_name}`,
            );

            dataJobsManagePage.chooseQuickFilter(0);

            dataJobsManagePage.sortByJobName();

            // verify url contains search value
            dataJobsManagePage
                .getCurrentUrl()
                .should(
                    "match",
                    new RegExp(
                        `\\/manage\\/data-jobs\\?search=${testJobsFixture[1].job_name}$`,
                    ),
                );

            // verify 1 test row visible
            dataJobsManagePage
                .getDataGridCell(testJobsFixture[0].job_name)
                .should("not.exist");
            dataJobsManagePage
                .getDataGridCell(testJobsFixture[1].job_name)
                .scrollIntoView()
                .should("be.visible");

            // clear search with button
            dataJobsManagePage.clearSearchFieldWithButton();

            // verify 2 test rows visible
            dataJobsManagePage
                .getDataGridCell(testJobsFixture[0].job_name)
                .scrollIntoView()
                .should("be.visible");
            dataJobsManagePage
                .getDataGridCell(testJobsFixture[1].job_name)
                .scrollIntoView()
                .should("be.visible");

            // verify url does not contain search value
            dataJobsManagePage
                .getCurrentUrl()
                .should("match", new RegExp(`\\/manage\\/data-jobs$`));
        });

        it("Data Jobs Manage Page - refresh shows newly created job", () => {
            dataJobsManagePage.chooseQuickFilter(0);

            dataJobsManagePage.filterByJobName(
                testJobsFixture[0].job_name.substring(0, 14),
            );

            dataJobsManagePage
                .getDataGridCell(testJobsFixture[0].job_name)
                .should("have.text", testJobsFixture[0].job_name);

            dataJobsManagePage
                .getDataGridCell(additionalTestJobFixture.job_name)
                .should("not.exist");

            DataJobsManagePage.createAdditionalShortLivedTestJobs();

            dataJobsManagePage.refreshDataGrid();

            dataJobsManagePage.filterByJobName(
                additionalTestJobFixture.job_name,
            );

            dataJobsManagePage
                .getDataGridCell(additionalTestJobFixture.job_name)
                .should("have.text", additionalTestJobFixture.job_name);
        });

        it(
            "Data Jobs Manage Page - click on edit button opens new page with Job details",
            { tags: "@integration" },
            () => {
                dataJobsManagePage.clickOnContentContainer();

                dataJobsManagePage.chooseQuickFilter(0);

                dataJobsManagePage.filterByJobName(
                    testJobsFixture[0].job_name.substring(0, 14),
                );

                dataJobsManagePage.sortByJobName();

                dataJobsManagePage.openJobDetails(
                    testJobsFixture[0].team,
                    testJobsFixture[0].job_name,
                );

                const dataJobManageDetailsPage =
                    DataJobManageDetailsPage.getPage();

                dataJobManageDetailsPage
                    .getMainTitle()
                    .scrollIntoView()
                    .should("be.visible")
                    .should("contains.text", testJobsFixture[0].job_name);

                dataJobManageDetailsPage
                    .getDescription()
                    .scrollIntoView()
                    .should("be.visible")
                    .should(
                        "contain.text",
                        testJobsFixture[0].description
                            .split(" ")
                            .slice(0, descriptionWordsBeforeTruncate)
                            .join(" "),
                    );

                dataJobManageDetailsPage
                    .getSchedule()
                    .scrollIntoView()
                    .should("be.visible");

                dataJobManageDetailsPage
                    .getDeploymentStatus("not-deployed")
                    .scrollIntoView()
                    .should("be.visible")
                    .should("have.text", "Not Deployed");
            },
        );

        it(
            "Data Jobs Manage Page - disable/enable job",
            { tags: "@integration" },
            () => {
                dataJobsManagePage.clickOnContentContainer();

                dataJobsManagePage.chooseQuickFilter(0);

                const jobName = longLivedTestJobFixture.job_name;
                const team = longLivedTestJobFixture.team;

                dataJobsManagePage.searchByJobName(jobName);

                //Toggle job status twice, enable to disable and vice versa.
                dataJobsManagePage.toggleJobStatus(
                    longLivedTestJobFixture.job_name,
                );
                dataJobsManagePage.toggleJobStatus(
                    longLivedTestJobFixture.job_name,
                );
            },
        );

        it(
            "Data Jobs Manage Page - quick filters",
            { tags: "@integration" },
            () => {
                // Disable data job before test start
                DataJobsManagePage.changeLongLivedJobStatus("failing", true)
                    .then(() =>
                        DataJobsManagePage.changeLongLivedJobStatus(
                            "test",
                            false,
                        ),
                    )
                    .then(() => {
                        dataJobsManagePage.clickOnContentContainer();

                        dataJobsManagePage.waitForClickThinkingTime();
                        dataJobsManagePage.chooseQuickFilter(0);
                        dataJobsManagePage.waitForViewToRender();

                        dataJobsManagePage
                            .getDataGridStatusIcons()
                            .then(($icons) => {
                                for (const icon of Array.from($icons)) {
                                    cy.wrap(icon)
                                        .invoke("attr", "data-cy")
                                        .should(
                                            "match",
                                            new RegExp(
                                                "data-pipelines-job-(enabled|disabled|not-deployed)",
                                            ),
                                        );
                                }
                            });

                        dataJobsManagePage.waitForClickThinkingTime();
                        dataJobsManagePage.chooseQuickFilter(1);
                        dataJobsManagePage.waitForViewToRender();

                        dataJobsManagePage
                            .getDataGridStatusIcons()
                            .then(($icons) => {
                                for (const icon of Array.from($icons)) {
                                    cy.wrap(icon).should(
                                        "have.attr",
                                        "data-cy",
                                        "data-pipelines-job-enabled",
                                    );
                                }
                            });

                        dataJobsManagePage.waitForClickThinkingTime();
                        dataJobsManagePage.chooseQuickFilter(2);
                        dataJobsManagePage.waitForViewToRender();

                        dataJobsManagePage
                            .getDataGridStatusIcons()
                            .then(($icons) => {
                                for (const icon of Array.from($icons)) {
                                    cy.wrap(icon).should(
                                        "have.attr",
                                        "data-cy",
                                        "data-pipelines-job-disabled",
                                    );
                                }
                            });

                        dataJobsManagePage.waitForClickThinkingTime();
                        dataJobsManagePage.chooseQuickFilter(3);
                        dataJobsManagePage.waitForViewToRender();

                        dataJobsManagePage
                            .getDataGridStatusIcons()
                            .then(($icons) => {
                                for (const icon of Array.from($icons)) {
                                    cy.wrap(icon).should(
                                        "have.attr",
                                        "data-cy",
                                        "data-pipelines-job-not-deployed",
                                    );
                                }
                            });

                        // Enable data job after job end
                        DataJobsManagePage.changeLongLivedJobStatus(
                            "test",
                            true,
                        );
                    });
            },
        );

        it("Data Jobs Manage Page - show/hide column when toggling from menu", () => {
            // show panel for show/hide columns
            dataJobsManagePage.toggleColumnShowHidePanel();

            // verify correct options are rendered
            dataJobsManagePage
                .getDataGridColumnShowHideOptionsValues()
                .should("have.length", 10)
                .invoke("join", ",")
                .should(
                    "eq",
                    "Description,Deployment Status,Last Execution Duration,Success rate,Next run (UTC),Last Deployed (UTC),Last Deployed By,Notifications,Source,Logs",
                );

            // verify column is not checked in toggling menu
            dataJobsManagePage
                .getDataGridColumnShowHideOption("Notifications")
                .should("exist")
                .should("not.be.checked");

            // verify header cell for column is not rendered
            dataJobsManagePage
                .getDataGridHeaderCell("Notifications")
                .should("have.length", 0);

            // toggle column to render
            dataJobsManagePage.checkColumnShowHideOption("Notifications");

            // verify column is checked in toggling menu
            dataJobsManagePage
                .getDataGridColumnShowHideOption("Notifications")
                .should("exist")
                .should("be.checked");

            // verify header cell for column is rendered
            dataJobsManagePage
                .getDataGridHeaderCell("Notifications")
                .should("have.length", 1);

            // toggle column to hide
            dataJobsManagePage.uncheckColumnShowHideOption("Notifications");

            // verify column is not checked in toggling menu
            dataJobsManagePage
                .getDataGridColumnShowHideOption("Notifications")
                .should("exist")
                .should("not.be.checked");

            // verify header cell for column is not rendered
            dataJobsManagePage
                .getDataGridHeaderCell("Notifications")
                .should("have.length", 0);

            // hide panel for show/hide columns
            dataJobsManagePage.toggleColumnShowHidePanel();
        });

        it(
            "Data Jobs Manage Page - execute now",
            { tags: "@integration" },
            () => {
                const jobName = longLivedTestJobFixture.job_name;
                const team = longLivedTestJobFixture.team;

                dataJobsManagePage.chooseQuickFilter(0);

                dataJobsManagePage.filterByJobName(jobName.substring(0, 14));

                dataJobsManagePage.executeDataJob(jobName);

                // TODO better handling toast message. If tests are executed immediately it will return
                // error 409 conflict and it will say that the job is already executing
                dataJobsManagePage
                    .getToastTitle(10000) // Wait up to 10 seconds for Toast to show.
                    .should("exist")
                    .contains(
                        /Data job Queued for execution|Failed, Data job is already executing/,
                    );
            },
        );

        it(
            `Data Jobs Manage Page - execute now is disabled when Job doesn't have deployment`,
            { tags: "@integration" },
            () => {
                const jobName = testJobsFixture[0].job_name;
                const team = testJobsFixture[0].team;

                dataJobsManagePage.chooseQuickFilter(0);

                dataJobsManagePage.filterByJobName(jobName.substring(0, 14));

                dataJobsManagePage.selectRow(jobName);

                dataJobsManagePage.waitForViewToRenderShort();
                dataJobsManagePage.waitForClickThinkingTime();

                dataJobsManagePage
                    .getExecuteNowGridButton()
                    .should("be.disabled");
            },
        );
    },
);
