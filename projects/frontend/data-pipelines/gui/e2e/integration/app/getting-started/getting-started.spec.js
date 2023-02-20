/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />
import { DataPipelinesBasePO } from '../../../support/application/data-pipelines-base.po';
import { GettingStartedPage } from '../../../support/pages/app/getting-started/getting-started.po';
import { DataJobsHealthPanelComponentPO } from '../../../support/pages/app/getting-started/data-jobs-health-panel-component.po';
import { DataJobManageDetailsPage } from '../../../support/pages/app/lib/manage/data-job-details.po';
import { DataJobManageExecutionsPage } from '../../../support/pages/app/lib/manage/data-job-executions.po';
import { applyGlobalEnvSettings } from '../../../support/helpers/commands.helpers';

describe('Getting Started Page', { tags: ['@dataPipelines'] }, () => {
    let testJob;

    before(() => {
        return DataPipelinesBasePO.recordHarIfSupported()
                                  .then(() => cy.clearLocalStorageSnapshot('getting-started'))
                                  .then(() => DataPipelinesBasePO.login())
                                  .then(() => cy.saveLocalStorage('getting-started'))
                                  .then(() => cy.prepareLongLivedFailingTestJob())
                                  .then(() => cy.createExecutionsLongLivedFailingTestJob())
                                  .then(() => cy.fixture('e2e-cy-dp-failing.job.json'))
                                  .then((failingTestJob) => {
                                      testJob = applyGlobalEnvSettings(failingTestJob);

                                      return cy.wrap({ context: 'getting-started.spec::before()', action: 'continue' });
                                  });
    });

    after(() => {
        DataPipelinesBasePO.saveHarIfSupported();
    });

    beforeEach(() => {
        cy.restoreLocalStorage('getting-started');

        DataPipelinesBasePO.initBackendRequestInterceptor();
    });

    it('Main Title Component have text: Get Started with Data Pipelines', () => {
        GettingStartedPage
            .navigateTo()
            .getMainTitle()
            //TODO : Discuss/agree what should be the assertion strategy of the UI Components.
            // Do we assert text directly, or use some other form?
            .should('have.text', 'Get Started with Data Pipelines');
    });

    describe('Data Jobs Health Overview Panel', () => {
        it('Verify Widgets rendered correct data and failing jobs navigates correctly', () => {
            GettingStartedPage
                .navigateTo();

            let dataJobsHealthPanel = DataJobsHealthPanelComponentPO
                .getComponent();
            dataJobsHealthPanel
                .waitForViewToRender();
            dataJobsHealthPanel
                .getDataJobsHealthPanel()
                .scrollIntoView();

            dataJobsHealthPanel
                .getExecutionsSuccessPercentage()
                .should('be.gte', 0)
                .should('be.lte', 100);
            dataJobsHealthPanel
                .getNumberOfFailedExecutions()
                .should('be.gte', 2);
            dataJobsHealthPanel
                .getExecutionsTotal()
                .should('be.gte', 2);

            dataJobsHealthPanel
                .getAllFailingJobs()
                .should('have.length.gte', 1);

            dataJobsHealthPanel
                .getAllMostRecentFailingJobsExecutions()
                .should('have.length.gte', 1);

            // navigate to failing job details
            dataJobsHealthPanel
                .navigateToFailingJobDetails(testJob.job_name);

            const dataJobManageDetailsPage = DataJobManageDetailsPage
                .getPage();
            dataJobManageDetailsPage
                .getMainTitle()
                .should('contain.text', testJob.job_name);
            dataJobManageDetailsPage
                .getDetailsTab()
                .should('be.visible')
                .should('have.class', 'active');
            dataJobManageDetailsPage
                .getExecutionsTab()
                .should('exist')
                .should('not.have.class', 'active');
            dataJobManageDetailsPage
                .showMoreDescription()
                .getDescriptionFull()
                .should('contain.text', testJob.description);
        });

        it('Verify most recent failing executions Widget navigates correctly', () => {
            GettingStartedPage
                .navigateTo();

            let dataJobsHealthPanel = DataJobsHealthPanelComponentPO
                .getComponent();
            dataJobsHealthPanel
                .waitForViewToRender();
            dataJobsHealthPanel
                .getDataJobsHealthPanel()
                .scrollIntoView();

            dataJobsHealthPanel
                .getAllMostRecentFailingJobsExecutions()
                .should('have.length.gte', 1);

            // navigate to most recent failing job executions
            dataJobsHealthPanel
                .navigateToMostRecentFailingJobExecutions(testJob.job_name);

            const dataJobManageExecutionsPage = DataJobManageExecutionsPage
                .getPage();
            dataJobManageExecutionsPage
                .getMainTitle()
                .should('contain.text', testJob.job_name);
            dataJobManageExecutionsPage
                .getDetailsTab()
                .should('be.visible')
                .should('not.have.class', 'active');
            dataJobManageExecutionsPage
                .getExecutionsTab()
                .should('be.visible')
                .should('have.class', 'active');
            dataJobManageExecutionsPage
                .getDataGridRows()
                .should('have.length.gte', 1);
        });
    });
});
