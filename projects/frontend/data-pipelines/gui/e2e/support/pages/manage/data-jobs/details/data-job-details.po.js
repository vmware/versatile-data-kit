/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { DataJobDetailsBasePO } from '../../../base/data-pipelines/data-job-details-base.po';

export class DataJobManageDetailsPage extends DataJobDetailsBasePO {
    /**
     * ** Returns instance of the page object.
     *
     * @returns {DataJobManageDetailsPage}
     */
    static getPage() {
        return new DataJobManageDetailsPage();
    }

    /**
     * @inheritDoc
     * @return {DataJobManageDetailsPage}
     */
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
        return cy.get('[data-cy=data-pipelines-data-job-details-description] button:contains(Save)');
    }

    openDescription() {
        this.getDescriptionEditButton().click({ force: true });
    }

    enterDescriptionDetails(description) {
        this.getDescriptionEditTextarea().clear().type(description);
    }

    saveDescription() {
        this.getDescriptionSaveButton().click({ force: true });

        this.waitForDataJobPutReqInterceptor();
    }

    /**
     * ** Format ISO DateTime to Data job executions timeline format.
     *
     *  <b>e.g.</b>
     *      '2023-03-27T10:25:24.960717Z' -> 'Mar 27, 2023, 10:25 AM UTC'
     *
     * @param {string} isoDate
     */
    formatDateTimeFromISOToExecutionsTimeline(isoDate) {
        const dateTimeChunks = isoDate.replace(/(\..*)?Z$/, '').split('T');
        const dateChunk = dateTimeChunks[0];
        const timeChunk = dateTimeChunks[1];

        return `${this._formatDateFromISOToExecutionsTimeline(dateChunk)}, ${this._formatTimeFromISOToExecutionsTimeline(timeChunk)} UTC`;
    }

    // Schedule methods

    getSchedule() {
        return cy.get('[data-cy=data-pipelines-data-job-details-schedule] .form-section-readonly');
    }

    // Disable/Enable methods

    getStatusEditButton() {
        return cy.get('[data-cy=data-pipelines-data-job-details-status] .form-section-header > .btn');
    }

    getStatusSaveButton() {
        return cy.get('[data-cy=data-pipelines-data-job-details-status] button:contains(Save)');
    }

    // Executions Timeline

    getExecutionsSteps() {
        return cy.get('.clr-timeline-step');
    }

    getExecutionStepStartedTile(stepSelector) {
        return cy.get(stepSelector).should('exist').scrollIntoView().find('[data-cy=data-pipelines-executions-timeline-started]').invoke('attr', 'title');
    }

    getExecutionStepEndedTile(stepSelector) {
        return cy.get(stepSelector).should('exist').find('[data-cy=data-pipelines-executions-timeline-ended]').invoke('attr', 'title');
    }

    getExecutionStepManualTriggerer(stepSelector) {
        return cy.get(stepSelector).find('[data-cy=data-pipelines-executions-timeline-manual-start]');
    }

    getExecutionStepStatusIcon(stepSelector, status) {
        const STATUS_ICON_MAP = {};
        STATUS_ICON_MAP['SUBMITTED'] = 'hourglass';
        STATUS_ICON_MAP['RUNNING'] = 'play';
        STATUS_ICON_MAP['SUCCEEDED'] = 'success-standard';
        STATUS_ICON_MAP['CANCELLED'] = 'times-circle';
        STATUS_ICON_MAP['SKIPPED'] = 'circle-arrow';
        STATUS_ICON_MAP['USER_ERROR'] = 'error-standard';
        STATUS_ICON_MAP['PLATFORM_ERROR'] = 'error-standard';

        if (status === 'RUNNING') {
            return cy.get(stepSelector).find(`clr-spinner[aria-label='In progress']`);
        }

        return cy.get(stepSelector).find(`[shape=${STATUS_ICON_MAP[status]}]`);
    }

    // Actions

    changeStatus(currentStatus) {
        const newStatus = currentStatus.trim().toLowerCase() === 'enabled' ? 'disable' : 'enable';

        return cy.get(`[data-cy=data-pipelines-data-job-details-status-${newStatus}]`).should('exist').check({ force: true });
    }

    toggleJobStatus() {
        cy.get('[data-cy=data-pipelines-job-details-status]')
            .invoke('text')
            .then((jobStatus) => {
                this.getStatusEditButton().scrollIntoView().click({ force: true });

                this.changeStatus(jobStatus);

                this.waitForClickThinkingTime();

                this.getStatusSaveButton().scrollIntoView().click({ force: true });

                let newStatus = jobStatus === 'Enabled' ? 'Disabled' : 'Enabled';

                this.waitForDataJobDeploymentPatchReqInterceptor();

                this.getToastTitle().should('exist').should('contain.text', 'Status update completed');

                this.waitForActionThinkingTime(); // Natural wait for User action

                this.getToastDismiss().should('exist').click({ force: true });

                cy.get('[data-cy=data-pipelines-job-details-status]').scrollIntoView().should('have.text', newStatus);
            });
    }

    /**
     * ** Format Date chunk to Data job Executions timeline format.
     *
     *  <b>e.g.</b>
     *      '2023-03-27' -> 'Mar 27, 2023'
     *
     * @param {string} dateChunk
     * @return {string}
     * @private
     */
    _formatDateFromISOToExecutionsTimeline(dateChunk) {
        if (!dateChunk) {
            return '';
        }

        const dateChunks = dateChunk.split('-');
        const year = dateChunks[0];
        const month = dateChunks[1];
        const day = parseInt(dateChunks[2], 10);

        const dayMonth = `${day}, ${year}`;

        let monthAbbreviation;

        switch (month) {
            case '01':
                monthAbbreviation = 'Jan';
                break;
            case '02':
                monthAbbreviation = 'Feb';
                break;
            case '03':
                monthAbbreviation = 'Mar';
                break;
            case '04':
                monthAbbreviation = 'Apr';
                break;
            case '05':
                monthAbbreviation = 'May';
                break;
            case '06':
                monthAbbreviation = 'Jun';
                break;
            case '07':
                monthAbbreviation = 'Jul';
                break;
            case '08':
                monthAbbreviation = 'Aug';
                break;
            case '09':
                monthAbbreviation = 'Sep';
                break;
            case '10':
                monthAbbreviation = 'Oct';
                break;
            case '11':
                monthAbbreviation = 'Nov';
                break;
            case '12':
                monthAbbreviation = 'Dec';
                break;
            default:
                monthAbbreviation = '';
        }

        return `${monthAbbreviation} ${dayMonth}`;
    }

    /**
     * ** Format Time chunk to Data job Executions timeline format.
     *
     *  <b>e.g.</b>
     *      '10:25:24' -> '10:25 AM'
     *
     * @param {string} timeChunk
     * @return {string}
     * @private
     */
    _formatTimeFromISOToExecutionsTimeline(timeChunk) {
        if (!timeChunk) {
            return '';
        }

        const timeChunks = timeChunk.split(':');
        const hour = parseInt(timeChunks[0], 10);
        const minute = parseInt(timeChunks[1], 10);
        const beforeOrAfter = hour >= 12 ? 'PM' : 'AM';
        const hourNormalizedTo12Hours = hour > 12 ? hour % 12 : hour === 0 ? 12 : hour;
        const hourNormalizedToString = hourNormalizedTo12Hours < 10 ? `0${hourNormalizedTo12Hours}` : `${hourNormalizedTo12Hours}`;
        const minuteNormalizedToString = minute < 10 ? `0${minute}` : `${minute}`;

        return `${hourNormalizedToString}:${minuteNormalizedToString} ${beforeOrAfter}`;
    }
}
