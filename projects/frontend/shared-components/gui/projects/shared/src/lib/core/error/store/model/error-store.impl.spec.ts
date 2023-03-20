/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpErrorResponse } from '@angular/common/http';

import { CallFake } from '../../../../unit-testing';

import { CollectionsUtil } from '../../../../utils';

import { ErrorRecord } from '../../../../common';

import { ErrorStoreImpl, filterErrorRecords } from './error-store.impl';

describe('ErrorStoreImpl', () => {
    let errorCodes: string[];
    let errorRecords: ErrorRecord[];

    beforeEach(() => {
        errorCodes = [
            'SomeCode',
            'SomeCodeRnd_422',
            'SomeCodeRnd_404',
            'SomeDng_404',
            'SomeDngRbg_500',
            'SomeCodeRnd_503',
            'SomeCodeRnd_500',
            'SomeCode_422'
        ];
        errorRecords = [
            {
                code: errorCodes[0],
                error: new Error('Some Error'),
                objectUUID: 'SomeObjectUUID_1'
            },
            {
                code: errorCodes[1],
                error: new HttpErrorResponse({
                    error: new Error('Some Error 2'),
                    status: 422
                }),
                httpStatusCode: 422,
                objectUUID: 'SomeObjectUUID_1'
            },
            {
                code: errorCodes[2],
                error: new HttpErrorResponse({
                    error: new Error('Some Error 3'),
                    status: 404
                }),
                httpStatusCode: 404,
                objectUUID: 'SomeObjectUUID_2'
            },
            {
                code: errorCodes[3],
                error: new Error('Some Error 3'),
                objectUUID: 'SomeObjectUUID_3'
            },
            {
                code: errorCodes[4],
                error: new HttpErrorResponse({
                    error: new Error('Some Error 4'),
                    status: 503
                }),
                httpStatusCode: 503,
                objectUUID: 'SomeObjectUUID_4'
            },
            {
                code: errorCodes[5],
                error: new HttpErrorResponse({
                    error: new Error('Some Error 5'),
                    status: 503
                }),
                httpStatusCode: 503,
                objectUUID: 'SomeObjectUUID_5'
            },
            {
                code: errorCodes[6],
                error: new HttpErrorResponse({
                    error: new Error('Some Error 6'),
                    status: 500
                }),
                httpStatusCode: 500,
                objectUUID: 'SomeObjectUUID_6'
            },
            {
                code: errorCodes[7],
                error: new HttpErrorResponse({
                    error: new Error('Some Error 7'),
                    status: 422
                }),
                httpStatusCode: 422,
                objectUUID: 'SomeObjectUUID_7'
            }
        ];
    });

    it('should verify instance is created', () => {
        // When
        const instance = new ErrorStoreImpl();

        // Then
        expect(instance).toBeDefined();
    });

    it('should verify correct value are assigned', () => {
        // When
        const instance = new ErrorStoreImpl(errorRecords);

        // Then
        expect(instance.records).toBe(errorRecords);
        expect(instance.changeListeners).toEqual([]);
    });

    it('should verify on Nil or missing parameter default values will be assigned', () => {
        // When
        const instance1 = new ErrorStoreImpl();
        const instance2 = new ErrorStoreImpl(null);
        const instance3 = new ErrorStoreImpl(undefined);

        // Then
        expect(instance1.records).toEqual([]);
        expect(instance1.changeListeners).toEqual([]);

        expect(instance2.records).toEqual([]);
        expect(instance2.changeListeners).toEqual([]);

        expect(instance3.records).toEqual([]);
        expect(instance3.changeListeners).toEqual([]);
    });

    describe('Statics::', () => {
        describe('Methods::', () => {
            describe('|of|', () => {
                it('should verify factory method will create instance', () => {
                    // When
                    const instance = ErrorStoreImpl.of(errorRecords);

                    // Then
                    expect(instance).toBeInstanceOf(ErrorStoreImpl);
                    expect(instance.records).toBe(errorRecords);
                    expect(instance.changeListeners).toEqual([]);
                });
            });

            describe('|empty|', () => {
                it('should verify will create empty instance with default values', () => {
                    // When
                    const instance = ErrorStoreImpl.empty();

                    // Then
                    expect(instance).toBeInstanceOf(ErrorStoreImpl);
                    expect(instance.records).toEqual([]);
                    expect(instance.changeListeners).toEqual([]);
                });
            });

            describe('|fromLiteral|', () => {
                it('should verify will invoke method ErrorStoreImpl.cloneDeepErrorRecords', () => {
                    // Given
                    const spyCloneDeepErrorRecords = spyOn(ErrorStoreImpl, 'cloneDeepErrorRecords').and.callThrough();
                    const spyOf = spyOn(ErrorStoreImpl, 'of').and.callThrough();

                    // When
                    const instance = ErrorStoreImpl.fromLiteral(errorRecords);

                    // Then
                    expect(instance.records).toEqual(errorRecords);
                    expect(spyCloneDeepErrorRecords).toHaveBeenCalledWith(errorRecords);
                    expect(spyOf).toHaveBeenCalledWith([
                        jasmine.any(Object),
                        jasmine.any(Object),
                        jasmine.any(Object),
                        jasmine.any(Object),
                        jasmine.any(Object),
                        jasmine.any(Object),
                        jasmine.any(Object),
                        jasmine.any(Object)
                    ]);
                });
            });

            describe('|cloneDeepErrorRecords|', () => {
                it('should verify will clone deep provided ErrorRecords literals', () => {
                    // When
                    const recordsClonedDeep = ErrorStoreImpl.cloneDeepErrorRecords(errorRecords);

                    // Then
                    expect(recordsClonedDeep).toEqual(errorRecords);

                    expect(recordsClonedDeep).not.toBe(errorRecords);
                    for (let i = 0; i < recordsClonedDeep.length; i++) {
                        expect(recordsClonedDeep[i]).not.toBe(errorRecords[i]);
                    }
                });

                it('should verify will return empty Array if Nil parameter is provided', () => {
                    // When
                    const records1 = ErrorStoreImpl.cloneDeepErrorRecords(null);
                    const records2 = ErrorStoreImpl.cloneDeepErrorRecords(undefined);

                    // Then
                    expect(records1).toEqual([]);
                    expect(records2).toEqual([]);
                });
            });
        });
    });

    describe('Methods::', () => {
        let instance: ErrorStoreImpl;
        let spyExecuteChangeListeners: jasmine.Spy;

        // mock times
        let dateNow1: number;
        let dateNow2: number;
        let dateNow3: number;
        let dateNow4: number;
        let dateNow5: number;
        let dateNow6: number;
        let dateNow7: number;
        let dateNow8: number;

        let extraErrorRecords: ErrorRecord[];

        beforeEach(() => {
            dateNow1 = Date.now() - 20000;
            dateNow2 = Date.now() - 10000;
            dateNow3 = Date.now() - 2000;
            dateNow4 = Date.now() - 1000;
            dateNow5 = Date.now() - 500;
            dateNow6 = Date.now() - 250;
            dateNow7 = Date.now() - 100;
            dateNow8 = Date.now() - 50;

            let counter = 0;
            spyOn(CollectionsUtil, 'dateNow').and.callFake(() => {
                switch (++counter) {
                    case 1:
                    case 9:
                        return dateNow1;
                    case 2:
                    case 10:
                        return dateNow2;
                    case 3:
                    case 11:
                        return dateNow3;
                    case 4:
                    case 12:
                        return dateNow4;
                    case 5:
                    case 13:
                        return dateNow5;
                    case 6:
                    case 14:
                        return dateNow6;
                    case 7:
                    case 15:
                        return dateNow7;
                    case 8:
                    case 16:
                        return dateNow8;
                    default:
                        return Date.now() + Math.ceil(Math.random() * 1000);
                }
            });

            // @ts-ignore
            spyExecuteChangeListeners = spyOn(ErrorStoreImpl, '_executeChangeListeners').and.callThrough();

            instance = new ErrorStoreImpl();

            extraErrorRecords = [
                {
                    code: 'SomeCodeBrr_110',
                    error: new HttpErrorResponse({
                        error: new Error('Some Error 110'),
                        status: 404
                    }),
                    httpStatusCode: 404,
                    objectUUID: 'SomeObjectUUID_110'
                },
                {
                    code: 'SomeCodeBrr_120',
                    error: new Error('Some Error 11'),
                    objectUUID: 'SomeObjectUUID_120'
                },
                {
                    code: 'SomeCodeBrr_130',
                    error: new HttpErrorResponse({
                        error: new Error('Some Error 130'),
                        status: 409
                    }),
                    httpStatusCode: 409,
                    objectUUID: 'SomeObjectUUID_130'
                }
            ];
        });

        describe('|hasErrors|', () => {
            it('should verify will return true if ErrorRecords exist', () => {
                // Given
                instance = new ErrorStoreImpl(errorRecords);

                // When
                const value = instance.hasErrors();

                // Then
                expect(value).toBeTrue();
            });

            it('should verify will return false if ErrorRecords does not exist', () => {
                // Given
                instance = new ErrorStoreImpl();

                // When
                const value = instance.hasErrors();

                // Then
                expect(value).toBeFalse();
            });
        });

        describe('|hasCode|', () => {
            it('should verify will return true if code exist', () => {
                // Given
                instance = new ErrorStoreImpl(errorRecords);

                // When
                const value1 = instance.hasCode('RandomCode', 'UnknownCode', errorCodes[0], 'NotExistedCode', errorCodes[1]);
                const value2 = instance.hasCode(errorCodes[0]);
                const value3 = instance.hasCode(errorCodes[1], errorCodes[2]);

                // Then
                expect(value1).toBeTrue();
                expect(value2).toBeTrue();
                expect(value3).toBeTrue();
            });

            it('should verify will return false if code does not exist', () => {
                // Given
                const instance1 = new ErrorStoreImpl(errorRecords);
                const instance2 = new ErrorStoreImpl();

                // When
                const value1 = instance1.hasCode('RandomCode', 'UnknownCode', 'NotExistedCode');
                const value2 = instance1.hasCode('RandomCode');
                const value3 = instance2.hasCode('RandomCode', 'UnknownCode', 'NotExistedCode');
                const value4 = instance2.hasCode('RandomCode');

                // Then
                expect(value1).toBeFalse();
                expect(value2).toBeFalse();
                expect(value3).toBeFalse();
                expect(value4).toBeFalse();
            });
        });

        describe('|hasCodePattern|', () => {
            it('should verify will return true if codePattern exist', () => {
                // Given
                instance = new ErrorStoreImpl(errorRecords);

                // When
                const value1 = instance.hasCodePattern(
                    'RandomCode',
                    'UnknownCode',
                    null,
                    'SomeDng',
                    undefined,
                    'NotExistedCode',
                    errorCodes[1]
                );
                const value2 = instance.hasCodePattern(`${errorCodes[0]}$`);
                const value3 = instance.hasCodePattern(`${errorCodes[1]}$`);
                const value4 = instance.hasCodePattern(`SomeCodeRnd`);
                const value5 = instance.hasCodePattern(`Code$`);
                const value6 = instance.hasCodePattern(`Rnd`);
                const value7 = instance.hasCodePattern(`SomeCode`);

                // Then
                expect(value1).toBeTrue();
                expect(value2).toBeTrue();
                expect(value3).toBeTrue();
                expect(value4).toBeTrue();
                expect(value5).toBeTrue();
                expect(value6).toBeTrue();
                expect(value7).toBeTrue();
            });

            it('should verify will return false if codePattern does not exist', () => {
                // Given
                const instance1 = new ErrorStoreImpl(errorRecords);
                const instance2 = new ErrorStoreImpl();

                // When
                const value1 = instance1.hasCodePattern('RandomCode', undefined, 'UnknownCode', null, 'NotExistedCode');
                const value2 = instance1.hasCodePattern(`${errorCodes[0]}111`);
                const value3 = instance1.hasCodePattern(`SomeCode__`);
                const value4 = instance2.hasCodePattern(`${errorCodes[1]}$`);
                const value5 = instance2.hasCodePattern('RandomCode', null, 'NotExistedCode', `${errorCodes[1]}$`);
                const value6 = instance2.hasCodePattern(`SomeCodeDng`);

                // Then
                expect(value1).toBeFalse();
                expect(value2).toBeFalse();
                expect(value3).toBeFalse();
                expect(value4).toBeFalse();
                expect(value5).toBeFalse();
                expect(value6).toBeFalse();
            });

            it('should verify will throw/catch error and log to console', () => {
                // Given
                instance = new ErrorStoreImpl(errorRecords);
                const error = new SyntaxError('Unsupported Action');
                spyOn(Array.prototype, 'findIndex').and.throwError(error);
                const spyConsoleError = spyOn(console, 'error').and.callFake(CallFake);

                // When/Then
                const found1 = instance.hasCodePattern(errorCodes[2], errorCodes[0]);
                expect(found1).toBeFalse();
                const found2 = instance.hasCodePattern('SomeCodeRnd');
                expect(found2).toBeFalse();

                expect(spyConsoleError).toHaveBeenCalledWith(error);
            });
        });

        describe('|record|', () => {
            it('should verify will record error', () => {
                // Then 1
                expect(instance.records).toEqual([]);

                // When/Then 2
                instance.record(errorRecords[1].code, errorRecords[1].objectUUID, errorRecords[1].error);
                expect(instance.records).toEqual([{ ...errorRecords[1], time: dateNow1, httpStatusCode: null }]);
                instance.record(errorRecords[0]);
                expect(instance.records).toEqual([
                    { ...errorRecords[1], time: dateNow1, httpStatusCode: null },
                    { ...errorRecords[0], time: dateNow2 }
                ]);
                instance.record(errorRecords[2]);
                expect(instance.records).toEqual([
                    { ...errorRecords[1], time: dateNow1, httpStatusCode: null },
                    { ...errorRecords[0], time: dateNow2 },
                    { ...errorRecords[2], time: dateNow3, httpStatusCode: 404 }
                ]);
                instance.record(errorRecords[3].code, errorRecords[3].objectUUID, null);
                expect(instance.records).toEqual([
                    { ...errorRecords[1], time: dateNow1, httpStatusCode: null },
                    { ...errorRecords[0], time: dateNow2 },
                    { ...errorRecords[2], time: dateNow3, httpStatusCode: 404 },
                    { ...errorRecords[3], time: dateNow4, error: null, httpStatusCode: null }
                ]);
                instance.record(errorRecords[4].code, errorRecords[4].objectUUID, errorRecords[4].error, errorRecords[4].httpStatusCode);
                expect(instance.records).toEqual([
                    { ...errorRecords[1], time: dateNow1, httpStatusCode: null },
                    { ...errorRecords[0], time: dateNow2 },
                    { ...errorRecords[2], time: dateNow3, httpStatusCode: 404 },
                    { ...errorRecords[3], time: dateNow4, error: null, httpStatusCode: null },
                    { ...errorRecords[4], time: dateNow5 }
                ]);

                // 5 times during record
                expect(spyExecuteChangeListeners).toHaveBeenCalledTimes(5);
                expect(spyExecuteChangeListeners).toHaveBeenCalledWith(instance, instance.changeListeners);
            });

            it('should verify will replace existing error for same errorCode and objectUUID and apply new time', () => {
                // Then 1
                expect(instance.records).toEqual([]);

                // When/Then 2
                instance.record(errorRecords[1].code, errorRecords[1].objectUUID, errorRecords[1].error);
                expect(instance.records).toEqual([{ ...errorRecords[1], time: dateNow1, httpStatusCode: null }]);
                instance.record(errorRecords[1]);
                expect(instance.records).toEqual([{ ...errorRecords[1], time: dateNow2 }]);
                instance.record(errorRecords[2]);
                expect(instance.records).toEqual([
                    { ...errorRecords[1], time: dateNow2 },
                    { ...errorRecords[2], time: dateNow3, httpStatusCode: 404 }
                ]);
                instance.record(errorRecords[2].code, errorRecords[2].objectUUID, null);
                expect(instance.records).toEqual([
                    { ...errorRecords[1], time: dateNow2 },
                    { ...errorRecords[2], time: dateNow4, error: null, httpStatusCode: null }
                ]);
                instance.record(errorRecords[4].code, errorRecords[4].objectUUID, errorRecords[4].error, errorRecords[4].httpStatusCode);
                expect(instance.records).toEqual([
                    { ...errorRecords[1], time: dateNow2 },
                    { ...errorRecords[2], time: dateNow4, error: null, httpStatusCode: null },
                    { ...errorRecords[4], time: dateNow5 }
                ]);

                // 5 times during record
                expect(spyExecuteChangeListeners).toHaveBeenCalledTimes(5);
                expect(spyExecuteChangeListeners).toHaveBeenCalledWith(instance, instance.changeListeners);
            });
        });

        describe('|removeCode|', () => {
            it('should verify will remove existed error codes', () => {
                // Given
                instance.record(errorRecords[1]);
                instance.record(errorRecords[0]);
                instance.record(errorRecords[3]);
                instance.record(errorRecords[2]);
                instance.record(errorRecords[4]);

                // Then 1
                expect(instance.records).toEqual([
                    { ...errorRecords[1], time: dateNow1 },
                    { ...errorRecords[0], time: dateNow2 },
                    { ...errorRecords[3], time: dateNow3 },
                    { ...errorRecords[2], time: dateNow4 },
                    { ...errorRecords[4], time: dateNow5 }
                ]);

                // When/Then 2
                instance.removeCode(errorCodes[0], errorCodes[4]);
                expect(instance.records).toEqual([
                    { ...errorRecords[1], time: dateNow1 },
                    { ...errorRecords[3], time: dateNow3 },
                    { ...errorRecords[2], time: dateNow4 }
                ]);
                instance.removeCode('SomeCodeRndDng_10');
                expect(instance.records).toEqual([
                    { ...errorRecords[1], time: dateNow1 },
                    { ...errorRecords[3], time: dateNow3 },
                    { ...errorRecords[2], time: dateNow4 }
                ]);
                instance.removeCode(errorCodes[2], errorCodes[0], errorCodes[3]);
                expect(instance.records).toEqual([{ ...errorRecords[1], time: dateNow1 }]);
                instance.removeCode(errorCodes[1], 'SomeCode');
                expect(instance.records).toEqual([]);

                // 5 times during record and 4 times during remove
                expect(spyExecuteChangeListeners).toHaveBeenCalledTimes(9);
                expect(spyExecuteChangeListeners).toHaveBeenCalledWith(instance, instance.changeListeners);
            });

            it('should verify will throw/catch error and log to console', () => {
                // Given
                const error = new SyntaxError('Unsupported Action');
                spyOn(Array.prototype, 'includes').and.throwError(error);
                const spyConsoleError = spyOn(console, 'error').and.callFake(CallFake);

                instance.record(errorRecords[3]);
                instance.record(errorRecords[1]);
                instance.record(errorRecords[4]);
                instance.record(errorRecords[0]);
                instance.record(errorRecords[2]);

                // Then 1
                expect(instance.records).toEqual([
                    { ...errorRecords[3], time: dateNow1 },
                    { ...errorRecords[1], time: dateNow2 },
                    { ...errorRecords[4], time: dateNow3 },
                    { ...errorRecords[0], time: dateNow4 },
                    { ...errorRecords[2], time: dateNow5 }
                ]);

                // When/Then 2
                instance.removeCode(errorCodes[0], errorCodes[4]);
                expect(instance.records).toEqual([
                    { ...errorRecords[3], time: dateNow1 },
                    { ...errorRecords[1], time: dateNow2 },
                    { ...errorRecords[4], time: dateNow3 },
                    { ...errorRecords[0], time: dateNow4 },
                    { ...errorRecords[2], time: dateNow5 }
                ]);
                instance.removeCode(errorCodes[1]);
                expect(instance.records).toEqual([
                    { ...errorRecords[3], time: dateNow1 },
                    { ...errorRecords[1], time: dateNow2 },
                    { ...errorRecords[4], time: dateNow3 },
                    { ...errorRecords[0], time: dateNow4 },
                    { ...errorRecords[2], time: dateNow5 }
                ]);

                expect(spyConsoleError).toHaveBeenCalledWith(error);
                // 5 times during record and 2 times during remove
                expect(spyExecuteChangeListeners).toHaveBeenCalledTimes(7);
            });
        });

        describe('|removeCodePattern|', () => {
            beforeEach(() => {
                // Given
                instance.record(errorRecords[1]);
                instance.record(errorRecords[0]);
                instance.record(errorRecords[3]);
                instance.record(errorRecords[2]);
                instance.record(errorRecords[4]);
                instance.record(errorRecords[6]);
                instance.record(errorRecords[5]);
                instance.record(errorRecords[7]);
            });

            it('should verify will remove existed error codes patterns', () => {
                // Then 1
                expect(instance.records).toEqual([
                    { ...errorRecords[1], time: dateNow1 },
                    { ...errorRecords[0], time: dateNow2 },
                    { ...errorRecords[3], time: dateNow3 },
                    { ...errorRecords[2], time: dateNow4 },
                    { ...errorRecords[4], time: dateNow5 },
                    { ...errorRecords[6], time: dateNow6 },
                    { ...errorRecords[5], time: dateNow7 },
                    { ...errorRecords[7], time: dateNow8 }
                ]);

                // When/Then 2
                instance.removeCodePattern(errorCodes[1], null, errorCodes[3]);
                expect(instance.records).toEqual([
                    { ...errorRecords[0], time: dateNow2 },
                    { ...errorRecords[2], time: dateNow4 },
                    { ...errorRecords[4], time: dateNow5 },
                    { ...errorRecords[6], time: dateNow6 },
                    { ...errorRecords[5], time: dateNow7 },
                    { ...errorRecords[7], time: dateNow8 }
                ]);
                instance.removeCodePattern('SomeCodeRnd$', undefined);
                expect(instance.records).toEqual([
                    { ...errorRecords[0], time: dateNow2 },
                    { ...errorRecords[2], time: dateNow4 },
                    { ...errorRecords[4], time: dateNow5 },
                    { ...errorRecords[6], time: dateNow6 },
                    { ...errorRecords[5], time: dateNow7 },
                    { ...errorRecords[7], time: dateNow8 }
                ]);
                instance.removeCodePattern('SomeCodeRnd');
                expect(instance.records).toEqual([
                    { ...errorRecords[0], time: dateNow2 },
                    { ...errorRecords[4], time: dateNow5 },
                    { ...errorRecords[7], time: dateNow8 }
                ]);
                instance.removeCodePattern(null, 'RandomCodeNotExisting');
                expect(instance.records).toEqual([
                    { ...errorRecords[0], time: dateNow2 },
                    { ...errorRecords[4], time: dateNow5 },
                    { ...errorRecords[7], time: dateNow8 }
                ]);
                instance.removeCodePattern('SomeCode_');
                expect(instance.records).toEqual([
                    { ...errorRecords[0], time: dateNow2 },
                    { ...errorRecords[4], time: dateNow5 }
                ]);
                instance.removeCodePattern(errorCodes[4], 'SomeCode');
                expect(instance.records).toEqual([]);

                // 8 times during record and 6 times during remove
                expect(spyExecuteChangeListeners).toHaveBeenCalledTimes(14);
                expect(spyExecuteChangeListeners).toHaveBeenCalledWith(instance, instance.changeListeners);
            });

            it('should verify will remove regex error codes patterns', () => {
                // Then 1
                expect(instance.records).toEqual([
                    { ...errorRecords[1], time: dateNow1 },
                    { ...errorRecords[0], time: dateNow2 },
                    { ...errorRecords[3], time: dateNow3 },
                    { ...errorRecords[2], time: dateNow4 },
                    { ...errorRecords[4], time: dateNow5 },
                    { ...errorRecords[6], time: dateNow6 },
                    { ...errorRecords[5], time: dateNow7 },
                    { ...errorRecords[7], time: dateNow8 }
                ]);

                // When/Then 2
                instance.removeCodePattern(`SomeCodeRnd_4\\d\\d`);
                expect(instance.records).toEqual([
                    { ...errorRecords[0], time: dateNow2 },
                    { ...errorRecords[3], time: dateNow3 },
                    { ...errorRecords[4], time: dateNow5 },
                    { ...errorRecords[6], time: dateNow6 },
                    { ...errorRecords[5], time: dateNow7 },
                    { ...errorRecords[7], time: dateNow8 }
                ]);
                instance.removeCodePattern('SomeCodeRnd$');
                expect(instance.records).toEqual([
                    { ...errorRecords[0], time: dateNow2 },
                    { ...errorRecords[3], time: dateNow3 },
                    { ...errorRecords[4], time: dateNow5 },
                    { ...errorRecords[6], time: dateNow6 },
                    { ...errorRecords[5], time: dateNow7 },
                    { ...errorRecords[7], time: dateNow8 }
                ]);
                instance.removeCodePattern('SomeCodeRnd');
                expect(instance.records).toEqual([
                    { ...errorRecords[0], time: dateNow2 },
                    { ...errorRecords[3], time: dateNow3 },
                    { ...errorRecords[4], time: dateNow5 },
                    { ...errorRecords[7], time: dateNow8 }
                ]);
                instance.removeCodePattern('RandomCodeNotExisting');
                expect(instance.records).toEqual([
                    { ...errorRecords[0], time: dateNow2 },
                    { ...errorRecords[3], time: dateNow3 },
                    { ...errorRecords[4], time: dateNow5 },
                    { ...errorRecords[7], time: dateNow8 }
                ]);
                instance.removeCodePattern(errorCodes[4], 'SomeCode');
                expect(instance.records).toEqual([{ ...errorRecords[3], time: dateNow3 }]);
                instance.removeCodePattern('Dng_404');
                expect(instance.records).toEqual([]);

                // 8 times during record and 6 times during remove
                expect(spyExecuteChangeListeners).toHaveBeenCalledTimes(14);
                expect(spyExecuteChangeListeners).toHaveBeenCalledWith(instance, instance.changeListeners);
            });

            it('should verify will throw/catch error and log to console', () => {
                // Given
                const error = new SyntaxError('Unsupported Action');
                spyOn(Array.prototype, 'filter').and.throwError(error);
                const spyConsoleError = spyOn(console, 'error').and.callFake(CallFake);

                // Then 1
                expect(instance.records).toEqual([
                    { ...errorRecords[1], time: dateNow1 },
                    { ...errorRecords[0], time: dateNow2 },
                    { ...errorRecords[3], time: dateNow3 },
                    { ...errorRecords[2], time: dateNow4 },
                    { ...errorRecords[4], time: dateNow5 },
                    { ...errorRecords[6], time: dateNow6 },
                    { ...errorRecords[5], time: dateNow7 },
                    { ...errorRecords[7], time: dateNow8 }
                ]);

                // When/Then 2
                instance.removeCodePattern(errorCodes[4], errorCodes[2]);
                expect(instance.records).toEqual([
                    { ...errorRecords[1], time: dateNow1 },
                    { ...errorRecords[0], time: dateNow2 },
                    { ...errorRecords[3], time: dateNow3 },
                    { ...errorRecords[2], time: dateNow4 },
                    { ...errorRecords[4], time: dateNow5 },
                    { ...errorRecords[6], time: dateNow6 },
                    { ...errorRecords[5], time: dateNow7 },
                    { ...errorRecords[7], time: dateNow8 }
                ]);
                instance.removeCodePattern(errorCodes[3]);
                expect(instance.records).toEqual([
                    { ...errorRecords[1], time: dateNow1 },
                    { ...errorRecords[0], time: dateNow2 },
                    { ...errorRecords[3], time: dateNow3 },
                    { ...errorRecords[2], time: dateNow4 },
                    { ...errorRecords[4], time: dateNow5 },
                    { ...errorRecords[6], time: dateNow6 },
                    { ...errorRecords[5], time: dateNow7 },
                    { ...errorRecords[7], time: dateNow8 }
                ]);

                expect(spyConsoleError).toHaveBeenCalledWith(error);
                expect(spyConsoleError).toHaveBeenCalledTimes(3);
                // 8 times during record and 2 times during remove
                expect(spyExecuteChangeListeners).toHaveBeenCalledTimes(10);
            });
        });

        describe('|findRecords|', () => {
            beforeEach(() => {
                // Given
                instance.record(errorRecords[4]);
                instance.record(errorRecords[0]);
                instance.record(errorRecords[2]);
                instance.record(errorRecords[3]);
                instance.record(errorRecords[1]);
                instance.record(errorRecords[7]);
            });

            it('should verify will return Array of ErrorRecord empty or filled with elements if found', () => {
                // Then 1
                expect(instance.records).toEqual([
                    { ...errorRecords[4], time: dateNow1 },
                    { ...errorRecords[0], time: dateNow2 },
                    { ...errorRecords[2], time: dateNow3 },
                    { ...errorRecords[3], time: dateNow4 },
                    { ...errorRecords[1], time: dateNow5 },
                    { ...errorRecords[7], time: dateNow6 }
                ]);

                // When/Then 2
                const found1 = instance.findRecords(errorCodes[0], errorCodes[3]);
                expect(found1).toEqual([
                    { ...errorRecords[0], time: dateNow2 },
                    { ...errorRecords[3], time: dateNow4 }
                ]);
                const found2 = instance.findRecords('SomeRandomCode');
                expect(found2).toEqual([]);
                const found3 = instance.findRecords(errorCodes[4]);
                expect(found3).toEqual([{ ...errorRecords[4], time: dateNow1 }]);
            });
        });

        describe('|findRecordsByPattern|', () => {
            beforeEach(() => {
                // Given
                instance.record(errorRecords[0]);
                instance.record(errorRecords[4]);
                instance.record(errorRecords[3]);
                instance.record(errorRecords[2]);
                instance.record(errorRecords[1]);
                instance.record(errorRecords[7]);
            });

            it('should verify will return Array of ErrorRecord empty or filled with elements if found', () => {
                // Then 1
                expect(instance.records).toEqual([
                    { ...errorRecords[0], time: dateNow1 },
                    { ...errorRecords[4], time: dateNow2 },
                    { ...errorRecords[3], time: dateNow3 },
                    { ...errorRecords[2], time: dateNow4 },
                    { ...errorRecords[1], time: dateNow5 },
                    { ...errorRecords[7], time: dateNow6 }
                ]);

                // When/Then 2
                const found1 = instance.findRecordsByPattern(errorCodes[2], undefined, errorCodes[1], null);
                expect(found1).toEqual([
                    { ...errorRecords[2], time: dateNow4 },
                    { ...errorRecords[1], time: dateNow5 }
                ]);
                const found2 = instance.findRecordsByPattern('SomeCodeRnd');
                expect(found2).toEqual([
                    { ...errorRecords[2], time: dateNow4 },
                    { ...errorRecords[1], time: dateNow5 }
                ]);
                const found3 = instance.findRecordsByPattern('SomeCodeRnd$');
                expect(found3).toEqual([]);
                const found4 = instance.findRecordsByPattern('SomeCode');
                expect(found4).toEqual([
                    { ...errorRecords[0], time: dateNow1 },
                    { ...errorRecords[2], time: dateNow4 },
                    { ...errorRecords[1], time: dateNow5 },
                    { ...errorRecords[7], time: dateNow6 }
                ]);
            });

            it('should verify will throw/catch error and log to console', () => {
                // Given
                const error = new SyntaxError('Unsupported Action');
                spyOn(Array.prototype, 'filter').and.throwError(error);
                const spyConsoleError = spyOn(console, 'error').and.callFake(CallFake);

                // Then 1
                expect(instance.records).toEqual([
                    { ...errorRecords[0], time: dateNow1 },
                    { ...errorRecords[4], time: dateNow2 },
                    { ...errorRecords[3], time: dateNow3 },
                    { ...errorRecords[2], time: dateNow4 },
                    { ...errorRecords[1], time: dateNow5 },
                    { ...errorRecords[7], time: dateNow6 }
                ]);

                // When/Then 2
                const found1 = instance.findRecordsByPattern(errorCodes[2], null, errorCodes[0]);
                expect(found1).toEqual([]);
                const found2 = instance.findRecordsByPattern('SomeCodeRnd');
                expect(found2).toEqual([]);

                expect(spyConsoleError).toHaveBeenCalledWith(error);
            });
        });

        describe('|distinctErrorRecords|', () => {
            beforeEach(() => {
                // Given
                instance.record(errorRecords[0]);
                instance.record(errorRecords[1]);
                instance.record(errorRecords[4]);
                instance.record(errorRecords[2]);
                instance.record(errorRecords[3]);
                instance.record(errorRecords[6]);
                instance.record(errorRecords[5]);
                instance.record(errorRecords[7]);
            });

            it('should verify will return Array of ErrorRecord from store records that are not equal by value to provided Array of ErrorRecord', () => {
                // Given
                const instance2 = new ErrorStoreImpl();
                instance2.record(errorRecords[0]);
                instance2.record(errorRecords[1]);
                instance2.record(errorRecords[4]);
                instance2.record(errorRecords[2]);
                instance2.record(errorRecords[3]);
                instance2.record(errorRecords[6]);
                instance2.record(errorRecords[5]);
                instance2.record(errorRecords[7]);
                instance2.record(extraErrorRecords[0]);
                instance2.record(extraErrorRecords[2]);
                instance2.record(extraErrorRecords[1]);

                // When
                const value1 = instance.distinctErrorRecords(instance2.records);
                const value2 = instance.distinctErrorRecords(null);
                const value3 = instance.distinctErrorRecords(undefined);
                const value4 = instance.distinctErrorRecords([]);
                const value5 = instance2.distinctErrorRecords(instance.records);

                // Then
                expect(value1).toEqual([]);
                expect(value2).toEqual([
                    instance.records[0],
                    instance.records[1],
                    instance.records[2],
                    instance.records[3],
                    instance.records[4],
                    instance.records[5],
                    instance.records[6],
                    instance.records[7]
                ]);
                expect(value3).toEqual([
                    instance.records[0],
                    instance.records[1],
                    instance.records[2],
                    instance.records[3],
                    instance.records[4],
                    instance.records[5],
                    instance.records[6],
                    instance.records[7]
                ]);
                expect(value4).toEqual([
                    instance.records[0],
                    instance.records[1],
                    instance.records[2],
                    instance.records[3],
                    instance.records[4],
                    instance.records[5],
                    instance.records[6],
                    instance.records[7]
                ]);
                expect(value5).toEqual([instance2.records[8], instance2.records[9], instance2.records[10]]);
            });
        });

        describe('|purge|', () => {
            beforeEach(() => {
                // Given
                instance.record(errorRecords[2]);
                instance.record(errorRecords[0]);
                instance.record(errorRecords[4]);
                instance.record(errorRecords[1]);
                instance.record(errorRecords[3]);
                instance.record(errorRecords[6]);
                instance.record(errorRecords[5]);
                instance.record(errorRecords[7]);
            });

            it('should verify purge will not trigger change listeners and wont add anything if both ErrorStore are equal', () => {
                // Given
                const instance2 = new ErrorStoreImpl();
                instance2.record(errorRecords[2]);
                instance2.record(errorRecords[0]);
                instance2.record(errorRecords[4]);
                instance2.record(errorRecords[1]);
                instance2.record(errorRecords[3]);
                instance2.record(errorRecords[6]);
                instance2.record(errorRecords[5]);
                instance2.record(errorRecords[7]);

                // When
                instance.purge(instance2);

                // Then
                expect(instance.records).toEqual([
                    { ...errorRecords[2], time: dateNow1 },
                    { ...errorRecords[0], time: dateNow2 },
                    { ...errorRecords[4], time: dateNow3 },
                    { ...errorRecords[1], time: dateNow4 },
                    { ...errorRecords[3], time: dateNow5 },
                    { ...errorRecords[6], time: dateNow6 },
                    { ...errorRecords[5], time: dateNow7 },
                    { ...errorRecords[7], time: dateNow8 }
                ]);
                // 16 times during record, 8 for instance and 8 for instance2
                expect(spyExecuteChangeListeners).toHaveBeenCalledTimes(16);
            });

            it('should verify purge will trigger change listeners and will add ErrorRecords from injected ErrorStore to invoker', () => {
                // Given
                const instance2 = new ErrorStoreImpl();
                instance2.record(extraErrorRecords[2]);
                instance2.record(extraErrorRecords[0]);
                instance2.record(extraErrorRecords[1]);

                // When
                instance.purge(instance2);

                // Then
                expect(instance.records).toEqual([
                    { ...extraErrorRecords[2], time: dateNow1 },
                    { ...extraErrorRecords[0], time: dateNow2 },
                    { ...extraErrorRecords[1], time: dateNow3 }
                ]);
                // 11 times during record, 8 for instance and 3 for instance2 and 1 for purge
                expect(spyExecuteChangeListeners).toHaveBeenCalledTimes(12);
            });
        });

        describe('|onChange|', () => {
            it('should verify will add listener for change in local repository', () => {
                // Given
                const listener1: (store: ErrorStoreImpl) => void = (store: ErrorStoreImpl) => {
                    expect(store).toBe(instance);
                };
                const listener2: (store: ErrorStoreImpl) => void = (store: ErrorStoreImpl) => {
                    expect(store).toBe(instance);
                };
                const listener3: (store: ErrorStoreImpl) => void = null;
                const listener4: (store: ErrorStoreImpl) => void = undefined;

                // When
                instance.onChange(listener1);
                instance.onChange(listener2);
                instance.onChange(listener3);
                instance.onChange(listener4);

                // Then
                expect(instance.changeListeners.length).toEqual(2);
                expect(instance.changeListeners[0]).toBe(listener1);
                expect(instance.changeListeners[1]).toBe(listener2);
            });

            it('should verify attached listeners are executed on ErrorRecord recording', () => {
                // Given
                const error = new Error('Thrown Error Executed Listener');
                const listener1 = jasmine.createSpy<(_store: ErrorStoreImpl) => void>('listener1').and.callFake(CallFake);
                const listener2 = jasmine.createSpy<(_store: ErrorStoreImpl) => void>('listener2').and.throwError(error);
                const spyConsoleError = spyOn(console, 'error').and.callFake(CallFake);
                instance.onChange(listener1);
                instance.onChange(listener2);

                // When
                instance.record(errorRecords[0]);

                // Then
                expect(listener1).toHaveBeenCalledWith(instance);
                expect(listener2).toHaveBeenCalledWith(instance);
                expect(spyConsoleError).toHaveBeenCalledWith(`Taurus ErrorStore failed to execute change listeners`, error);
            });
        });

        describe('|dispose|', () => {
            it('should verify will invoke correct methods', () => {
                // Given
                const listener1: (store: ErrorStoreImpl) => void = (_store: ErrorStoreImpl) => {
                    // No-op.
                };
                const listener2: (store: ErrorStoreImpl) => void = (_store: ErrorStoreImpl) => {
                    // No-op.
                };

                instance = new ErrorStoreImpl(errorRecords);
                instance.onChange(listener1);
                instance.onChange(listener2);

                const spyClear = spyOn(instance, 'clear').and.callThrough();

                // Then 1
                expect(instance.records).toEqual(errorRecords);
                expect(instance.changeListeners).toEqual([listener1, listener2]);

                // When
                instance.dispose();

                // Then 2
                expect(spyClear).toHaveBeenCalledTimes(1);
                expect(instance.records).toEqual([]);
                expect(instance.changeListeners).toEqual([]);
            });
        });

        describe('|clear|', () => {
            it('should verify will clear ErrorRecord items from records', () => {
                instance = new ErrorStoreImpl(extraErrorRecords);

                // Then 1
                expect(instance.records).toEqual(extraErrorRecords);

                // When
                instance.clear();

                // Then 2
                expect(instance.records).toEqual([]);
            });
        });

        describe('|toLiteral|', () => {
            it('should verify will return Array of ErrorRecord shallow cloned', () => {
                instance = new ErrorStoreImpl(extraErrorRecords);

                // Then 1
                expect(instance.records).toEqual(extraErrorRecords);

                // When
                const literals = instance.toLiteral();

                // Then 2
                expect(literals).toEqual(extraErrorRecords);
                expect(literals).not.toBe(extraErrorRecords);
                for (let i = 0; i < literals.length; i++) {
                    expect(literals[i]).toBe(extraErrorRecords[i]);
                }
            });
        });

        describe('|toLiteralCloneDeep|', () => {
            it('should verify will return Array of ErrorRecord deep cloned', () => {
                instance = new ErrorStoreImpl(extraErrorRecords);

                // Then 1
                expect(instance.records).toEqual(extraErrorRecords);

                // When
                const literals = instance.toLiteralCloneDeep();

                // Then 2
                expect(literals).toEqual(extraErrorRecords);
                expect(literals).not.toBe(extraErrorRecords);
                for (let i = 0; i < literals.length; i++) {
                    expect(literals[i]).not.toBe(extraErrorRecords[i]);
                }
            });
        });

        describe('|copy|', () => {
            it('should verify will return new instance of ErrorStoreImpl with existing ErrorRecord', () => {
                instance = new ErrorStoreImpl(extraErrorRecords);

                // Then 1
                expect(instance.records).toEqual(extraErrorRecords);

                // When
                const newInstance = instance.copy();

                // Then 2
                expect(newInstance).toBeInstanceOf(ErrorStoreImpl);
                expect(newInstance.records).toEqual(extraErrorRecords);
                expect(newInstance.records).not.toBe(extraErrorRecords);
                for (let i = 0; i < newInstance.records.length; i++) {
                    expect(newInstance.records[i]).toBe(extraErrorRecords[i]);
                }
            });
        });

        describe('|equals|', () => {
            it('should verify will return true when both instances of ErrorStoreImpl have same content using deep comparison', () => {
                // Given
                const instance1 = new ErrorStoreImpl();
                instance1.record(errorRecords[0]);
                instance1.record(errorRecords[1]);
                instance1.record(errorRecords[2]);
                instance1.record(errorRecords[3]);
                instance1.record(errorRecords[4]);
                instance1.record(errorRecords[5]);
                instance1.record(errorRecords[6]);
                instance1.record(errorRecords[7]);

                const instance2 = new ErrorStoreImpl();
                instance2.record(errorRecords[0]);
                instance2.record(errorRecords[1]);
                instance2.record(errorRecords[2]);
                instance2.record(errorRecords[3]);
                instance2.record(errorRecords[4]);
                instance2.record(errorRecords[5]);
                instance2.record(errorRecords[6]);
                instance2.record(errorRecords[7]);

                const instance3 = new ErrorStoreImpl();
                const instance4 = new ErrorStoreImpl();

                // When
                const areEqual1 = instance1.equals(instance2);
                const areEqual2 = instance3.equals(instance3);

                // Then 2
                expect(areEqual1).toBeTrue();
                expect(instance1.records).toEqual(instance2.records);
                expect(instance1.records).not.toBe(instance2.records);
                for (let i = 0; i < instance1.records.length; i++) {
                    expect(instance1.records[i]).not.toBe(instance2.records[i]);
                }

                expect(areEqual2).toBeTrue();
                expect(instance3.records).toEqual(instance4.records);
            });

            it('should verify will return false when injected ErrorStoreImpl is Nil', () => {
                // Given
                const instance1 = new ErrorStoreImpl();
                instance1.record(errorRecords[0]);
                instance1.record(errorRecords[1]);
                instance1.record(errorRecords[2]);

                // When
                const areEqual1 = instance1.equals(null);
                const areEqual2 = instance1.equals(undefined);

                // Then
                expect(areEqual1).toBeFalse();
                expect(areEqual2).toBeFalse();
            });

            it('should verify will return false when both instances of ErrorStoreImpl have different ErrorRecord size', () => {
                // Given
                const instance1 = new ErrorStoreImpl();
                instance1.record(errorRecords[0]);
                instance1.record(errorRecords[1]);
                instance1.record(errorRecords[2]);

                const instance2 = new ErrorStoreImpl();
                instance2.record(extraErrorRecords[0]);
                instance2.record(extraErrorRecords[1]);

                // When
                const areEqual1 = instance1.equals(instance2);

                // Then 2
                expect(areEqual1).toBeFalse();
                expect(instance1.records).not.toEqual(instance2.records);
            });

            it('should verify will return false when both instances of ErrorStoreImpl have same ErrorRecord size but for one code is different', () => {
                // Given
                const instance1 = new ErrorStoreImpl();
                instance1.record(errorRecords[0]);
                instance1.record(errorRecords[1]);
                instance1.record(errorRecords[2]);
                instance1.record(errorRecords[3]);
                instance1.record(errorRecords[4]);
                instance1.record(errorRecords[5]);
                instance1.record(errorRecords[6]);
                instance1.record(errorRecords[7]);

                const instance2 = new ErrorStoreImpl();
                instance2.record(errorRecords[0]);
                instance2.record(errorRecords[1]);
                instance2.record(errorRecords[2]);
                instance2.record(extraErrorRecords[0]);
                instance2.record(errorRecords[4]);
                instance2.record(errorRecords[5]);
                instance2.record(errorRecords[6]);
                instance2.record(errorRecords[7]);

                // When
                const areEqual1 = instance1.equals(instance2);

                // Then 2
                expect(areEqual1).toBeFalse();
                expect(instance1.records).not.toEqual(instance2.records);
            });

            it('should verify will return false when both instances of ErrorStoreImpl have same ErrorRecord size but for one objectUUID is different', () => {
                // Given
                const instance1 = new ErrorStoreImpl();
                instance1.record(errorRecords[0]);
                instance1.record(errorRecords[1]);
                instance1.record(errorRecords[2]);
                instance1.record(errorRecords[3]);
                instance1.record(errorRecords[4]);
                instance1.record(errorRecords[5]);
                instance1.record(errorRecords[6]);
                instance1.record(errorRecords[7]);

                const instance2 = new ErrorStoreImpl();
                instance2.record(errorRecords[0]);
                instance2.record(errorRecords[1]);
                instance2.record(errorRecords[2]);
                instance2.record(errorRecords[3]);
                instance2.record(errorRecords[4]);
                instance2.record({ ...errorRecords[5], objectUUID: 'newObjectUUID_not_overlap' });
                instance2.record(errorRecords[6]);
                instance2.record(errorRecords[7]);

                // When
                const areEqual1 = instance1.equals(instance2);

                // Then 2
                expect(areEqual1).toBeFalse();
                expect(instance1.records).not.toEqual(instance2.records);
            });

            it('should verify will return false when both instances of ErrorStoreImpl have same ErrorRecord size but for one time is different', () => {
                // Given
                const instance1 = new ErrorStoreImpl();
                instance1.record(errorRecords[0]);
                instance1.record(errorRecords[1]);
                instance1.record(errorRecords[2]);
                instance1.record(errorRecords[3]);
                instance1.record(errorRecords[4]);
                instance1.record(errorRecords[5]);
                instance1.record(errorRecords[6]);
                instance1.record(errorRecords[7]);

                const instance2 = new ErrorStoreImpl();
                instance2.record(errorRecords[0]);
                instance2.record(errorRecords[1]);
                instance2.record(errorRecords[2]);
                instance2.record(errorRecords[3]);
                instance2.record(errorRecords[4]);
                instance2.record(errorRecords[5]);
                instance2.record(errorRecords[6]);
                instance2.record(errorRecords[7]);
                // extra record that applies new time for record 6
                instance2.record(errorRecords[6]);

                // When
                const areEqual1 = instance1.equals(instance2);

                // Then 2
                expect(areEqual1).toBeFalse();
                expect(instance1.records).not.toEqual(instance2.records);
            });

            it('should verify will return false when both instances of ErrorStoreImpl have same ErrorRecord size but for one error is different v1', () => {
                // Given
                const instance1 = new ErrorStoreImpl();
                instance1.record(errorRecords[0]);
                instance1.record(errorRecords[1]);
                instance1.record(errorRecords[2]);
                instance1.record(errorRecords[3]);
                instance1.record(errorRecords[4]);
                instance1.record(errorRecords[5]);
                instance1.record(errorRecords[6]);
                instance1.record(errorRecords[7]);

                const instance2 = new ErrorStoreImpl();
                instance2.record(errorRecords[0]);
                instance2.record(errorRecords[1]);
                instance2.record({ ...errorRecords[2], error: new Error('New Error Thrown not overlap') });
                instance2.record(errorRecords[3]);
                instance2.record(errorRecords[4]);
                instance2.record(errorRecords[5]);
                instance2.record(errorRecords[6]);
                instance2.record(errorRecords[7]);

                // When
                const areEqual1 = instance1.equals(instance2);

                // Then 2
                expect(areEqual1).toBeFalse();
                expect(instance1.records).not.toEqual(instance2.records);
            });

            it('should verify will return false when both instances of ErrorStoreImpl have same ErrorRecord size but for one error is different v2', () => {
                // Given
                const instance1 = new ErrorStoreImpl();
                instance1.record(errorRecords[0]);
                instance1.record(errorRecords[1]);
                instance1.record(errorRecords[2]);
                instance1.record(errorRecords[3]);
                instance1.record(errorRecords[4]);
                instance1.record(errorRecords[5]);
                instance1.record(errorRecords[6]);
                instance1.record(errorRecords[7]);

                const instance2 = new ErrorStoreImpl();
                instance2.record(errorRecords[0]);
                instance2.record(errorRecords[1]);
                instance2.record(errorRecords[2]);
                instance2.record(errorRecords[3]);
                instance2.record({ ...errorRecords[4], httpStatusCode: 401 });
                instance2.record(errorRecords[5]);
                instance2.record(errorRecords[6]);
                instance2.record(errorRecords[7]);

                // When
                const areEqual1 = instance1.equals(instance2);

                // Then 2
                expect(areEqual1).toBeFalse();
                expect(instance1.records).not.toEqual(instance2.records);
            });
        });
    });
});

describe('filterErrorRecords', () => {
    let errorCodes: string[];
    let errorRecords: ErrorRecord[];

    // mock times
    let dateNow1: number;
    let dateNow2: number;
    let dateNow3: number;
    let dateNow4: number;
    let dateNow5: number;

    beforeEach(() => {
        errorCodes = ['SomeCd', 'SomeCdRnd_1', 'SomeCdRnd_2', 'SomeBng_3', 'SomeBngRbg_4'];
        errorRecords = [
            {
                code: errorCodes[0],
                error: new Error('Some Error'),
                objectUUID: 'SomeObjectUUID_20'
            },
            {
                code: errorCodes[1],
                error: new Error('Some Error 100'),
                objectUUID: 'SomeObjectUUID_20'
            },
            {
                code: errorCodes[2],
                error: new HttpErrorResponse({
                    error: new Error('Some Error 200'),
                    status: 422
                }),
                httpStatusCode: 422,
                objectUUID: 'SomeObjectUUID_30'
            },
            {
                code: errorCodes[3],
                error: new Error('Some Error 300'),
                objectUUID: 'SomeObjectUUID_40'
            },
            {
                code: errorCodes[4],
                error: new HttpErrorResponse({
                    error: new Error('Some Error 400'),
                    status: 500
                }),
                httpStatusCode: 500,
                objectUUID: 'SomeObjectUUID_50'
            }
        ];

        dateNow1 = Date.now() - 35000;
        dateNow2 = Date.now() - 30000;
        dateNow3 = Date.now() - 25000;
        dateNow4 = Date.now() - 20000;
        dateNow5 = Date.now() - 15000;

        let counter = 0;
        spyOn(CollectionsUtil, 'dateNow').and.callFake(() => {
            switch (++counter) {
                case 1:
                    return dateNow1;
                case 2:
                    return dateNow2;
                case 3:
                    return dateNow3;
                case 4:
                    return dateNow4;
                case 5:
                    return dateNow5;
                default:
                    return Date.now() + Math.ceil(Math.random() * 1000);
            }
        });
    });

    it('should verify filters Array of ErrorRecord correctly', () => {
        // Given
        const instance = new ErrorStoreImpl();
        instance.record(errorRecords[0]);
        instance.record(errorRecords[1]);
        instance.record(errorRecords[2]);
        instance.record(errorRecords[3]);
        instance.record(errorRecords[4]);

        // When
        const filteredErrorRecords1 = filterErrorRecords(instance.records, [errorCodes[0], errorCodes[4]]);
        const filteredErrorRecords2 = filterErrorRecords(instance.records, [errorCodes[4]], ['SomeCdRnd', null]);
        const filteredErrorRecords3 = filterErrorRecords(instance.records, [], ['SomeBng$', undefined]);
        const filteredErrorRecords4 = filterErrorRecords(instance.records, null, null);
        const filteredErrorRecords5 = filterErrorRecords(instance.records);

        // Then
        expect(filteredErrorRecords1).toEqual([instance.records[4], instance.records[0]]);
        expect(filteredErrorRecords2).toEqual([instance.records[4], instance.records[2], instance.records[1]]);
        expect(filteredErrorRecords3).toEqual([]);
        expect(filteredErrorRecords4).toEqual([]);
        expect(filteredErrorRecords5).toEqual([]);
    });
});
