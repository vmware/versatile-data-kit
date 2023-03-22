/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { TEAM_NAME_DP_DATA_JOB_FAILING } from "../../../support/helpers/constants.support";

import { DataPipelinesBasePO } from "../../../support/application/data-pipelines-base.po";
import { GettingStartedPage } from "../../../support/pages/app/getting-started/getting-started.po";
import { DataJobsHealthPanelComponentPO } from "../../../support/pages/app/getting-started/data-jobs-health-panel-component.po";
import { DataJobManageDetailsPage } from "../../../support/pages/app/lib/manage/data-job-details.po";
import { DataJobManageExecutionsPage } from "../../../support/pages/app/lib/manage/data-job-executions.po";

describe("Getting Started Page", { tags: ["@dataPipelines"] }, () => {
    /**
     * @type {{name: string; description: string; users: Array<{id: string; description: string}>; lakeNamespaces: Array<string>; collectors:Array<string>}}
     */
    let testJob;

    before(() => {
        return DataPipelinesBasePO.recordHarIfSupported()
            .then(() => cy.clearLocalStorageSnapshot("getting-started"))
            .then(() => DataPipelinesBasePO.login())
            .then(() => cy.saveLocalStorage("getting-started"))
            .then(() => DataPipelinesBasePO.createTeam())
            .then(() => DataPipelinesBasePO.createLongLivedJobs("failing"))
            .then(() =>
                DataPipelinesBasePO.provideExecutionsForLongLivedJobs(
                    "failing",
                ),
            )
            .then(() => {
                return DataPipelinesBasePO.loadLongLivedFailingJobFixture().then(
                    (jobFixture) => {
                        testJob = jobFixture;

                        return cy.wrap({
                            context: "getting-started.spec::before()",
                            action: "continue",
                        });
                    },
                );
            });
    });

    after(() => {
        DataPipelinesBasePO.saveHarIfSupported();
    });

    beforeEach(() => {
        cy.restoreLocalStorage("getting-started");

        DataPipelinesBasePO.wireUserSession();
        DataPipelinesBasePO.initInterceptors();
    });

    it("Main Title Component have text: Get Started with Data Pipelines", () => {
        GettingStartedPage.navigateTo()
            .getMainTitle()
            .should(($el) =>
                expect($el.text().trim()).to.equal(
                    "Get Started with Data Pipelines",
                ),
            );
    });

    describe("Data Jobs Health Overview Panel", () => {
        it("Verify Widgets rendered correct data and failing jobs navigates correctly", () => {
            GettingStartedPage.navigateTo();

            let dataJobsHealthPanel =
                DataJobsHealthPanelComponentPO.getComponent();
            dataJobsHealthPanel.waitForViewToRender();
            dataJobsHealthPanel.getDataJobsHealthPanel().scrollIntoView();

            dataJobsHealthPanel
                .getExecutionsSuccessPercentage()
                .should("be.gte", 0)
                .should("be.lte", 100);
            dataJobsHealthPanel
                .getNumberOfFailedExecutions()
                .should("be.gte", 2);
            dataJobsHealthPanel.getExecutionsTotal().should("be.gte", 2);

            dataJobsHealthPanel
                .getAllFailingJobs()
                .should("have.length.gte", 1);

            dataJobsHealthPanel
                .getAllMostRecentFailingJobsExecutions()
                .should("have.length.gte", 1);

            // navigate to failing job details
            dataJobsHealthPanel.navigateToFailingJobDetails(
                TEAM_NAME_DP_DATA_JOB_FAILING,
            );

            const dataJobManageDetailsPage = DataJobManageDetailsPage.getPage();
            dataJobManageDetailsPage
                .getMainTitle()
                .should("contain.text", TEAM_NAME_DP_DATA_JOB_FAILING);
            dataJobManageDetailsPage
                .getDetailsTab()
                .should("be.visible")
                .should("have.class", "active");
            dataJobManageDetailsPage
                .getExecutionsTab()
                .should("exist")
                .should("not.have.class", "active");
            dataJobManageDetailsPage
                .getLineageTab()
                .should("be.visible")
                .should("not.have.class", "active");
            dataJobManageDetailsPage
                .showMoreDescription()
                .getDescriptionFull()
                .should("contain.text", testJob.description);
        });

        it("Verify most recent failing executions Widget navigates correctly", () => {
            GettingStartedPage.navigateTo();

            let dataJobsHealthPanel =
                DataJobsHealthPanelComponentPO.getComponent();
            dataJobsHealthPanel.waitForViewToRender();
            dataJobsHealthPanel.getDataJobsHealthPanel().scrollIntoView();

            dataJobsHealthPanel
                .getAllMostRecentFailingJobsExecutions()
                .should("have.length.gte", 1);

            // navigate to most recent failing job executions
            dataJobsHealthPanel.navigateToMostRecentFailingJobExecutions(
                TEAM_NAME_DP_DATA_JOB_FAILING,
            );

            const dataJobManageExecutionsPage =
                DataJobManageExecutionsPage.getPage();
            dataJobManageExecutionsPage
                .getMainTitle()
                .should("contain.text", TEAM_NAME_DP_DATA_JOB_FAILING);
            dataJobManageExecutionsPage
                .getDetailsTab()
                .should("be.visible")
                .should("not.have.class", "active");
            dataJobManageExecutionsPage
                .getExecutionsTab()
                .should("be.visible")
                .should("have.class", "active");
            dataJobManageExecutionsPage
                .getLineageTab()
                .should("be.visible")
                .should("not.have.class", "active");
            dataJobManageExecutionsPage
                .getDataGridRows()
                .should("have.length.gte", 1);
        });
    });
});
