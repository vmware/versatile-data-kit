/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/naming-convention,prefer-arrow/prefer-arrow-functions,space-before-function-paren */

import { CollectionsUtil } from './collections-util';

const testObj: {
	num: number;
	str: string;
	arr: any[];
	arrEmpty: any[];
	obj: Record<any, any>;
	objNoProp: Record<any, any>;
	undef: any;
	nullVal: null;
	bool: boolean;
	nan: any;
	map: Map<any, any>;
	weakMap: WeakMap<any, any>;
	set: Set<any>;
	func: () => void;
	date: Date;
} = {
	num: 1,
	str: 'string',
	arr: [1, 2, 3, 4, 5],
	arrEmpty: [],
	obj: { prop: 1 },
	objNoProp: {},
	undef: undefined,
	nullVal: null,
	bool: true,
	nan: NaN,
	map: new Map(),
	weakMap: new WeakMap(),
	set: new Set(),
	func: () => {
		// do nothing;
	},
	date: new Date()
};

describe('CollectionsUtil::', () => {
	describe('Statics', () => {
		describe('Methods::()', () => {
			describe('|isUndefined|', () => {
				it('should verify if undefined', () => {
					expect(CollectionsUtil.isUndefined(testObj.undef)).toBeTruthy();

					expect(CollectionsUtil.isUndefined(testObj.num)).toBeFalsy();
					expect(CollectionsUtil.isUndefined(testObj.str)).toBeFalsy();
					expect(CollectionsUtil.isUndefined(testObj.arr)).toBeFalsy();
					expect(CollectionsUtil.isUndefined(testObj.arrEmpty)).toBeFalsy();
					expect(CollectionsUtil.isUndefined(testObj.obj)).toBeFalsy();
					expect(CollectionsUtil.isUndefined(testObj.objNoProp)).toBeFalsy();
					expect(CollectionsUtil.isUndefined(testObj.nullVal)).toBeFalsy();
					expect(CollectionsUtil.isUndefined(testObj.bool)).toBeFalsy();
					expect(CollectionsUtil.isUndefined(testObj.nan)).toBeFalsy();
					expect(CollectionsUtil.isUndefined(testObj.func)).toBeFalsy();
				});
			});

			describe('|isNumber|', () => {
				it('should verify if number', () => {
					expect(CollectionsUtil.isNumber(testObj.num)).toBeTruthy();
					expect(CollectionsUtil.isNumber(testObj.nan)).toBeTruthy();

					expect(CollectionsUtil.isNumber(testObj.str)).toBeFalsy();
					expect(CollectionsUtil.isNumber(testObj.arr)).toBeFalsy();
					expect(CollectionsUtil.isNumber(testObj.arrEmpty)).toBeFalsy();
					expect(CollectionsUtil.isNumber(testObj.obj)).toBeFalsy();
					expect(CollectionsUtil.isNumber(testObj.objNoProp)).toBeFalsy();
					expect(CollectionsUtil.isNumber(testObj.undef)).toBeFalsy();
					expect(CollectionsUtil.isNumber(testObj.nullVal)).toBeFalsy();
					expect(CollectionsUtil.isNumber(testObj.bool)).toBeFalsy();
					expect(CollectionsUtil.isNumber(testObj.func)).toBeFalsy();
				});
			});

			describe('|isString|', () => {
				it('should verify if string', () => {
					expect(CollectionsUtil.isString(testObj.str)).toBeTruthy();

					expect(CollectionsUtil.isString(testObj.num)).toBeFalsy();
					expect(CollectionsUtil.isString(testObj.arr)).toBeFalsy();
					expect(CollectionsUtil.isString(testObj.arrEmpty)).toBeFalsy();
					expect(CollectionsUtil.isString(testObj.obj)).toBeFalsy();
					expect(CollectionsUtil.isString(testObj.objNoProp)).toBeFalsy();
					expect(CollectionsUtil.isString(testObj.undef)).toBeFalsy();
					expect(CollectionsUtil.isString(testObj.nullVal)).toBeFalsy();
					expect(CollectionsUtil.isString(testObj.bool)).toBeFalsy();
					expect(CollectionsUtil.isString(testObj.nan)).toBeFalsy();
					expect(CollectionsUtil.isString(testObj.func)).toBeFalsy();
				});
			});

			describe('|isBoolean|', () => {
				it('should verify if boolean', () => {
					expect(CollectionsUtil.isBoolean(testObj.bool)).toBeTruthy();

					expect(CollectionsUtil.isBoolean(testObj.num)).toBeFalsy();
					expect(CollectionsUtil.isBoolean(testObj.str)).toBeFalsy();
					expect(CollectionsUtil.isBoolean(testObj.arr)).toBeFalsy();
					expect(CollectionsUtil.isBoolean(testObj.arrEmpty)).toBeFalsy();
					expect(CollectionsUtil.isBoolean(testObj.obj)).toBeFalsy();
					expect(CollectionsUtil.isBoolean(testObj.objNoProp)).toBeFalsy();
					expect(CollectionsUtil.isBoolean(testObj.undef)).toBeFalsy();
					expect(CollectionsUtil.isBoolean(testObj.nullVal)).toBeFalsy();
					expect(CollectionsUtil.isBoolean(testObj.nan)).toBeFalsy();
					expect(CollectionsUtil.isBoolean(testObj.func)).toBeFalsy();
				});
			});

			describe('|isPrimitive|', () => {
				it('should verify if value is Primitive', () => {
					expect(CollectionsUtil.isPrimitive(testObj.bool)).toBeTruthy();
					expect(CollectionsUtil.isPrimitive(testObj.num)).toBeTruthy();
					expect(CollectionsUtil.isPrimitive(testObj.nan)).toBeTruthy();
					expect(CollectionsUtil.isPrimitive(testObj.str)).toBeTruthy();
					expect(CollectionsUtil.isPrimitive(testObj.undef)).toBeTruthy();

					expect(CollectionsUtil.isPrimitive(testObj.arr)).toBeFalsy();
					expect(CollectionsUtil.isPrimitive(testObj.arrEmpty)).toBeFalsy();
					expect(CollectionsUtil.isPrimitive(testObj.obj)).toBeFalsy();
					expect(CollectionsUtil.isPrimitive(testObj.objNoProp)).toBeFalsy();
					expect(CollectionsUtil.isPrimitive(testObj.nullVal)).toBeFalsy();
					expect(CollectionsUtil.isPrimitive(testObj.func)).toBeFalsy();
				});
			});

			describe('|isObject|', () => {
				it('should verify if object', () => {
					expect(CollectionsUtil.isObject(testObj.obj)).toBeTruthy();
					expect(CollectionsUtil.isObject(testObj.objNoProp)).toBeTruthy();
					expect(CollectionsUtil.isObject(testObj.arr)).toBeTruthy();
					expect(CollectionsUtil.isObject(testObj.arrEmpty)).toBeTruthy();
					expect(CollectionsUtil.isObject(testObj.nullVal)).toBeTruthy();

					expect(CollectionsUtil.isObject(testObj.func)).toBeFalsy();
					expect(CollectionsUtil.isObject(testObj.num)).toBeFalsy();
					expect(CollectionsUtil.isObject(testObj.str)).toBeFalsy();
					expect(CollectionsUtil.isObject(testObj.undef)).toBeFalsy();
					expect(CollectionsUtil.isObject(testObj.bool)).toBeFalsy();
					expect(CollectionsUtil.isObject(testObj.nan)).toBeFalsy();
				});
			});

			describe('|isArray|', () => {
				it('should verify if array', () => {
					expect(CollectionsUtil.isArray(testObj.arr)).toBeTruthy();
					expect(CollectionsUtil.isArray(testObj.arrEmpty)).toBeTruthy();

					expect(CollectionsUtil.isArray(testObj.num)).toBeFalsy();
					expect(CollectionsUtil.isArray(testObj.str)).toBeFalsy();
					expect(CollectionsUtil.isArray(testObj.obj)).toBeFalsy();
					expect(CollectionsUtil.isArray(testObj.objNoProp)).toBeFalsy();
					expect(CollectionsUtil.isArray(testObj.undef)).toBeFalsy();
					expect(CollectionsUtil.isArray(testObj.nullVal)).toBeFalsy();
					expect(CollectionsUtil.isArray(testObj.bool)).toBeFalsy();
					expect(CollectionsUtil.isArray(testObj.nan)).toBeFalsy();
					expect(CollectionsUtil.isArray(testObj.func)).toBeFalsy();
				});
			});

			describe('|isArrayEmpty|', () => {
				it('should verify will return true when value is not Array', () => {
					expect(CollectionsUtil.isArrayEmpty(testObj.num)).toBeTruthy();
					expect(CollectionsUtil.isArrayEmpty(testObj.str)).toBeTruthy();
					expect(CollectionsUtil.isArrayEmpty(testObj.obj)).toBeTruthy();
					expect(CollectionsUtil.isArrayEmpty(testObj.objNoProp)).toBeTruthy();
					expect(CollectionsUtil.isArrayEmpty(testObj.undef)).toBeTruthy();
					expect(CollectionsUtil.isArrayEmpty(testObj.nullVal)).toBeTruthy();
					expect(CollectionsUtil.isArrayEmpty(testObj.bool)).toBeTruthy();
					expect(CollectionsUtil.isArrayEmpty(testObj.nan)).toBeTruthy();
					expect(CollectionsUtil.isArrayEmpty(testObj.func)).toBeTruthy();
				});

				it(`should verify will return true when value is Array and doesn't have elements`, () => {
					expect(CollectionsUtil.isArrayEmpty(testObj.arrEmpty)).toBeTruthy();
				});

				it('should verify will return false when value is Array and has elements', () => {
					expect(CollectionsUtil.isArrayEmpty(testObj.arr)).toBeFalsy();
				});
			});

			describe('|isNull|', () => {
				it('should verify if null', () => {
					expect(CollectionsUtil.isNull(testObj.nullVal)).toBeTruthy();

					expect(CollectionsUtil.isNull(testObj.num)).toBeFalsy();
					expect(CollectionsUtil.isNull(testObj.str)).toBeFalsy();
					expect(CollectionsUtil.isNull(testObj.arr)).toBeFalsy();
					expect(CollectionsUtil.isNull(testObj.arrEmpty)).toBeFalsy();
					expect(CollectionsUtil.isNull(testObj.obj)).toBeFalsy();
					expect(CollectionsUtil.isNull(testObj.objNoProp)).toBeFalsy();
					expect(CollectionsUtil.isNull(testObj.undef)).toBeFalsy();
					expect(CollectionsUtil.isNull(testObj.bool)).toBeFalsy();
					expect(CollectionsUtil.isNull(testObj.nan)).toBeFalsy();
					expect(CollectionsUtil.isNull(testObj.func)).toBeFalsy();
				});
			});

			describe('|isNaN|', () => {
				it('should verify if nan', () => {
					expect(CollectionsUtil.isNaN(testObj.nan)).toBeTruthy();

					expect(CollectionsUtil.isNaN(testObj.func)).toBeFalsy();
					expect(CollectionsUtil.isNaN(testObj.nullVal)).toBeFalsy();
					expect(CollectionsUtil.isNaN(testObj.num)).toBeFalsy();
					expect(CollectionsUtil.isNaN(testObj.str)).toBeFalsy();
					expect(CollectionsUtil.isNaN(testObj.arr)).toBeFalsy();
					expect(CollectionsUtil.isNaN(testObj.arrEmpty)).toBeFalsy();
					expect(CollectionsUtil.isNaN(testObj.obj)).toBeFalsy();
					expect(CollectionsUtil.isNaN(testObj.objNoProp)).toBeFalsy();
					expect(CollectionsUtil.isNaN(testObj.undef)).toBeFalsy();
					expect(CollectionsUtil.isNaN(testObj.bool)).toBeFalsy();
				});
			});

			describe('|isDate|', () => {
				it('should verify if Date', () => {
					expect(CollectionsUtil.isDate(testObj.date)).toBeTruthy();

					expect(CollectionsUtil.isDate(testObj.nan)).toBeFalsy();
					expect(CollectionsUtil.isDate(testObj.func)).toBeFalsy();
					expect(CollectionsUtil.isDate(testObj.nullVal)).toBeFalsy();
					expect(CollectionsUtil.isDate(testObj.num)).toBeFalsy();
					expect(CollectionsUtil.isDate(testObj.str)).toBeFalsy();
					expect(CollectionsUtil.isDate(testObj.arr)).toBeFalsy();
					expect(CollectionsUtil.isDate(testObj.arrEmpty)).toBeFalsy();
					expect(CollectionsUtil.isDate(testObj.obj)).toBeFalsy();
					expect(CollectionsUtil.isDate(testObj.objNoProp)).toBeFalsy();
					expect(CollectionsUtil.isDate(testObj.undef)).toBeFalsy();
					expect(CollectionsUtil.isDate(testObj.bool)).toBeFalsy();
				});
			});

			describe('|isPrimitiveOrDate|', () => {
				it('should verify if Date or Primitive', () => {
					expect(CollectionsUtil.isPrimitiveOrDate(testObj.date)).toBeTruthy();
					expect(CollectionsUtil.isPrimitiveOrDate(testObj.bool)).toBeTruthy();
					expect(CollectionsUtil.isPrimitiveOrDate(testObj.num)).toBeTruthy();
					expect(CollectionsUtil.isPrimitiveOrDate(testObj.nan)).toBeTruthy();
					expect(CollectionsUtil.isPrimitiveOrDate(testObj.str)).toBeTruthy();
					expect(CollectionsUtil.isPrimitiveOrDate(testObj.undef)).toBeTruthy();

					expect(CollectionsUtil.isPrimitiveOrDate(testObj.arr)).toBeFalsy();
					expect(
						CollectionsUtil.isPrimitiveOrDate(testObj.arrEmpty)
					).toBeFalsy();
					expect(CollectionsUtil.isPrimitiveOrDate(testObj.obj)).toBeFalsy();
					expect(
						CollectionsUtil.isPrimitiveOrDate(testObj.objNoProp)
					).toBeFalsy();
					expect(
						CollectionsUtil.isPrimitiveOrDate(testObj.nullVal)
					).toBeFalsy();
					expect(CollectionsUtil.isPrimitiveOrDate(testObj.func)).toBeFalsy();
				});
			});

			describe('|isFunction|', () => {
				it('should verify if function', () => {
					expect(CollectionsUtil.isFunction(testObj.func)).toBeTruthy();

					expect(CollectionsUtil.isFunction(testObj.nullVal)).toBeFalsy();
					expect(CollectionsUtil.isFunction(testObj.num)).toBeFalsy();
					expect(CollectionsUtil.isFunction(testObj.str)).toBeFalsy();
					expect(CollectionsUtil.isFunction(testObj.arr)).toBeFalsy();
					expect(CollectionsUtil.isFunction(testObj.arrEmpty)).toBeFalsy();
					expect(CollectionsUtil.isFunction(testObj.obj)).toBeFalsy();
					expect(CollectionsUtil.isFunction(testObj.objNoProp)).toBeFalsy();
					expect(CollectionsUtil.isFunction(testObj.undef)).toBeFalsy();
					expect(CollectionsUtil.isFunction(testObj.bool)).toBeFalsy();
					expect(CollectionsUtil.isFunction(testObj.nan)).toBeFalsy();
				});
			});

			describe('|isBooleanAndTrue|', () => {
				it('should verify if boolean and true', () => {
					expect(CollectionsUtil.isBooleanAndTrue(testObj.bool)).toBeTruthy();
					expect(CollectionsUtil.isBooleanAndTrue(false)).toBeFalsy();

					expect(CollectionsUtil.isBooleanAndTrue(testObj.num)).toBeFalsy();
					expect(CollectionsUtil.isBooleanAndTrue(testObj.str)).toBeFalsy();
					expect(CollectionsUtil.isBooleanAndTrue(testObj.arr)).toBeFalsy();
					expect(
						CollectionsUtil.isBooleanAndTrue(testObj.arrEmpty)
					).toBeFalsy();
					expect(CollectionsUtil.isBooleanAndTrue(testObj.obj)).toBeFalsy();
					expect(
						CollectionsUtil.isBooleanAndTrue(testObj.objNoProp)
					).toBeFalsy();
					expect(CollectionsUtil.isBooleanAndTrue(testObj.undef)).toBeFalsy();
					expect(CollectionsUtil.isBooleanAndTrue(testObj.nullVal)).toBeFalsy();
					expect(CollectionsUtil.isBooleanAndTrue(testObj.nan)).toBeFalsy();
					expect(CollectionsUtil.isBooleanAndTrue(testObj.func)).toBeFalsy();
				});
			});

			describe('|isLiteralObjectOrNull|', () => {
				it('should verify if literal object including null', () => {
					expect(
						CollectionsUtil.isLiteralObjectOrNull(testObj.obj)
					).toBeTruthy();
					expect(
						CollectionsUtil.isLiteralObjectOrNull(testObj.objNoProp)
					).toBeTruthy();
					expect(
						CollectionsUtil.isLiteralObjectOrNull(testObj.nullVal)
					).toBeTruthy();

					expect(
						CollectionsUtil.isLiteralObjectOrNull(testObj.func)
					).toBeFalsy();
					expect(
						CollectionsUtil.isLiteralObjectOrNull(testObj.num)
					).toBeFalsy();
					expect(
						CollectionsUtil.isLiteralObjectOrNull(testObj.str)
					).toBeFalsy();
					expect(
						CollectionsUtil.isLiteralObjectOrNull(testObj.arr)
					).toBeFalsy();
					expect(
						CollectionsUtil.isLiteralObjectOrNull(testObj.arrEmpty)
					).toBeFalsy();
					expect(
						CollectionsUtil.isLiteralObjectOrNull(testObj.undef)
					).toBeFalsy();
					expect(
						CollectionsUtil.isLiteralObjectOrNull(testObj.bool)
					).toBeFalsy();
					expect(
						CollectionsUtil.isLiteralObjectOrNull(testObj.nan)
					).toBeFalsy();
				});
			});

			describe('|isLiteralObject|', () => {
				it('should verify if literal object', () => {
					expect(CollectionsUtil.isLiteralObject(testObj.obj)).toBeTruthy();
					expect(
						CollectionsUtil.isLiteralObject(testObj.objNoProp)
					).toBeTruthy();

					expect(CollectionsUtil.isLiteralObject(testObj.func)).toBeFalsy();
					expect(CollectionsUtil.isLiteralObject(testObj.num)).toBeFalsy();
					expect(CollectionsUtil.isLiteralObject(testObj.str)).toBeFalsy();
					expect(CollectionsUtil.isLiteralObject(testObj.arr)).toBeFalsy();
					expect(CollectionsUtil.isLiteralObject(testObj.arrEmpty)).toBeFalsy();
					expect(CollectionsUtil.isLiteralObject(testObj.undef)).toBeFalsy();
					expect(CollectionsUtil.isLiteralObject(testObj.nullVal)).toBeFalsy();
					expect(CollectionsUtil.isLiteralObject(testObj.bool)).toBeFalsy();
					expect(CollectionsUtil.isLiteralObject(testObj.nan)).toBeFalsy();
				});
			});

			describe('|isLiteralObjectWithProperties|', () => {
				it('should verify if plain object with properties', () => {
					expect(
						CollectionsUtil.isLiteralObjectWithProperties(testObj.obj)
					).toBeTruthy();

					expect(
						CollectionsUtil.isLiteralObjectWithProperties(testObj.func)
					).toBeFalsy();
					expect(
						CollectionsUtil.isLiteralObjectWithProperties(testObj.num)
					).toBeFalsy();
					expect(
						CollectionsUtil.isLiteralObjectWithProperties(testObj.str)
					).toBeFalsy();
					expect(
						CollectionsUtil.isLiteralObjectWithProperties(testObj.arr)
					).toBeFalsy();
					expect(
						CollectionsUtil.isLiteralObjectWithProperties(testObj.arrEmpty)
					).toBeFalsy();
					expect(
						CollectionsUtil.isLiteralObjectWithProperties(testObj.objNoProp)
					).toBeFalsy();
					expect(
						CollectionsUtil.isLiteralObjectWithProperties(testObj.undef)
					).toBeFalsy();
					expect(
						CollectionsUtil.isLiteralObjectWithProperties(testObj.nullVal)
					).toBeFalsy();
					expect(
						CollectionsUtil.isLiteralObjectWithProperties(testObj.bool)
					).toBeFalsy();
					expect(
						CollectionsUtil.isLiteralObjectWithProperties(testObj.nan)
					).toBeFalsy();
				});
			});

			describe('|isCollection|', () => {
				it('should verify if value is type of Collection', () => {
					expect(CollectionsUtil.isCollection(testObj.obj)).toBeTruthy();
					expect(CollectionsUtil.isCollection(testObj.arr)).toBeTruthy();
					expect(CollectionsUtil.isCollection(testObj.arrEmpty)).toBeTruthy();
					expect(CollectionsUtil.isCollection(testObj.objNoProp)).toBeTruthy();
					expect(CollectionsUtil.isCollection(testObj.map)).toBeTruthy();
					expect(CollectionsUtil.isCollection(testObj.weakMap)).toBeTruthy();
					expect(CollectionsUtil.isCollection(testObj.set)).toBeTruthy();

					expect(CollectionsUtil.isCollection(testObj.func)).toBeFalsy();
					expect(CollectionsUtil.isCollection(testObj.num)).toBeFalsy();
					expect(CollectionsUtil.isCollection(testObj.str)).toBeFalsy();
					expect(CollectionsUtil.isCollection(testObj.undef)).toBeFalsy();
					expect(CollectionsUtil.isCollection(testObj.nullVal)).toBeFalsy();
					expect(CollectionsUtil.isCollection(testObj.bool)).toBeFalsy();
					expect(CollectionsUtil.isCollection(testObj.nan)).toBeFalsy();
				});
			});

			describe('|isObjectNotNull|', () => {
				it('should verify if value is Object but not null', () => {
					expect(CollectionsUtil.isObjectNotNull(testObj.obj)).toBeTruthy();
					expect(CollectionsUtil.isObjectNotNull(testObj.arr)).toBeTruthy();
					expect(
						CollectionsUtil.isObjectNotNull(testObj.arrEmpty)
					).toBeTruthy();
					expect(
						CollectionsUtil.isObjectNotNull(testObj.objNoProp)
					).toBeTruthy();
					expect(CollectionsUtil.isObjectNotNull(testObj.map)).toBeTruthy();
					expect(CollectionsUtil.isObjectNotNull(testObj.weakMap)).toBeTruthy();
					expect(CollectionsUtil.isObjectNotNull(testObj.set)).toBeTruthy();

					expect(CollectionsUtil.isObjectNotNull(testObj.func)).toBeFalsy();
					expect(CollectionsUtil.isObjectNotNull(testObj.num)).toBeFalsy();
					expect(CollectionsUtil.isObjectNotNull(testObj.str)).toBeFalsy();
					expect(CollectionsUtil.isObjectNotNull(testObj.undef)).toBeFalsy();
					expect(CollectionsUtil.isObjectNotNull(testObj.nullVal)).toBeFalsy();
					expect(CollectionsUtil.isObjectNotNull(testObj.bool)).toBeFalsy();
					expect(CollectionsUtil.isObjectNotNull(testObj.nan)).toBeFalsy();
				});
			});

			describe('|isObjectWithProperties|', () => {
				it('should verify if value is Object and has properties', () => {
					expect(
						CollectionsUtil.isObjectWithProperties(testObj.obj)
					).toBeTruthy();
					expect(
						CollectionsUtil.isObjectWithProperties(testObj.arr)
					).toBeTruthy();

					expect(
						CollectionsUtil.isObjectWithProperties(testObj.map)
					).toBeFalsy();
					expect(
						CollectionsUtil.isObjectWithProperties(testObj.weakMap)
					).toBeFalsy();
					expect(
						CollectionsUtil.isObjectWithProperties(testObj.set)
					).toBeFalsy();
					expect(
						CollectionsUtil.isObjectWithProperties(testObj.objNoProp)
					).toBeFalsy();
					expect(
						CollectionsUtil.isObjectWithProperties(testObj.arrEmpty)
					).toBeFalsy();
					expect(
						CollectionsUtil.isObjectWithProperties(testObj.func)
					).toBeFalsy();
					expect(
						CollectionsUtil.isObjectWithProperties(testObj.num)
					).toBeFalsy();
					expect(
						CollectionsUtil.isObjectWithProperties(testObj.str)
					).toBeFalsy();
					expect(
						CollectionsUtil.isObjectWithProperties(testObj.undef)
					).toBeFalsy();
					expect(
						CollectionsUtil.isObjectWithProperties(testObj.nullVal)
					).toBeFalsy();
					expect(
						CollectionsUtil.isObjectWithProperties(testObj.bool)
					).toBeFalsy();
					expect(
						CollectionsUtil.isObjectWithProperties(testObj.nan)
					).toBeFalsy();
				});
			});

			describe('|dateISO|', () => {
				it('should verify will return Date in ISO format', () => {
					// When
					const res = CollectionsUtil.dateISO();

					// Then
					// eslint-disable-next-line max-len
					expect(
						/^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$/.test(
							res
						)
					);
				});
			});

			describe('|isEqual|', () => {
				it('should verify will return true after deep comparison of two objects', () => {
					// Given
					const obj1 = {
						project: 'aProject',
						country: 'aCountry',
						teams: ['aTeam', 'bTeam', 'cTeam', 'dTeam'],
						managers: {
							aTeam: 'aManager',
							bTeam: 'bManager'
						},
						prod: true,
						age: 3,
						deps: null
					};
					const obj2 = {
						project: 'aProject',
						country: 'aCountry',
						teams: ['aTeam', 'bTeam', 'cTeam', 'dTeam'],
						managers: {
							aTeam: 'aManager',
							bTeam: 'bManager'
						},
						prod: true,
						age: 3,
						deps: null
					};

					// When
					const r = CollectionsUtil.isEqual(obj1, obj2);

					// Then
					expect(r).toBeTrue();
				});
			});

			describe('|cloneDeep|', () => {
				it('should verify will deep clone provided Object', () => {
					// Given
					class A {
						constructor(protected readonly name: string) {}
					}

					class B extends A {
						constructor(name: string, private readonly surname: string) {
							super(name);
						}

						getName(): string {
							return this.name;
						}

						getSurname(): string {
							return this.surname;
						}
					}

					const instance = new B('aUser', 'bUser');

					// When
					const cloned = CollectionsUtil.cloneDeep(instance);

					// Then
					expect(cloned).not.toBe(instance);
					expect(cloned).toEqual(instance);
					expect(cloned.getName()).toEqual('aUser');
					expect(cloned.getSurname()).toEqual('bUser');
				});

				it('should verify will deep clone provided Array', () => {
					// Given
					const arr = ['aUser', 'bUser', 'cUser'];

					// When
					const cloned = CollectionsUtil.cloneDeep(arr);

					// Then
					expect(cloned).not.toBe(arr);
					expect(cloned).toEqual(arr);
				});
			});

			describe('|objectValues|', () => {
				it('should verify will return Array of values from provided Object', () => {
					// Given
					const obj = {
						prop1: 1,
						prop2: 2,
						prop3: 3,
						prop4: 4,
						prop5: 5
					};

					// When
					const values = CollectionsUtil.objectValues(obj);

					// Then
					expect(values).toEqual([1, 2, 3, 4, 5]);
				});
			});

			describe('|transformMapToObject|', () => {
				it('should verify will remap provided Map to Object', () => {
					// Given
					const map = new Map<string, any>();
					map.set('name', 'aName');
					map.set('age', 35);
					map.set('surname', 'aSurname');
					map.set('city', 'aCity');
					map.set('graduated', true);

					// When
					const obj = CollectionsUtil.transformMapToObject(map);

					// Then
					expect(obj).toEqual({
						name: 'aName',
						age: 35,
						surname: 'aSurname',
						city: 'aCity',
						graduated: true
					});
				});
			});

			describe('|transformObjectToMap|', () => {
				it('should verify will remap provided Object to Map', () => {
					// Given
					const assertionMap = new Map<string, any>();
					assertionMap.set('name', 'aName');
					assertionMap.set('age', 35);
					assertionMap.set('surname', 'aSurname');
					assertionMap.set('city', 'aCity');
					assertionMap.set('graduated', true);

					const obj: { [key: string]: any } = {
						name: 'aName',
						age: 35,
						surname: 'aSurname',
						city: 'aCity',
						graduated: true
					};

					// When
					const map = CollectionsUtil.transformObjectToMap(obj);

					// Then
					expect(map).toEqual(assertionMap);
				});
			});

			describe('|iterateObject|', () => {
				it('should verify method will iterate all properties from Object', () => {
					// Given
					const obj = {
						prop1: 'prop1',
						prop2: [],
						prop3: {},
						prop4: true
					};

					// When/Then
					let cnt = 0;
					const r = CollectionsUtil.iterateObject(
						obj,
						(value, key, collection) => {
							expect(obj[key]).toBe(value);
							expect(obj).toBe(collection);
							cnt++;
						}
					);

					expect(cnt).toEqual(4);
					expect(r).toBe(obj);
				});

				it('should verify will return null immediately if there is no iterator provided', () => {
					// Given
					const obj = {
						prop1: 'prop1',
						prop2: [],
						prop3: {},
						prop4: true
					};

					// When
					const r = CollectionsUtil.iterateObject(obj, null);

					// Then
					expect(r).toEqual(null);
				});

				it('should verify will return null immediately if value is not literal object', () => {
					// Given
					const obj = [] as unknown;

					// When/Then
					let cnt = 0;
					const r = CollectionsUtil.iterateObject(
						obj as Record<string, unknown>,
						() => {
							cnt++;
						}
					);

					expect(cnt).toEqual(0);
					expect(r).toEqual(null);
				});

				it('should verify will return null immediately if value is null', () => {
					// Given
					const obj = null;

					// When/Then
					let cnt = 0;
					const r = CollectionsUtil.iterateObject(obj, () => {
						cnt++;
					});

					expect(cnt).toEqual(0);
					expect(r).toEqual(null);
				});

				it('should verify will return null immediately if value is null', () => {
					// When/Then
					let cnt = 0;
					const r = CollectionsUtil.iterateObject(
						null,
						() => {
							cnt++;
						},
						'objectLookLike'
					);

					expect(cnt).toEqual(0);
					expect(r).toEqual(null);
				});

				it('should verify will break iteration if iterator returns false or -1', () => {
					// Given
					const obj = {
						prop1: 'prop1',
						prop2: [],
						prop3: {},
						prop4: true
					};

					// When/Then
					let cnt1 = 0;
					// @ts-ignore
					const r1 = CollectionsUtil.iterateObject(
						obj,
						(value, key, collection) => {
							if (cnt1 === 2) {
								return false;
							}

							expect(obj[key]).toBe(value);
							expect(obj).toBe(collection);
							cnt1++;
						}
					);
					let cnt2 = 0;
					// @ts-ignore
					const r2 = CollectionsUtil.iterateObject(
						obj,
						(value, key, collection) => {
							if (cnt2 === 3) {
								return -1;
							}

							expect(obj[key]).toBe(value);
							expect(obj).toBe(collection);
							cnt2++;
						}
					);

					expect(cnt2).toEqual(3);
					expect(r1).toBe(obj);
					expect(r2).toBe(obj);
				});
			});

			describe('|objectPairs|', () => {
				it('should verify will return Array of pairs [key, value] from provided Object', () => {
					// Given
					const obj: { [key: string]: any } = {
						prop1: 1,
						prop2: 2,
						prop3: 3,
						prop4: 4,
						prop5: 5
					};

					// When
					const values = CollectionsUtil.objectPairs(obj);

					// Then
					expect(values).toEqual([
						['prop1', 1],
						['prop2', 2],
						['prop3', 3],
						['prop4', 4],
						['prop5', 5]
					]);
				});

				it('should verify will return empty Array if provided value is not literal Object', () => {
					// When
					const values = CollectionsUtil.objectPairs(null);

					// Then
					expect(values).toEqual([]);
				});
			});

			describe('|getObjectPropertyDescriptor|', () => {
				it('should verify will get Object property descriptor', () => {
					// Given
					const obj = { user: 'aUser' };

					// When
					const descriptor = CollectionsUtil.getObjectPropertyDescriptor(
						obj,
						'user'
					);

					// Then
					expect(descriptor).toEqual({
						value: 'aUser',
						enumerable: true,
						configurable: true,
						writable: true
					});
				});

				it('should verify will return null if provided value is not Function or Object or key is not String', () => {
					// When
					const descriptor1 = CollectionsUtil.getObjectPropertyDescriptor(
						undefined,
						'user'
					);
					const descriptor2 = CollectionsUtil.getObjectPropertyDescriptor(
						{},
						null
					);
					const descriptor3 = CollectionsUtil.getObjectPropertyDescriptor(
						function () {
							// No-op.
						},
						null
					);

					// Then
					expect(descriptor1).toEqual(null);
					expect(descriptor2).toEqual(null);
					expect(descriptor3).toEqual(null);
				});
			});

			describe('|iterateClassStatics|', () => {
				it('should verify will return null when no class provided', () => {
					// Given
					let cnt = 0;

					// When
					const result = CollectionsUtil.iterateClassStatics(
						null,
						(_descriptor, _key, _fn) => {
							cnt++;
						}
					);

					// Then
					expect(result).toEqual(null);
					expect(cnt).toEqual(0);
				});
			});

			describe('|areMapsEqual|', () => {
				it('should verify will return true when maps are same reference', () => {
					// Given
					const map1 = new Map<string, any>([
						['users', ['aUser', 'bUser', 'cUser']]
					]);
					const map2 = map1;

					// When
					const result = CollectionsUtil.areMapsEqual(map1, map2);

					// Then
					expect(result).toBeTrue();
				});

				it('should verify will return false when maps are different reference and different size', () => {
					// Given
					const map1 = new Map<string, any>([
						['users', ['aUser', 'bUser', 'cUser']]
					]);
					const map2 = new Map<string, any>([
						['holders', ['aHolder', 'bHolder', 'cHolder', 'dHolder']]
					]);

					// When
					const result = CollectionsUtil.areMapsEqual(map1, map2);

					// Then
					expect(result).toBeFalse();
				});

				// eslint-disable-next-line max-len
				it('should verify will return false when maps are different reference, same size, same content, different order', () => {
					// Given
					const map1 = new Map<string, any>([
						['users', ['aUser', 'bUser', 'cUser']],
						[
							'data',
							[
								{ person: 'aPerson', salary: 89087, age: 35 },
								{ person: 'bPerson', salary: 78963, age: 31 },
								{ person: 'cPerson', salary: 70664, age: 37 }
							]
						]
					]);
					const map2 = new Map<string, any>([
						['users', ['cUser', 'bUser', 'aUser']],
						[
							'data',
							[
								{ person: 'aPerson', salary: 89087, age: 35 },
								{ person: 'bPerson', salary: 78963, age: 31 },
								{ person: 'cPerson', salary: 70664, age: 37 }
							]
						]
					]);
					const map3 = new Map<string, any>([
						['users', ['aUser', 'bUser', 'cUser']],
						[
							'data',
							[
								{ person: 'cPerson', salary: 70664, age: 37 },
								{ person: 'bPerson', salary: 78963, age: 31 },
								{ person: 'aPerson', salary: 89087, age: 35 }
							]
						]
					]);

					// When
					const result1 = CollectionsUtil.areMapsEqual(map1, map2);
					const result2 = CollectionsUtil.areMapsEqual(map1, map3);

					// Then
					expect(result1).toBeFalse();
					expect(result2).toBeFalse();
				});

				it('should verify will return false when maps are different reference, same size and different content', () => {
					// Given
					const map1 = new Map<string, any>([
						['users', ['aUser', 'bUser', 'cUser']]
					]);
					const map2 = new Map<string, any>([
						['users', ['aUser', 'bUser', 'dUser']]
					]);
					const map3 = new Map<string, any>([
						['holders', ['aHolder', 'cHolder', 'dHolder']]
					]);
					const map4 = new Map<string, any>([
						['val0', 1],
						['val2', 2],
						['val3', 3],
						['val-undefined', undefined]
					]);
					const map5 = new Map<string, any>([
						['val0', 1],
						['val2', 2],
						['val3', 3],
						['val4', 4]
					]);

					// When
					const result1 = CollectionsUtil.areMapsEqual(map1, map2);
					const result2 = CollectionsUtil.areMapsEqual(map1, map3);
					const result3 = CollectionsUtil.areMapsEqual(map4, map5);

					// Then
					expect(result1).toBeFalse();
					expect(result2).toBeFalse();
					expect(result3).toBeFalse();
				});

				it('should verify will return true when maps are different reference, same size and same content', () => {
					// Given
					const map1 = new Map<string, any>([
						['users', ['aUser', 'bUser', 'cUser']],
						[
							'data',
							new Map<string, any>([
								['emails', ['aEmail', 'bEmail', 'cEmail']],
								[
									'payments',
									[
										{ month: 'June', salary: 88900 },
										{ month: 'July', salary: 98431 }
									]
								]
							])
						]
					]);
					const map2 = new Map<string, any>([
						['users', ['aUser', 'bUser', 'cUser']],
						[
							'data',
							new Map<string, any>([
								['emails', ['aEmail', 'bEmail', 'cEmail']],
								[
									'payments',
									[
										{ month: 'June', salary: 88900 },
										{ month: 'July', salary: 98431 }
									]
								]
							])
						]
					]);
					const map3 = new Map<string, any>([['users', 'aUser']]);
					const map4 = new Map<string, any>([['users', 'aUser']]);

					// When
					const result1 = CollectionsUtil.areMapsEqual(map1, map2);
					const result2 = CollectionsUtil.areMapsEqual(map3, map4);

					// Then
					expect(result1).toBeTrue();
					expect(result2).toBeTrue();
				});
			});

			describe('|interpolateString|', () => {
				it('should verify will interpolate provided string replacers', () => {
					// Given
					const text = 'User %s want to delete entity %s.';

					// When
					const res = CollectionsUtil.interpolateString(text, 'John', '25');

					// Then
					expect(res).toEqual('User John want to delete entity 25.');
				});

				it('should verify will interpolate provided Replacer<string> replacers', () => {
					// Given
					const text =
						'Error {0} on line [1] because http request "%s%" failure.';

					// When
					const res = CollectionsUtil.interpolateString(
						text,
						{ searchValue: '{0}', replaceValue: 'HttpResponseError' },
						{ searchValue: '[1]', replaceValue: '27' },
						{ searchValue: '%s%', replaceValue: 'http://xy.com/api/entity/29' }
					);

					// Then
					expect(res).toEqual(
						'Error HttpResponseError on line 27 because http request "http://xy.com/api/entity/29" failure.'
					);
				});
			});
		});
	});
});
