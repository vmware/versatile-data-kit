/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { DataJobDetailsBasePO } from '../../../../application/data-job-details-base.po';

export class DataJobExploreDetailsPage extends DataJobDetailsBasePO {
    static getPage() {
        return new DataJobExploreDetailsPage();
    }

    static navigateTo(teamName, jobName) {
        return super.navigateTo('explore', teamName, jobName);
    }
}
