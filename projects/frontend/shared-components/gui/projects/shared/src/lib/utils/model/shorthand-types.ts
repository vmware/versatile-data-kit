

/* eslint-disable @typescript-eslint/no-explicit-any */

import { ArrayElement } from './data-source';

// Iterator function for Object.
export type ObjectIterator<TObject, TResult> = (value: TObject[keyof TObject], key: string, collection: TObject) => TResult;
// Iterator function for Array.
export type ArrayIterator<TCollection, TResult> = (value: TCollection, index: number, collection: TCollection[]) => TResult;
// Mapper function for Array.
export type ArrayMapper<TCollection, TResult> = (value: TCollection, index: number, collection: TCollection[]) => TResult;
// Accepted result from Iterator function.
export type IteratorFnResult = void | number | boolean;

// Predicate function for Object.
export type ObjectPredicateFn<TObject> = (value: TObject[keyof TObject], key?: string, collection?: TObject) => boolean;
// Predicate function for Array.
export type ArrayPredicateFn<TArray extends any[]> = (value: ArrayElement<TArray>, index?: number, collection?: TArray) => boolean;
// Predicate function Generic.
export type PredicateFn<T> = (value: T) => boolean;

// Subtract type from something.
export type Subtract<T, U> = T & Exclude<T, U>;
