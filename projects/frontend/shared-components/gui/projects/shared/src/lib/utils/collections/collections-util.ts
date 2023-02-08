

/* eslint-disable @typescript-eslint/no-explicit-any */

import { cloneDeep, isEqual } from 'lodash';

import { Replacer } from '../../common';

import { Collections, IteratorFnResult, LiteralObjectOrNull, Nil, ObjectIterator, Primitives, PrimitivesDate, Subtract } from '../model';

/**
 * ** Utility Class for Collections.
 */
export class CollectionsUtil {
    /**
     * ** Check if value is of type undefined.
     */
    static isUndefined(value: any): value is undefined {
        return typeof value === 'undefined';
    }

    /**
     * ** Check if value has value null.
     */
    static isNull(value: any): value is null {
        return value === null;
    }

    /**
     * ** Check if value is undefined or null.
     */
    static isNil(value: any): value is Nil {
        return CollectionsUtil.isNull(value) || CollectionsUtil.isUndefined(value);
    }

    /**
     * ** Check if value is defined (opposite of isNil).
     *
     *     - Not null.
     *     - Not undefined.
     */
    static isDefined<T>(value: T): boolean {
        return !CollectionsUtil.isNull(value) && !CollectionsUtil.isUndefined(value);
    }

    /**
     * ** Check if value T is of type Number.
     */
    static isNumber<T extends number>(num: T | any): num is number {
        return typeof num === 'number';
    }

    /**
     * ** Check if value T is of type String.
     */
    static isString<T extends string>(str: T | any): str is string {
        return typeof str === 'string';
    }

    /**
     * ** Check if value T is of type Boolean.
     */
    static isBoolean<T extends boolean>(bool: T | any): bool is boolean {
        return typeof bool === 'boolean';
    }

    /**
     * ** Check if value is Primitive.
     *
     *     - String, Number, Boolean, null or undefined.
     */
    static isPrimitive(value: any): value is (Primitives | Nil) {
        return CollectionsUtil.isString(value) ||
            CollectionsUtil.isBoolean(value) ||
            CollectionsUtil.isNumber(value) ||
            CollectionsUtil.isUndefined(value);
    }

    /**
     * ** Check if value is NaN.
     */
    static isNaN<T extends number>(value: T | any): boolean {
        return Number.isNaN(value);
    }

    /**
     * ** Check if value is of type Date.
     */
    static isDate(value: any): value is Date {
        return value instanceof Date;
    }

    /**
     * ** Check if value is Primitive or Date.
     *
     *     - String, Number, Boolean, null, undefined or Date.
     */
    static isPrimitiveOrDate<T extends PrimitivesDate>(value: T | any): value is (Primitives | Nil | Date) {
        return CollectionsUtil.isPrimitive(value) || CollectionsUtil.isDate(value);
    }

    /**
     *  ** Check if value T is a reference that points to function (Class/Method).
     */
    // eslint-disable-next-line
    static isFunction<T extends (...args: any[]) => any>(value: T | any): value is (...args: any[]) => any {
        return typeof value === 'function';
    }

    /**
     * ** Check if value T is of type Object.
     */
    static isObject<T extends Record<string, unknown>>(obj: T | any): obj is Record<string, unknown> {
        return typeof obj === 'object';
    }

    /**
     * ** Check if value T is instance of Array.
     */
    static isArray<T>(arr: T | any): arr is (T extends any[] ? T : any[]) {
        return arr instanceof Array;
    }

    /**
     * ** Check if value T is not instance of Array or there are no elements in Array.
     */
    static isArrayEmpty<T>(arr: T | any): boolean {
        return !CollectionsUtil.isArray(arr) || arr.length === 0;
    }

    /**
     * ** Check if value is Map.
     */
    static isMap(obj: Map<any, any> | any): obj is Map<any, any> {
        return obj instanceof Map;
    }

    /**
     * ** Check if value is WeakMap.
     */
    static isWeakMap(obj: WeakMap<any, any> | any): obj is WeakMap<any, any> {
        return obj instanceof WeakMap;
    }

    /**
     * ** Check if value is Set.
     */
    static isSet(obj: Set<any> | any): obj is Set<any> {
        return obj instanceof Set;
    }

    /**
     * ** Check if value is Collection (literal Object, Array, Map, WeakMap or Set).
     */
    static isCollection(obj: Collections | any): obj is Collections {
        return CollectionsUtil.isArray(obj) ||
            CollectionsUtil.isMap(obj) ||
            CollectionsUtil.isWeakMap(obj) ||
            CollectionsUtil.isSet(obj) ||
            CollectionsUtil.isLiteralObject(obj);
    }

    /**
     * ** Check if value is of type Object and not null.
     */
    static isObjectNotNull<T extends Record<string, unknown>>(obj: T | any):
        obj is Record<string, unknown> & Subtract<Record<string, unknown>, null> {

        return CollectionsUtil.isObject<T>(obj) && !CollectionsUtil.isNull(obj);
    }

    /**
     * ** Check if some variable is of type Boolean and is true.
     */
    static isBooleanAndTrue(bool: boolean | any): boolean {
        return CollectionsUtil.isBoolean(bool) && bool;
    }

    /**
     * ** Check if value is literal Object or null.
     *
     *     - Not an Array, Map, WeakMap or Set.
     */
    static isLiteralObjectOrNull<T extends Record<string, unknown>>(obj: T | any): obj is LiteralObjectOrNull {
        return CollectionsUtil.isObject(obj) &&
            !CollectionsUtil.isArray(obj) &&
            !CollectionsUtil.isMap(obj) &&
            !CollectionsUtil.isWeakMap(obj) &&
            !CollectionsUtil.isSet(obj);
    }

    /**
     * ** Check if provided value is literal Object.
     *
     *     - Not and Array, Map, WeakMap, Set or null.
     */
    static isLiteralObject<T extends Record<string, unknown>>(obj: T | any): boolean {
        return CollectionsUtil.isLiteralObjectOrNull(obj) && !CollectionsUtil.isNull(obj);
    }

    /**
     * ** Check if value is Object and has properties.
     */
    static isObjectWithProperties<T extends Record<string, unknown>>(obj: T | any): boolean {
        return CollectionsUtil.isObjectNotNull(obj) && Object.keys(obj).length > 0;
    }

    /**
     * ** Return current Date in ISO string format.
     */
    static dateISO(): string {
        return new Date().toISOString();
    }

    /**
     * ** Performs deep comparison between two values to determine if the are equivalent.
     */
    static isEqual(value1: any, value2: any): boolean {
        return isEqual(value1, value2);
    }

    /**
     * ** Create recursive deep cloned value from provided one.
     */
    static cloneDeep<T>(value: T): T {
        return cloneDeep(value);
    }

    /**
     * ** Iterates own enumerable properties in Object.
     *
     *     - use Object.keys method for extraction, and executes provided iteratorFn.
     *     - if iteratorFn returns false or -1 it will break iteration.
     *     - all other return values continue until last property.
     *
     *     - flag as third parameter is optional:
     *          - Without flag or with flag and has value 'plainObject, method will iterate only through literal Objects.
     *          - With flag and has value 'objectLookLike', method will try to iterate through everything
     *                  that passes type value === 'object' (literal Object, Array, Map, Set, WeakMap, etc..).
     */
    static iterateObject<T extends Record<string, unknown>>(obj: T,
                                                            iteratorFn: ObjectIterator<T, IteratorFnResult>,
                                                            flag: 'plainObject' | 'objectLookLike' = 'plainObject'): T | null {

        if (!CollectionsUtil.isFunction(iteratorFn)) {
            return null;
        }

        if (flag === 'objectLookLike') {
            if (!CollectionsUtil.isObjectNotNull(obj)) {
                return null;
            }
        } else {
            if (!CollectionsUtil.isLiteralObject(obj)) {
                return null;
            }
        }

        const objectKeys = Object.keys(obj);
        for (const key of objectKeys) {
            const resultOfIteratorFn = iteratorFn(obj[key] as T[keyof T], key, obj);
            if (resultOfIteratorFn === false || resultOfIteratorFn === -1) {
                break;
            }
        }

        return obj;
    }

    /**
     * ** Check if value is Literal Object and has properties.
     */
    static isLiteralObjectWithProperties<T extends Record<string, unknown>>(obj: T | unknown): boolean {
        return CollectionsUtil.isLiteralObject<T>(obj) && Object.keys(obj).length > 0;
    }

    /**
     * ** Iterates over object properties and return Array of its values.
     */
    static objectValues<T extends Record<string, any>>(obj: T | null | undefined): Array<T[keyof T]> {
        const _result: Array<T[keyof T]> = [];

        CollectionsUtil.iterateObject(obj, (value) => {
            _result.push(value);
        });

        return _result;
    }

    /**
     * ** Transform given Map to Object.
     */
    static transformMapToObject<T extends Map<string, unknown>>(map: T): { [key: string]: unknown } {
        const obj: { [key: string]: any } = {};

        map.forEach((value, key) => obj[key] = value);

        return obj;
    }

    /**
     * ** Transform given Object to Map.
     */
    static transformObjectToMap<T extends { [key: string]: any }>(obj: T): Map<string, any> {
        const map = new Map<string, any>();

        CollectionsUtil.iterateObject(obj, (value, key) => {
            map.set(key, value);
        });

        return map;
    }

    /**
     * ** Iterates over object properties and return Array of its keys/values in pairs.
     * <p>
     *     - Returns Array of subArrays that have 2 elements each, first element key and second element value.
     */
    static objectPairs<T extends Record<string, any>>(obj: T | null | undefined): Array<[string, T[keyof T]]> {
        if (!CollectionsUtil.isLiteralObject(obj)) {
            return [];
        }

        return Object.entries(obj) as Array<[string, T[keyof T]]>;
    }

    /**
     * ** Return own property Descriptor from provided object/function.
     */
    static getObjectPropertyDescriptor<T extends Record<string, any>>(obj: T, key: string): PropertyDescriptor {
        if (!((CollectionsUtil.isFunction(obj) || CollectionsUtil.isObject(obj)) && CollectionsUtil.isString(key))) {
            return null;
        }

        return Object.getOwnPropertyDescriptor(obj, key);
    }

    /**
     * ** Iterates own enumerable properties (statics) of Function (Class).
     *
     *     - use Object.getOwnPropertyDescriptors method for extraction, and executes provided iteratorFn.
     *     - if iteratorFn returns false or -1 will break iteration.
     *     - all other return values means continue until last property.
     */
    static iterateClassStatics<T extends Record<string, any>>(fn: T,
                                                              iteratorFn: (descriptor: PropertyDescriptor,
                                                                           key: string,
                                                                           fn: T) => IteratorFnResult) {

        if (!CollectionsUtil.isFunction(fn) || !CollectionsUtil.isFunction(iteratorFn)) {
            return null;
        }

        const descriptors = Object.getOwnPropertyDescriptors(fn);
        CollectionsUtil.iterateObject(
            descriptors,
            (descriptor: PropertyDescriptor, key) => iteratorFn(descriptor, key, fn)
        );

        return fn;
    }

    /**
     * ** Check if two Maps are Equal.
     *
     *   - They are equal if they have same references.
     *   - They are equal if they have same keys and same values for compared keys.
     */
    static areMapsEqual(m1: Map<unknown, unknown>, m2: Map<unknown, unknown>): boolean {
        const evaluateDeepComparison = () => {
            for (const [key, val] of m1) {
                const compareVal = m2.get(key);

                if (CollectionsUtil.isMap(val)) {
                    if (!CollectionsUtil.areMapsEqual(val, compareVal as Map<unknown, unknown>)) {
                        return false;
                    }

                    continue;
                }

                if (!CollectionsUtil.isEqual(val, compareVal) || (CollectionsUtil.isUndefined(compareVal) && !m2.has(key))) {
                    return false;
                }
            }

            return true;
        };

        return CollectionsUtil.isMap(m1)
            && CollectionsUtil.isMap(m2)
            && (
                m1 === m2
                || (
                    m1.size === m2.size
                    && evaluateDeepComparison()
                )
            );
    }

    /**
     * ** Interpolate string and replace while iterating through provided strings.
     *
     *      - Replacers are strings that are replaced on every place where %s is found starting from index 0.
     */
    static interpolateString(target: string, ...replacers: string[]): string;
    /**
     * ** Interpolate text and replace while iterating through provided replacers.
     *
     *      - Replacers are objects ofType {@link Replacer} that are iterates and consumes,
     *              searchValue is matcher and replaceValue is value that is placed on match.
     */
    static interpolateString(target: string, ...replacers: Array<Replacer<string>>): string;
    /**
     * @inheritDoc
     */
    static interpolateString(target: string, ...replacers: string[] | Array<Replacer<string>>): string {
        let response = target;

        replacers.forEach((replacer: string | Replacer<string>) => {
            if (CollectionsUtil.isString(replacer)) {
                response = response.replace('%s', replacer);
            } else {
                response = response.replace(
                    replacer.searchValue,
                    replacer.replaceValue
                );
            }
        });

        return response;
    }
}
