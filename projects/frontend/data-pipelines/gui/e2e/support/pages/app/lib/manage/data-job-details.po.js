/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { DataJobDetailsBasePO } from '../../../../application/data-job-details-base.po';

export class DataJobManageDetailsPage extends DataJobDetailsBasePO {
    static getPage() {
        return new DataJobManageDetailsPage();
    }

    static navigateTo(teamName, jobName) {
        return super.navigateTo('manage', teamName, jobName);
    }

    // Deployment methods

    // Acceptable values are "not-deployed", "enabled", "disabled"
    getDeploymentStatus(status) {
        return cy.get('[data-cy=data-pipelines-job-details-status-' + status + ']');
    }

    // Description methods

    getDescription() {
        return cy.get('[data-cy=data-pipelines-data-job-details-description] .form-section-readonly');
    }

    getDescriptionEditButton() {
        return cy.get('[data-cy=data-pipelines-data-job-details-description] .form-section-header > .btn');
    }

    getDescriptionEditTextarea() {
        return cy.get('[data-cy=data-pipelines-data-job-details-description] textarea');
    }

    getDescriptionSaveButton() {
        return cy.get('[data-cy=data-pipelines-data-job-details-description] button:contains(Save)')
    }

    openDescription() {
        this.getDescriptionEditButton()
            .click({ force: true });
    }

    enterDescriptionDetails(description) {
        this.getDescriptionEditTextarea()
            .clear()
            .type(description)
    }

    saveDescription() {
        this.getDescriptionSaveButton()
            .click({ force: true });

        this.waitForBackendRequestCompletion()
    }

    // Schedule methods

    getSchedule() {
        return cy.get('[data-cy=data-pipelines-data-job-details-schedule] .form-section-readonly');
    }

    // Disable/Enable methods

    getStatusEditButton() {
        return cy.get('[data-cy=data-pipelines-data-job-details-status] .form-section-header > .btn')
    }

    getStatusSaveButton() {
        return cy.get('[data-cy=data-pipelines-data-job-details-status] button:contains(Save)');
    }

    changeStatus(currentStatus) {
        const newStatus = currentStatus.trim().toLowerCase() === 'enabled'
            ? 'disable'
            : 'enable';

        return cy.get(`[data-cy=data-pipelines-data-job-details-status-${ newStatus }]`)
                 .should('exist')
                 .check({ force: true });
    }

    toggleJobStatus() {
        cy.get('[data-cy=data-pipelines-job-details-status]')
          .invoke('text')
          .then((jobStatus) => {
              this.getStatusEditButton()
                  .scrollIntoView()
                  .click({ force: true });

              this.changeStatus(jobStatus);

              this.waitForClickThinkingTime();

              this.getStatusSaveButton()
                  .scrollIntoView()
                  .click({ force: true });

              let newStatus = jobStatus === 'Enabled'
                  ? 'Disabled'
                  : 'Enabled';

              this.waitForBackendRequestCompletion();

              this.getToastTitle()
                  .should('exist')
                  .should('contain.text', 'Status update completed');

              this.waitForActionThinkingTime(); // Natural wait for User action

              this.getToastDismiss()
                  .should('exist')
                  .click({ force: true });

              cy.get('[data-cy=data-pipelines-job-details-status]')
                .scrollIntoView()
                .should('have.text', newStatus);
          })
    }
}
