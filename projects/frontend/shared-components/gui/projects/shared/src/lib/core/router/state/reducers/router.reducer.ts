

/* eslint-disable arrow-body-style,prefer-arrow/prefer-arrow-functions */

import {
    ROUTER_CANCEL,
    ROUTER_ERROR,
    ROUTER_NAVIGATION,
    RouterCancelAction,
    RouterErrorAction,
    RouterNavigationAction
} from '@ngrx/router-store';

import { RouterState, RouteState } from '../../model';

type AcceptedActions = RouterNavigationAction<RouteState> |
    RouterErrorAction<RouterState, RouteState> |
    RouterCancelAction<RouterState, RouteState>;

/**
 * ** Reducer for Router Actions.
 *
 * @author gorankokin
 */
export function routerReducer(
    state = RouterState.empty(),
    action: AcceptedActions = { type: null, payload: null }) {

    const actionPayload = action.payload;

    switch (action.type) {
        case ROUTER_NAVIGATION:
        case ROUTER_ERROR:
        case ROUTER_CANCEL:
            const newState = RouterState.of(actionPayload.routerState, actionPayload.event.id);
            newState.appendPrevious(state);

            return newState;
        default:
            return state;
    }
}
