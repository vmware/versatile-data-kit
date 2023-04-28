/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { DataJobBasePO } from '../../../base/data-pipelines/data-job-base.po';

export class DataJobExploreExecutionsPage extends DataJobBasePO {
    /**
     * ** Returns instance of the page object.
     *
     * @returns {DataJobExploreExecutionsPage}
     */
    static getPage() {
        return new DataJobExploreExecutionsPage();
    }

    /**
     * @inheritDoc
     * @param {string} teamName
     * @param {string} jobName
     * @return {DataJobExploreExecutionsPage}
     */
    static navigateTo(teamName, jobName) {
        return super.navigateTo('explore', teamName, jobName, 'executions');
    }
}
