

import { ActionReducerMap } from '@ngrx/store';

import { STORE_COMPONENTS, STORE_ROUTER, StoreState } from '../state';

import { routerReducer } from '../../router/state/reducers';
import { componentReducer } from '../../component/state';

/**
 * ** Root reducers for Shared.
 *
 * @author gorankokin
 */
export const SHARED_ROOT_REDUCERS: ActionReducerMap<StoreState> = {
    [STORE_ROUTER]: routerReducer,
    [STORE_COMPONENTS]: componentReducer
};
