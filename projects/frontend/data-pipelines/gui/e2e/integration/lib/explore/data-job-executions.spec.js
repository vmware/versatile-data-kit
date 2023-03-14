/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { DataJobBasePO } from "../../../support/application/data-job-base.po";
import { DataJobsExplorePage } from "../../../support/pages/app/lib/explore/data-jobs.po";
import { DataJobDetailsBasePO } from "../../../support/application/data-job-details-base.po";

describe(
    "Data Job Explore Executions Page",
    { tags: ["@dataPipelines", "@exploreDataJobExecutions"] },
    () => {
        /**
         * @type {Array<{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}>}
         */
        let testJobsFixture;

        before(() => {
            return DataJobBasePO.recordHarIfSupported()
                .then(() =>
                    cy.clearLocalStorageSnapshot("data-job-explore-executions"),
                )
                .then(() => DataJobBasePO.login())
                .then(() => cy.saveLocalStorage("data-job-explore-executions"))
                .then(() => DataJobBasePO.createTeam())
                .then(() => DataJobBasePO.deleteShortLivedTestJobs())
                .then(() => DataJobBasePO.createShortLivedTestJobs())
                .then(() =>
                    DataJobBasePO.loadShortLivedTestJobsFixture().then(
                        (fixtures) => {
                            testJobsFixture = [fixtures[0], fixtures[1]];

                            return cy.wrap({
                                context:
                                    "explore::data-job-executions.spec::before()",
                                action: "continue",
                            });
                        },
                    ),
                );
        });

        after(() => {
            DataJobBasePO.deleteShortLivedTestJobs();

            DataJobBasePO.saveHarIfSupported();
        });

        beforeEach(() => {
            cy.restoreLocalStorage("data-job-explore-executions");

            DataJobBasePO.wireUserSession();
            DataJobBasePO.initInterceptors();
        });

        it(`Data Job Explore Executions Page - should open Details and verify Executions tab is not displayed`, () => {
            cy.log("Fixture for name: " + testJobsFixture[0].job_name);

            const dataJobsExplorePage = DataJobsExplorePage.navigateTo();

            dataJobsExplorePage.openJobDetails(
                testJobsFixture[0].team,
                testJobsFixture[0].job_name,
            );

            const dataJobDetailsBasePage = DataJobDetailsBasePO.getPage();

            dataJobDetailsBasePage
                .getMainTitle()
                .scrollIntoView()
                .should("be.visible")
                .should("contains.text", testJobsFixture[0].job_name);

            dataJobDetailsBasePage
                .getDetailsTab()
                .should("have.class", "active");

            dataJobDetailsBasePage.getExecutionsTab().should("not.exist");
        });

        it("Data Job Explore Executions Page - should verify on URL navigate to Executions will redirect to Details", () => {
            const dataJobBasePage = DataJobBasePO.navigateToUrl(
                `/explore/data-jobs/${testJobsFixture[0].team}/${testJobsFixture[0].job_name}/executions`,
            );

            dataJobBasePage
                .getMainTitle()
                .scrollIntoView()
                .should("be.visible")
                .should("contains.text", testJobsFixture[0].job_name);

            dataJobBasePage
                .getCurrentUrl()
                .should(
                    "match",
                    new RegExp(
                        `\\/explore\\/data-jobs\\/${testJobsFixture[0].team}\\/${testJobsFixture[0].job_name}\\/details$`,
                    ),
                );

            dataJobBasePage.getDetailsTab().should("have.class", "active");
        });
    },
);
