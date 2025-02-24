/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/no-explicit-any */

import { Type } from '@angular/core';

import { Observable } from 'rxjs';

import { DisplayMode } from './grid-config.model';

export const MISSING_DEFAULT_TEAM_MESSAGE = 'The defaultOwnerTeamName property need to be set for the DATA_PIPELINES_CONFIGS';

export const RESERVED_DEFAULT_TEAM_NAME_MESSAGE = `The 'default' value is reserved, and can not be used for defaultOwnerTeamName property`;

/**
 * ** Configuration map for Data Pipelines library.
 */
export interface DataPipelinesConfig {
    resourceServer?: {
        getUrl?: () => string;
    };

    defaultOwnerTeamName: string;
    ownerTeamNamesObservable?: Observable<string[]>;
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

    // health status url configured by a segment after hostname, including slash with {0} for the id param,
    healthStatusUrl?: string; // eg: /dev-center/health-status?dataJob={0}

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
        confirmationMessageComponent: Type<any>;
    };

    /**
     * ** Reference to Explore Data Job(s) configuration map.
     */
    exploreConfig?: ExploreConfig;
    /**
     ** Reference to Manage Data Job(s) configuration map.
     */
    manageConfig?: ManageConfig;

    /**
     * ** Integration providers from Host application.
     */
    integrationProviders?: {
        /**
         * ** Users related.
         */
        users?: {
            /**
             * ** Get logged User email.
             */
            getEmail?: () => string;
            /**
             * ** Get logged User username.
             */
            getUsername?: () => string;
        };
        /**
         * ** Teams related.
         */
        teams?: {
            /**
             * ** Ensure User membership in early access program identified by its name.
             */
            ensureMembershipEarlyAccessProgram?: (key: string) => boolean;
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
