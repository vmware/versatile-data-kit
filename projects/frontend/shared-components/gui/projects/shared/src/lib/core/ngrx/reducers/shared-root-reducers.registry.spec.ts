/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { routerReducer } from '../../router/state/reducers';

import { componentReducer } from '../../component';

import { STORE_COMPONENTS, STORE_ROUTER } from '../state';

import { SHARED_ROOT_REDUCERS } from './shared-root-reducers.registry';

describe('SHARED_ROOT_REDUCERS', () => {
    it('should verify root reducers are registered', () => {
        // Then
        expect(SHARED_ROOT_REDUCERS).toEqual({
            [STORE_ROUTER]: routerReducer,
            [STORE_COMPONENTS]: componentReducer
        });
    });
});
