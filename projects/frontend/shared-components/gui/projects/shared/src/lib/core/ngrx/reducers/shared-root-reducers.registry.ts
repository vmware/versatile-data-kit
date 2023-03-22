/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ActionReducerMap } from '@ngrx/store';

import { STORE_COMPONENTS, STORE_ROUTER, StoreState } from '../state';

import { routerReducer } from '../../router/state/reducers';
import { componentReducer } from '../../component/state';

/**
 * ** Root reducers for Shared.
 */
export const SHARED_ROOT_REDUCERS: ActionReducerMap<StoreState> = {
    [STORE_ROUTER]: routerReducer,
    [STORE_COMPONENTS]: componentReducer
};
