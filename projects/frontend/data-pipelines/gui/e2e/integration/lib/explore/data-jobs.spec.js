/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { DataJobsExplorePage } from "../../../support/pages/app/lib/explore/data-jobs.po";
import { DataJobExploreDetailsPage } from "../../../support/pages/app/lib/explore/data-job-details.po";

describe(
    "Data Jobs Explore Page",
    { tags: ["@dataPipelines", "@exploreDataJobs"] },
    () => {
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
                .then(() => cy.clearLocalStorageSnapshot("data-jobs-explore"))
                .then(() => DataJobsExplorePage.login())
                .then(() => cy.saveLocalStorage("data-jobs-explore"))
                .then(() => DataJobsExplorePage.createTeam())
                .then(() => DataJobsExplorePage.deleteShortLivedTestJobs())
                .then(() => DataJobsExplorePage.createShortLivedTestJobs())
                .then(() =>
                    DataJobsExplorePage.loadShortLivedTestJobsFixture().then(
                        (fixtures) => {
                            testJobsFixture = [fixtures[0], fixtures[1]];
                            additionalTestJobFixture = fixtures[2];

                            return cy.wrap({
                                context: "explore::data-jobs.spec::before()",
                                action: "continue",
                            });
                        },
                    ),
                );
        });

        after(() => {
            DataJobsExplorePage.deleteShortLivedTestJobs();

            DataJobsExplorePage.saveHarIfSupported();
        });

        beforeEach(() => {
            cy.restoreLocalStorage("data-jobs-explore");

            DataJobsExplorePage.wireUserSession();
            DataJobsExplorePage.initInterceptors();
        });

        it("Main Title Component have text: Explore Data Jobs", () => {
            dataJobsExplorePage = DataJobsExplorePage.navigateTo();

            dataJobsExplorePage
                .getMainTitle()
                .scrollIntoView()
                .should("be.visible")
                .should("have.text", "Explore Data Jobs");
        });

        it("Data Jobs Explore Page - loaded and shows data jobs", () => {
            dataJobsExplorePage = DataJobsExplorePage.navigateTo();

            dataJobsExplorePage
                .getDataGrid()
                .scrollIntoView()
                .should("be.visible");

            testJobsFixture.forEach((testJob) => {
                cy.log("Fixture for name: " + testJob.job_name);

                dataJobsExplorePage
                    .getDataGridCell(testJob.job_name)
                    .scrollIntoView()
                    .should("be.visible");

                dataJobsExplorePage
                    .getDataGridCell(testJob.team)
                    .scrollIntoView()
                    .should("be.visible");
            });
        });

        it("Data Jobs Explore Page - filters data jobs", () => {
            cy.log("Fixture for name: " + testJobsFixture[0].job_name);

            dataJobsExplorePage = DataJobsExplorePage.navigateTo();

            dataJobsExplorePage.filterByJobName(testJobsFixture[0].job_name);

            dataJobsExplorePage
                .getDataGridCell(testJobsFixture[0].job_name)
                .scrollIntoView()
                .should("be.visible");

            dataJobsExplorePage
                .getDataGridCell(testJobsFixture[1].job_name)
                .should("not.exist");
        });

        it("Data Jobs Explore Page - refreshes data jobs", () => {
            dataJobsExplorePage = DataJobsExplorePage.navigateTo();

            dataJobsExplorePage
                .getDataGridCell(testJobsFixture[0].job_name)
                .should("have.text", testJobsFixture[0].job_name);

            dataJobsExplorePage
                .getDataGridCell(additionalTestJobFixture.job_name)
                .should("not.exist");

            DataJobsExplorePage.createAdditionalShortLivedTestJobs();

            dataJobsExplorePage.refreshDataGrid();

            dataJobsExplorePage.filterByJobName(
                additionalTestJobFixture.job_name,
            );

            dataJobsExplorePage
                .getDataGridCell(additionalTestJobFixture.job_name)
                .should("have.text", additionalTestJobFixture.job_name);
        });

        it("Data Jobs Explore Page - searches data jobs", () => {
            cy.log("Fixture for name: " + testJobsFixture[0].job_name);

            dataJobsExplorePage = DataJobsExplorePage.navigateTo();

            dataJobsExplorePage
                .getDataGridCell(testJobsFixture[1].job_name)
                .scrollIntoView()
                .should("be.visible");

            dataJobsExplorePage.searchByJobName(testJobsFixture[0].job_name);

            dataJobsExplorePage
                .getDataGridCell(testJobsFixture[0].job_name)
                .scrollIntoView()
                .should("be.visible");

            dataJobsExplorePage
                .getDataGridCell(testJobsFixture[1].job_name)
                .should("not.exist");
        });

        it("Data Jobs Explore Page - searches data jobs, search parameter goes into URL", () => {
            cy.log("Fixture for name: " + testJobsFixture[0].job_name);

            dataJobsExplorePage = DataJobsExplorePage.navigateTo();

            // verify 2 test rows visible
            dataJobsExplorePage
                .getDataGridCell(testJobsFixture[0].job_name)
                .scrollIntoView()
                .should("be.visible");
            dataJobsExplorePage
                .getDataGridCell(testJobsFixture[1].job_name)
                .scrollIntoView()
                .should("be.visible");

            // do search
            dataJobsExplorePage.searchByJobName(testJobsFixture[0].job_name);

            // verify 1 test row visible
            dataJobsExplorePage
                .getDataGridCell(testJobsFixture[0].job_name)
                .scrollIntoView()
                .should("be.visible");
            dataJobsExplorePage
                .getDataGridCell(testJobsFixture[1].job_name)
                .should("not.exist");

            // verify url contains search value
            dataJobsExplorePage
                .getCurrentUrl()
                .should(
                    "match",
                    new RegExp(
                        `\\/explore\\/data-jobs\\?search=${testJobsFixture[0].job_name}$`,
                    ),
                );

            // clear search with clear() method
            dataJobsExplorePage.clearSearchField();

            // verify 2 test rows visible
            dataJobsExplorePage
                .getDataGridCell(testJobsFixture[0].job_name)
                .scrollIntoView()
                .should("be.visible");
            dataJobsExplorePage
                .getDataGridCell(testJobsFixture[1].job_name)
                .scrollIntoView()
                .should("be.visible");

            // verify url does not contain search value
            dataJobsExplorePage
                .getCurrentUrl()
                .should("match", new RegExp(`\\/explore\\/data-jobs$`));
        });

        it("Data Jobs Explore Page - searches data jobs, perform search when URL contains search parameter", () => {
            cy.log("Fixture for name: " + testJobsFixture[1].job_name);

            // navigate with search value in URL
            dataJobsExplorePage = DataJobsExplorePage.navigateToUrl(
                `/explore/data-jobs?search=${testJobsFixture[1].job_name}`,
            );

            // verify url contains search value
            dataJobsExplorePage
                .getCurrentUrl()
                .should(
                    "match",
                    new RegExp(
                        `\\/explore\\/data-jobs\\?search=${testJobsFixture[1].job_name}$`,
                    ),
                );

            // verify 1 test row visible
            dataJobsExplorePage
                .getDataGridCell(testJobsFixture[0].job_name)
                .should("not.exist");
            dataJobsExplorePage
                .getDataGridCell(testJobsFixture[1].job_name)
                .scrollIntoView()
                .should("be.visible");

            // clear search with button
            dataJobsExplorePage.clearSearchFieldWithButton();

            // verify 2 test rows visible
            dataJobsExplorePage
                .getDataGridCell(testJobsFixture[0].job_name)
                .scrollIntoView()
                .should("be.visible");
            dataJobsExplorePage
                .getDataGridCell(testJobsFixture[1].job_name)
                .scrollIntoView()
                .should("be.visible");

            // verify url does not contain search value
            dataJobsExplorePage
                .getCurrentUrl()
                .should("match", new RegExp(`\\/explore\\/data-jobs$`));
        });

        it("Data Jobs Explore Page - show/hide column when toggling from menu", () => {
            dataJobsExplorePage = DataJobsExplorePage.navigateTo();

            // show panel for show/hide columns
            dataJobsExplorePage.toggleColumnShowHidePanel();

            // verify correct options are rendered
            dataJobsExplorePage
                .getDataGridColumnShowHideOptionsValues()
                .should("have.length", 9)
                .invoke("join", ",")
                .should(
                    "eq",
                    "Description,Deployment Status,Last Execution Duration,Success rate,Next run (UTC),Last Deployed (UTC),Last Deployed By,Source,Logs",
                );

            // verify column is not checked in toggling menu
            dataJobsExplorePage
                .getDataGridColumnShowHideOption("Last Execution Duration")
                .should("exist")
                .should("not.be.checked");

            // verify header cell for column is not rendered
            dataJobsExplorePage
                .getDataGridHeaderCell("Last Execution Duration")
                .should("have.length", 0);

            // toggle column to render
            dataJobsExplorePage.checkColumnShowHideOption(
                "Last Execution Duration",
            );

            // verify column is checked in toggling menu
            dataJobsExplorePage
                .getDataGridColumnShowHideOption("Last Execution Duration")
                .should("exist")
                .should("be.checked");

            // verify header cell for column is rendered
            dataJobsExplorePage
                .getDataGridHeaderCell("Last Execution Duration")
                .should("have.length", 1);

            // toggle column to hide
            dataJobsExplorePage.uncheckColumnShowHideOption(
                "Last Execution Duration",
            );

            // verify column is not checked in toggling menu
            dataJobsExplorePage
                .getDataGridColumnShowHideOption("Last Execution Duration")
                .should("exist")
                .should("not.be.checked");

            // verify header cell for column is not rendered
            dataJobsExplorePage
                .getDataGridHeaderCell("Last Execution Duration")
                .should("have.length", 0);

            // hide panel for show/hide columns
            dataJobsExplorePage.toggleColumnShowHidePanel();
        });

        it("Data Jobs Explore Page - navigates to data job", () => {
            cy.log("Fixture for name: " + testJobsFixture[0].job_name);

            dataJobsExplorePage = DataJobsExplorePage.navigateTo();

            dataJobsExplorePage.openJobDetails(
                testJobsFixture[0].team,
                testJobsFixture[0].job_name,
            );

            const dataJobExploreDetailsPage =
                DataJobExploreDetailsPage.getPage();

            dataJobExploreDetailsPage
                .getMainTitle()
                .scrollIntoView()
                .should("be.visible")
                .should("contains.text", testJobsFixture[0].job_name);

            dataJobExploreDetailsPage
                .getDescriptionField()
                .scrollIntoView()
                .should("be.visible")
                .should("contain.text", testJobsFixture[0].description);
        });
    },
);
