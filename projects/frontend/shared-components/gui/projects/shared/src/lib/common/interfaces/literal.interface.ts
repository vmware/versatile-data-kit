/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { PrimitivesNil, PrimitivesNilArrays, PrimitivesNilObject } from '../../utils';

type SerializedType = PrimitivesNil | PrimitivesNilArrays | PrimitivesNilObject | unknown;

/**
 * ** This interface gives boundaries for Class instances to get converted into Literals.
 */
export interface Literal<T extends SerializedType = SerializedType> {
    /**
     * ** Implements this method and return data you want to be serialized into Literals.
     */
    toLiteral(): T;

    /**
     * ** Implements this method and return data you want to be serialized into Literals.
     * <p>
     *     - Data should be deep clone before return, to comply with immutability.
     * </p>
     */
    toLiteralCloneDeep(): T;
}
