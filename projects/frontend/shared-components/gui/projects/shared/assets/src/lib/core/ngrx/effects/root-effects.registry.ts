

import { Type } from '@angular/core';

import { RouterEffects } from '../../router/state/effects';

/**
 * ** Registry for Root Effects.
 *
 * @author gorankokin
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const SHARED_ROOT_EFFECTS: Array<Type<any>> = [
    RouterEffects
];
