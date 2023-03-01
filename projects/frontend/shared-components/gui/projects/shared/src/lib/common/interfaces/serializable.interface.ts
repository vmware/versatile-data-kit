/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import {
	PrimitivesNil,
	PrimitivesNilArrays,
	PrimitivesNilObject
} from '../../utils';

type SerializedType =
	| PrimitivesNil
	| PrimitivesNilArrays
	| PrimitivesNilObject
	| unknown;

/**
 * ** This interface gives boundaries for Objects that we want to be serializable for JSON.
 *
 *
 */
export interface Serializable<T extends SerializedType = SerializedType> {
	/**
	 * ** Implements this method and return data you want to be serialized when JSON.stringify(...) is executed.
	 */
	toJSON(): T;
}
