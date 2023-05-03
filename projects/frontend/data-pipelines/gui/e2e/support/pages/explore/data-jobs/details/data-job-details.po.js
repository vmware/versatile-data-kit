/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { DataJobDetailsBasePO } from '../../../base/data-pipelines/data-job-details-base.po';

export class DataJobExploreDetailsPage extends DataJobDetailsBasePO {
    /**
     * ** Returns instance of the page object.
     *
     * @returns {DataJobExploreDetailsPage}
     */
    static getPage() {
        return new DataJobExploreDetailsPage();
    }

    /**
     * @inheritDoc
     * @param {string} teamName
     * @param {string} jobName
     * @return {DataJobExploreDetailsPage}
     */
    static navigateTo(teamName, jobName) {
        return super.navigateTo('explore', teamName, jobName);
    }
}
