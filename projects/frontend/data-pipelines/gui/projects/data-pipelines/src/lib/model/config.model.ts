/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Observable } from 'rxjs';

import { DisplayMode } from './grid-config.model';

export interface DataPipelinesConfig {
    defaultOwnerTeamName: string;
    ownerTeamNamesObservable?: Observable<string[]>;
    exploreConfig?: ExploreConfig;
    manageConfig?: ManageConfig;
    // health status url configured by a segment after hostname, including slash with {0} for the id param,
    healthStatusUrl?: string; // eg: /dev-center/health-status?dataJob={0}
    /**
     * @deprecated
     */
    showLogsInsightUrl?: boolean;
    /**
     * @deprecated
     */
    showExecutionsPage?: boolean;

    /**
     * ** Flag instruction to show or hide tab for lineage page.
     */
    showLineagePage?: boolean;
}

export interface ExploreConfig {
    showTeamsColumn?: boolean;
}

export interface ManageConfig {
    selectedTeamNameObservable?: Observable<string>;
    filterByTeamName?: boolean;
    displayMode?: DisplayMode;
    allowKeyTabDownloads?: boolean;
    showTeamsColumn?: boolean;
    ensureMembershipEarlyAccessProgram?: (key: string) => boolean;
}
