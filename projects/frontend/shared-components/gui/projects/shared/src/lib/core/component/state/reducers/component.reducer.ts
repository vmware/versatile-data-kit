

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable arrow-body-style,prefer-arrow/prefer-arrow-functions */

import { ROUTER_NAVIGATION, RouterNavigationAction } from '@ngrx/router-store';

import { CollectionsUtil } from '../../../../utils';

import { NavigationActions, RouteSegments, RouteState } from '../../../router';

import { ComponentsStateHelper, ComponentState, FAILED, IDLE, INITIALIZED, LiteralComponentState, LOADED, LOADING } from '../../model';

import {
    COMPONENT_CLEAR_DATA,
    COMPONENT_FAILED,
    COMPONENT_IDLE,
    COMPONENT_INIT,
    COMPONENT_LOADED,
    COMPONENT_LOADING,
    COMPONENT_UPDATE,
    ComponentActions,
    ComponentClearData,
    ComponentIdle,
    ComponentInit,
    ComponentLoaded,
    ComponentLoading,
    ComponentUpdate
} from '../actions';

const stateHelper = new ComponentsStateHelper();

/**
 * ** Reducer for Components Actions.
 *
 *
 */
export function componentReducer(
    state = stateHelper.getState(),
    action: ComponentActions | NavigationActions = { type: null, payload: null }) {

    let actionComponentState: ComponentState;
    let actionLiteralComponentState: LiteralComponentState;
    let storeLiteralComponentState: LiteralComponentState;

    stateHelper.setState(state);

    switch (action.type) {
        case COMPONENT_INIT:
            actionComponentState = (action as ComponentInit).payload;

            stateHelper.updateLiteralComponentState({
                ...actionComponentState.toLiteralDeepClone(),
                status: INITIALIZED
            });

            return stateHelper.getState();
        case COMPONENT_IDLE:
        case COMPONENT_LOADING:
            actionComponentState = (action as ComponentIdle | ComponentLoading).payload;
            storeLiteralComponentState = stateHelper
                .getLiteralComponentState(actionComponentState.id, actionComponentState.routePathSegments);

            actionLiteralComponentState = actionComponentState.toLiteralDeepClone();

            stateHelper.updateLiteralComponentState({
                ...storeLiteralComponentState,
                ...actionLiteralComponentState,
                status: action instanceof ComponentIdle
                    ? IDLE
                    : LOADING
            });

            return stateHelper.getState();
        case COMPONENT_UPDATE:
        case COMPONENT_LOADED:
            actionComponentState = (action as (ComponentLoaded | ComponentUpdate)).payload;
            storeLiteralComponentState = stateHelper
                .getLiteralComponentState(actionComponentState.id, actionComponentState.routePathSegments);

            actionLiteralComponentState = actionComponentState.toLiteralDeepClone();

            stateHelper.updateLiteralComponentState({
                ...storeLiteralComponentState,
                ...actionLiteralComponentState,
                status: action instanceof ComponentLoaded
                    ? LOADED
                    : actionComponentState.status,
                data: getComponentStateData(actionLiteralComponentState, storeLiteralComponentState)
            });

            return stateHelper.getState();
        case COMPONENT_FAILED:
            actionComponentState = (action as (ComponentLoaded | ComponentUpdate)).payload;
            storeLiteralComponentState = stateHelper
                .getLiteralComponentState(actionComponentState.id, actionComponentState.routePathSegments);

            actionLiteralComponentState = actionComponentState.toLiteralDeepClone();

            stateHelper.updateLiteralComponentState({
                ...storeLiteralComponentState,
                ...actionLiteralComponentState,
                data: getComponentStateData(actionLiteralComponentState, storeLiteralComponentState),
                status: FAILED
            });

            return stateHelper.getState();
        case COMPONENT_CLEAR_DATA:
            actionComponentState = (action as ComponentClearData).payload;
            storeLiteralComponentState = stateHelper.getLiteralComponentState(
                actionComponentState.id,
                actionComponentState.routePathSegments);

            stateHelper.updateLiteralComponentState({
                ...storeLiteralComponentState,
                ...actionComponentState.toLiteralDeepClone(),
                data: {},
                status: LOADING
            });

            return stateHelper.getState();
        case ROUTER_NAVIGATION:
            const routeSegments = (action as RouterNavigationAction<RouteState>).payload.routerState.routeSegments;

            if (!(routeSegments instanceof RouteSegments)) {
                return state;
            }

            stateHelper.resetComponentStates(routeSegments.routePathSegments);

            return stateHelper.getState();
        default:
            return state;
    }
}

const getComponentStateData = (
    actionComponentState: LiteralComponentState,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    storeLiteralComponentState: LiteralComponentState): { [key: string]: any } => {

    if (CollectionsUtil.isLiteralObjectWithProperties(actionComponentState.data)) {
        return actionComponentState.data;
    }

    if (CollectionsUtil.isDefined(storeLiteralComponentState)) {
        return storeLiteralComponentState.data;
    }

    return {};
};
