/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import {
    ArrayElement,
    TaurusNavigateAction,
    TaurusRouteData,
    TaurusRouteNavigateBackData,
    TaurusRouteNavigateToData,
    TaurusRoutes,
} from '@vdk/shared';

export interface DataPipelinesRestoreUI {
    /**
     * ** Restore when this condition is met, previous ConfigPath equals to provided.
     */
    previousConfigPathLike: string;
}

/**
 * ** Data pipelines Route data.
 */
export interface DataPipelinesRouteData
    extends TaurusRouteNavigateToData,
        TaurusRouteNavigateBackData {
    /**
     * ** Field that has pointer to paramKey for Team in Route config.
     */
    teamParamKey?: string;

    /**
     * ** Field that has pointer to paramKey for Job in Route config.
     */
    jobParamKey?: string;

    /**
     * ** Field flag that enable/disable Listener for Team Change and on Change to do some action.
     */
    activateListenerForTeamChange?: boolean;

    /**
     * ** Field flag that enable/disable subpage navigation.
     *
     *      - true - enables subpage navigation
     *      - false - disable subpage navigation and activate default root Page navigation.
     */
    activateSubpageNavigation?: boolean;

    /**
     * @inheritDoc
     */
    navigateTo?: TaurusNavigateAction<string | '$.team' | '$.job'>;

    /**
     * @inheritDoc
     */
    navigateBack?: TaurusNavigateAction<string | '$.team'>;

    /**
     * ** Field that instruct Component when should restore UI.
     */
    restoreUiWhen?: DataPipelinesRestoreUI;

    /**
     * ** Configuring this field, instruct Component on this Route to be in editable mode or no.
     *
     *      - true  -> Component is in editable mode.
     *      - false -> Component is in readonly mode.
     */
    editable?: boolean;
}

/**
 * ** Data pipelines Route config.
 */
export type DataPipelinesRoute = ArrayElement<DataPipelinesRoutes>;

/**
 * ** Data pipelines Routes configs.
 */
export type DataPipelinesRoutes = TaurusRoutes<
    TaurusRouteData<DataPipelinesRouteData>
>;
