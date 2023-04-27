/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Type } from '@angular/core';

import { Observable } from 'rxjs';

import { DisplayMode } from './grid-config.model';

/**
 * ** Configuration map for Data Pipelines library.
 */
export interface DataPipelinesConfig {
    defaultOwnerTeamName: string;
    ownerTeamNamesObservable?: Observable<string[]>;
    /**
     * ** Reference to Explore Data Job(s) configuration map.
     */
    exploreConfig?: ExploreConfig;
    /**
     ** Reference to Manage Data Job(s) configuration map.
     */
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
    /**
     * ** Documentation url for Data Pipelines.
     */
    dataPipelinesDocumentationUrl?: string;
    /**
     * ** Data Job change history configuration.
     */
    changeHistory?: {
        /**
         * ** Url template to external/internal system.
         */
        urlTemplate: string;
        /**
         * ** Confirmation title if url template is to external system.
         */
        confirmationTitle: string;
        /**
         * ** Confirmation message component if url template is to external system.
         */
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        confirmationMessageComponent: Type<any>;
    };
    /**
     * ** Integration providers from Host application.
     */
    integrationProviders?: {
        /**
         * ** Users related.
         */
        users: {
            /**
             * ** Get logged User email.
             */
            getEmail: () => string;
            /**
             * ** Get logged User username.
             */
            getUsername: () => string;
        };
        /**
         * ** Teams related.
         */
        teams?: {
            /**
             * ** Ensure User membership in early access program identified by its name.
             */
            ensureMembershipEarlyAccessProgram: (key: string) => boolean;
        };
    };
}

/**
 * ** Configuration map for Explore Data Job(s).
 */
export interface ExploreConfig {
    /**
     * ** Shot Teams column in Explore Data Jobs list.
     */
    showTeamsColumn?: boolean;
    /**
     * ** Show Teams section in Explore Data Job details.
     */
    showTeamSectionInJobDetails?: boolean;
    /**
     * ** Show Change history section in Explore Data Job details.
     */
    showChangeHistorySectionInJobDetails?: boolean;
}

/**
 * ** Configuration map for Manage Data Job(s).
 */
export interface ManageConfig {
    /**
     * ** Shot Teams column in Manage Data Jobs list.
     */
    showTeamsColumn?: boolean;
    /**
     * ** Show Teams section in Manage Data Job details.
     */
    showTeamSectionInJobDetails?: boolean;
    /**
     * ** Show Change history section in Manage Data Job details.
     */
    showChangeHistorySectionInJobDetails?: boolean;
    selectedTeamNameObservable?: Observable<string>;
    filterByTeamName?: boolean;
    displayMode?: DisplayMode;
    /**
     * ** Allow keytab download in Manage Data Job details.
     */
    allowKeyTabDownloads?: boolean;
}
