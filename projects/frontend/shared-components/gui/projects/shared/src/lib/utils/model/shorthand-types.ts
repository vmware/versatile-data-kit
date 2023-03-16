/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/no-explicit-any,@typescript-eslint/ban-types */

import { ArrayElement } from './data-source';

/**
 * ** Iterator function for Object.
 */
export type ObjectIterator<TObject, TResult> = (value: TObject[keyof TObject], key: string, collection: TObject) => TResult;

/**
 * ** Iterator function for Array.
 */
export type ArrayIterator<TCollection, TResult> = (value: TCollection, index: number, collection: TCollection[]) => TResult;

/**
 * ** Mapper function for Array.
 */
export type ArrayMapper<TCollection, TResult> = (value: TCollection, index: number, collection: TCollection[]) => TResult;

/**
 * ** Accepted result from Iterator function.
 */
export type IteratorFnResult = void | number | boolean;

/**
 * ** Predicate function for Object.
 */
export type ObjectPredicateFn<TObject> = (value: TObject[keyof TObject], key?: string, collection?: TObject) => boolean;

/**
 * ** Predicate function for Array.
 */
export type ArrayPredicateFn<TArray extends any[]> = (value: ArrayElement<TArray>, index?: number, collection?: TArray) => boolean;

/**
 * ** Predicate function Generic.
 */
export type PredicateFn<T> = (value: T) => boolean;

/**
 * ** Subtract type from something.
 */
export type Subtract<T, U> = T & Exclude<T, U>;

/**
 * ** Strip readonly from object properties and make them mutable.
 */
export type Mutable<T> = {
    -readonly [P in keyof T]: T[P] extends object ? Mutable<T[P]> : T[P];
};

/**
 * ** Filter public values from Object.
 *
 *      - assign as never values that don't match provided condition
 *      - exclude (omit) specific keys from object
 */
export type FilterValues<TObject, TCondition, KExclude extends keyof any> = {
    [key in keyof Omit<TObject, KExclude>]: Omit<TObject, KExclude>[key] extends TCondition ? key : never;
};

/**
 * ** Filter public values from Object.
 *
 *      - assign as never values that match provided condition
 *      - exclude (omit) specific keys from object
 */
export type FilterValuesNegation<TObject, TCondition, KExclude extends keyof any> = {
    [key in keyof Omit<TObject, KExclude>]: Omit<TObject, KExclude>[key] extends TCondition ? never : key;
};

/**
 * ** Filter public method names from Object.
 *
 *      - returns only names of fields that are methods.
 *      - match Function criteria
 */
export type FilterMethodNames<TClass, KExclude extends keyof any> = FilterValues<TClass, Function, KExclude>[keyof FilterValues<
    TClass,
    Function,
    KExclude
>];

/**
 * ** Filter public property names from Object.
 *
 *      - returns only names of fields that are properties.
 *      - don't match Function criteria
 */
export type FilterPropertyNames<TClass, KExclude extends keyof any> = FilterValuesNegation<
    TClass,
    Function,
    KExclude
>[keyof FilterValuesNegation<TClass, Function, KExclude>];

/**
 * ** Filter public methods from Object.
 *
 *      - returns type of Object where only methods are included as name and corresponding type.
 */
export type FilterMethods<TClass, KExclude extends keyof any = ''> = {
    [key in FilterMethodNames<TClass, KExclude>]: TClass[key];
};

/**
 * ** Filter public properties from Object.
 *
 *      - returns type of Object where only properties are included as name and corresponding type.
 */
export type FilterProperties<TClass, KExclude extends keyof any = ''> = {
    [key in FilterPropertyNames<TClass, KExclude>]: TClass[key];
};
