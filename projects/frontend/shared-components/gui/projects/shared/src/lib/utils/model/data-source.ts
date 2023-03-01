/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/no-explicit-any */

// Represent union of null and undefined.
export type Nil = null | undefined;
// Represent union of string, number or boolean.
export type Primitives = string | number | boolean;
// Represent union of Primitives and Date.
export type PrimitivesDate = Primitives | Date;
// Represent union of Primitives and Nil.
export type PrimitivesNil = Primitives | Nil;

// Represent Literal object.
export type LiteralObject<T = unknown> = { [p: string]: T };
// Represent union of Literal object and null.
export type LiteralObjectOrNull = LiteralObject | null;
// Represent union of Literal object and null.
export type LiteralObjectNull = LiteralObject | null;
// Represent union of Primitives, Nil and Arrays of them.
export type PrimitivesNilArrays = PrimitivesNil | PrimitivesNil[];
// Represent union of Primitives, Nil and Literal objects of them.
export type PrimitivesNilObject = PrimitivesNil | LiteralObject<PrimitivesNil>;

// Represent union of LiteralObject, Array, Map, WeakMap and Set.
export type Collections<T = unknown> =
	| LiteralObject
	| T[]
	| Map<any, T>
	| WeakMap<any, T>
	| Set<T>
	| { [key: string]: T };

// Extracts element from Array and its type.
export type ArrayElement<ArrayType extends ArrayLike<any>> = ArrayType[number];

/**
 * The state of a DataSource.
 */
export interface DataSource<T = DataSource<any>> {
	/**
	 * ** Map of DataSource.
	 *
	 *     - Each DataSource can be either a primitive, null or undefined, other DataSource or array of DataSources.
	 */
	readonly [key: string]:
		| PrimitivesNilArrays
		| DataSource<T>
		| Array<DataSource<T>>
		| T;
}
