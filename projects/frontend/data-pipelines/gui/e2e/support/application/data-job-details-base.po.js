/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { DataJobBasePO } from './data-job-base.po';

export class DataJobDetailsBasePO extends DataJobBasePO {
    static getPage() {
        return new DataJobDetailsBasePO();
    }

    static navigateTo(context, teamName, jobName) {
        return this.navigateToUrl(`/${ context }/data-jobs/${ teamName }/${ jobName }`);
    }

    // Selectors

    getStatusField() {
        return cy.get('[data-cy=data-pipelines-job-details-status]');
    }

    getDescriptionField() {
        return cy.get('[data-cy=data-pipelines-job-details-description]');
    }

    getDescriptionFull() {
        return cy.get('[data-cy=description-show-less]');
    }

    getShowDescriptionMoreBtn() {
        return cy.get('[data-cy=description-show-more]');
    }

    getTeamField() {
        return cy.get('[data-cy=data-pipelines-job-details-team]');
    }

    getScheduleField() {
        return cy.get('[data-cy=data-pipelines-job-details-schedule]');
    }

    getSourceField() {
        return cy.get('[data-cy=data-pipelines-job-details-source]');
    }

    getOnDeployedField() {
        return cy.get('[data-cy=data-pipelines-job-details-on-deployed]');
    }

    getOnPlatformErrorField() {
        return cy.get('[data-cy=data-pipelines-job-details-on-platform-error]');
    }

    getOnUserErrorField() {
        return cy.get('[data-cy=data-pipelines-job-details-on-user-error]');
    }

    getOnSuccessField() {
        return cy.get('[data-cy=data-pipelines-job-details-on-success]');
    }

    // Actions

    showMoreDescription() {
        this.getShowDescriptionMoreBtn()
            .should('exist')
            .click({ force: true });

        this.waitForViewToRenderShort();

        return this;
    }
}
