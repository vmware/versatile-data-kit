/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { DataJobBasePO } from './data-job-base.po';

export class DataJobDetailsBasePO extends DataJobBasePO {
    /**
     * ** Returns instance of the page object.
     *
     * @returns {DataJobDetailsBasePO}
     */
    static getPage() {
        return new DataJobDetailsBasePO();
    }

    /**
     * ** Navigate to Data Job Url.
     *
     * @param {'explore'|'manage'} context
     * @param {string} teamName
     * @param {string} jobName
     */
    static navigateTo(context, teamName, jobName) {
        return super.navigateTo(context, teamName, jobName, 'details');
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
        this.getShowDescriptionMoreBtn().should('exist').click({ force: true });

        this.waitForViewToRenderShort();

        return this;
    }
}
