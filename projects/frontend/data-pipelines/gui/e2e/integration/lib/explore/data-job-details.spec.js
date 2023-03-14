/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />
import { DataJobsExplorePage } from "../../../support/pages/app/lib/explore/data-jobs.po";
import { DataJobExploreDetailsPage } from "../../../support/pages/app/lib/explore/data-job-details.po";

describe(
    "Data Job Explore Details Page",
    { tags: ["@dataPipelines", "@exploreDataJobDetails"] },
    () => {
        /**
         * @type {DataJobExploreDetailsPage}
         */
        let dataJobExploreDetailsPage;
        /**
         * @type {Array<{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}>}
         */
        let testJobsFixture;

        before(() => {
            return DataJobExploreDetailsPage.recordHarIfSupported()
                .then(() =>
                    cy.clearLocalStorageSnapshot("data-job-explore-details"),
                )
                .then(() => DataJobExploreDetailsPage.login())
                .then(() => cy.saveLocalStorage("data-job-explore-details"))
                .then(() => DataJobExploreDetailsPage.createTeam())
                .then(() =>
                    DataJobExploreDetailsPage.deleteShortLivedTestJobs(),
                )
                .then(() =>
                    DataJobExploreDetailsPage.createShortLivedTestJobs(),
                )
                .then(() =>
                    DataJobExploreDetailsPage.loadShortLivedTestJobsFixture().then(
                        (fixtures) => {
                            testJobsFixture = [fixtures[0], fixtures[1]];

                            return cy.wrap({
                                context:
                                    "explore::data-job-details.spec::before()",
                                action: "continue",
                            });
                        },
                    ),
                );
        });

        after(() => {
            DataJobExploreDetailsPage.deleteShortLivedTestJobs();

            DataJobExploreDetailsPage.saveHarIfSupported();
        });

        beforeEach(() => {
            cy.restoreLocalStorage("data-job-explore-details");

            DataJobExploreDetailsPage.wireUserSession();
            DataJobExploreDetailsPage.initInterceptors();
        });

        it("Data Job Explore Details Page - should load and show job details", () => {
            cy.log("Fixture for name: " + testJobsFixture[0].job_name);

            const dataJobsExplorePage = DataJobsExplorePage.navigateTo();

            dataJobsExplorePage.openJobDetails(
                testJobsFixture[0].team,
                testJobsFixture[0].job_name,
            );

            dataJobExploreDetailsPage = DataJobExploreDetailsPage.getPage();

            dataJobExploreDetailsPage
                .getDetailsTab()
                .scrollIntoView()
                .should("be.visible");

            dataJobExploreDetailsPage
                .getMainTitle()
                .scrollIntoView()
                .should("be.visible")
                .should("contains.text", testJobsFixture[0].job_name);

            dataJobExploreDetailsPage
                .getStatusField()
                .scrollIntoView()
                .should("be.visible")
                // TODO: do the right assertion (once it gets implemented)
                .should("have.text", "Not Deployed");

            dataJobExploreDetailsPage
                .getDescriptionField()
                .scrollIntoView()
                .should("be.visible")
                .should("contain.text", testJobsFixture[0].description);

            dataJobExploreDetailsPage
                .getTeamField()
                .scrollIntoView()
                .should("be.visible")
                .should("have.text", testJobsFixture[0].team);

            dataJobExploreDetailsPage
                .getScheduleField()
                .scrollIntoView()
                .should("be.visible")
                .should(
                    "contains.text",
                    "At 12:00 AM, on day 01 of the month, and on Friday",
                );

            // DISABLED Because there is no Source at the moment.
            // dataJobExploreDetailsPage
            // .getSourceField()
            // .should('be.visible')
            // .should('contains.text', 'http://host/data-jobs/' + testJobs[0].job_name)
            // .should("have.attr", "href", 'http://host/data-jobs/' + testJobs[0].job_name);

            dataJobExploreDetailsPage
                .getOnDeployedField()
                .scrollIntoView()
                .should("be.visible")
                .should(
                    "contains.text",
                    testJobsFixture[0].config.contacts.notified_on_job_deploy,
                );

            dataJobExploreDetailsPage
                .getOnPlatformErrorField()
                .scrollIntoView()
                .should("be.visible")
                .should(
                    "contains.text",
                    testJobsFixture[0].config.contacts
                        .notified_on_job_failure_platform_error,
                );

            dataJobExploreDetailsPage
                .getOnUserErrorField()
                .scrollIntoView()
                .should("be.visible")
                .should(
                    "contains.text",
                    testJobsFixture[0].config.contacts
                        .notified_on_job_failure_user_error,
                );

            dataJobExploreDetailsPage
                .getOnSuccessField()
                .scrollIntoView()
                .should("be.visible")
                .should(
                    "contains.text",
                    testJobsFixture[0].config.contacts.notified_on_job_success,
                );
        });

        it("Data Job Explore Details Page - should verify Details tab is visible and active", () => {
            cy.log("Fixture for name: " + testJobsFixture[0].job_name);

            const dataJobsExplorePage = DataJobsExplorePage.navigateTo();

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
                .getDetailsTab()
                .scrollIntoView()
                .should("be.visible")
                .should("have.class", "active");
        });

        it("Data Job Explore Details Page - should verify Action buttons are not displayed", () => {
            cy.log("Fixture for name: " + testJobsFixture[0].job_name);

            const dataJobsExplorePage = DataJobsExplorePage.navigateTo();

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

            dataJobExploreDetailsPage.getExecuteNowButton().should("not.exist");

            dataJobExploreDetailsPage
                .getActionDropdownBtn()
                .should("not.exist");
        });
    },
);
