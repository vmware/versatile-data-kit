

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { RouterState } from '../../router';
import { LiteralComponentsState } from '../../component';

/**
 * ** Constant for Store Router field.
 */
export const STORE_ROUTER = 'router';

/**
 * ** Constant for Store Components field.
 */
export const STORE_COMPONENTS = 'components';

/**
 * ** Store State interface.
 *
 *
 */
export interface StoreState {
    [STORE_ROUTER]: RouterState;
    [STORE_COMPONENTS]: LiteralComponentsState;
}
