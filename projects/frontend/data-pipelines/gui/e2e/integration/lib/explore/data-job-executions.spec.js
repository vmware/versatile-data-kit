/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { DataJobsExplorePage } from '../../../support/pages/app/lib/explore/data-jobs.po';
import { DataJobBasePO } from '../../../support/application/data-job-base.po';
import { applyGlobalEnvSettings } from '../../../support/helpers/commands.helpers';

describe(
    'Data Job Explore Executions Page',
    { tags: ['@dataPipelines', '@exploreDataJobExecutions'] },
    () => {
        let testJobs;

        before(() => {
            return DataJobBasePO.recordHarIfSupported()
                .then(() =>
                    cy.clearLocalStorageSnapshot('data-job-explore-executions')
                )
                .then(() => DataJobBasePO.login())
                .then(() => cy.saveLocalStorage('data-job-explore-executions'))
                .then(() => cy.cleanTestJobs())
                .then(() => cy.prepareBaseTestJobs())
                .then(() => cy.fixture('lib/explore/test-jobs.json'))
                .then((loadedTestJobs) => {
                    testJobs = applyGlobalEnvSettings(loadedTestJobs);

                    return cy.wrap({
                        context: 'explore::data-job-executions.spec::before()',
                        action: 'continue'
                    });
                });
        });

        after(() => {
            cy.cleanTestJobs();

            DataJobBasePO.saveHarIfSupported();
        });

        beforeEach(() => {
            cy.restoreLocalStorage('data-job-explore-executions');

            DataJobBasePO.initBackendRequestInterceptor();
        });

        it(`Data Job Explore Executions Page - should open Details and verify Executions tab is not displayed`, () => {
            cy.log('Fixture for name: ' + testJobs[0].job_name);

            const dataJobsExplorePage = DataJobsExplorePage.navigateTo();

            dataJobsExplorePage.openJobDetails(
                testJobs[0].team,
                testJobs[0].job_name
            );

            const dataJobBasePage = DataJobBasePO.getPage();

            dataJobBasePage
                .getMainTitle()
                .should('be.visible')
                .should('contains.text', testJobs[0].job_name);

            dataJobBasePage.getDetailsTab().should('have.class', 'active');

            dataJobBasePage.getExecutionsTab().should('not.exist');
        });

        it('Data Job Explore Executions Page - should verify on URL navigate to Executions will redirect to Details', () => {
            const dataJobBasePage = DataJobBasePO.navigateToUrl(
                `/explore/data-jobs/${testJobs[0].team}/${testJobs[0].job_name}/executions`
            );

            dataJobBasePage
                .getMainTitle()
                .should('be.visible')
                .should('contains.text', testJobs[0].job_name);

            dataJobBasePage
                .getCurrentUrl()
                .should(
                    'match',
                    new RegExp(
                        `\\/explore\\/data-jobs\\/${testJobs[0].team}\\/${testJobs[0].job_name}\\/details$`
                    )
                );

            dataJobBasePage.getDetailsTab().should('have.class', 'active');
        });
    }
);
