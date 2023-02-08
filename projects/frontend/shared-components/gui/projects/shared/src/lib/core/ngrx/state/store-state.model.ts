

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
 * @author gorankokin
 */
export interface StoreState {
    [STORE_ROUTER]: RouterState;
    [STORE_COMPONENTS]: LiteralComponentsState;
}
