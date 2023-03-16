/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable, OnDestroy, Type } from '@angular/core';
import { HttpStatusCode } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';

import { Subscription } from 'rxjs';

import { CallFake } from '../../../unit-testing';

import { CollectionsUtil } from '../../../utils';

import { TaurusObject } from '../../object';

import { generateErrorCode, ServiceHttpErrorCodes } from '../../error';

import { ErrorCodes, TaurusBaseApiService } from './taurus-base-api-service.model';

@Injectable()
class DummyApiService extends TaurusBaseApiService<DummyApiService> implements OnDestroy {
    /**
     * @inheritDoc
     */
    static override readonly CLASS_NAME: string = 'DummyApiService';

    /**
     * @inheritDoc
     */
    static override readonly PUBLIC_NAME: string = 'Dummy-Api-Service';

    constructor() {
        super(DummyApiService.CLASS_NAME);

        this.registerErrorCodes(DummyApiService);
    }

    override dispose(): void {
        super.dispose();
    }

    override ngOnDestroy(): void {
        super.ngOnDestroy();
    }

    override cleanSubscriptions(): void {
        super.cleanSubscriptions();
    }

    override removeSubscriptionRef(subscriptionRef: Subscription): boolean {
        return super.removeSubscriptionRef(subscriptionRef);
    }

    override registerErrorCodes(service: Type<DummyApiService>): void {
        super.registerErrorCodes(service);
    }

    loadData(): void {
        this._doLoad();
    }

    modifyAssets(): void {
        this.doModify();
    }

    protected doModify(): void {
        // No-ops.
    }

    private _doLoad(): void {
        // No-ops.
    }
}

describe('TaurusBaseApiService', () => {
    let service: DummyApiService;
    let spyForRegisterErrorCodes: jasmine.Spy;

    beforeEach(() => {
        spyForRegisterErrorCodes = spyOn(DummyApiService.prototype, 'registerErrorCodes').and.callThrough();

        TestBed.configureTestingModule({
            providers: [{ provide: DummyApiService, useClass: DummyApiService }]
        });

        service = TestBed.inject(DummyApiService);
    });

    it('should verify instance is created', () => {
        // Then
        expect(service).toBeDefined();
        expect(service).toBeInstanceOf(DummyApiService);
        expect(service).toBeInstanceOf(TaurusBaseApiService);
        expect(service).toBeInstanceOf(TaurusObject);
    });

    describe('Statics::', () => {
        describe('Properties::', () => {
            describe('|CLASS_NAME|', () => {
                it('should verify the value', () => {
                    // Then
                    expect(DummyApiService.CLASS_NAME).toEqual('DummyApiService');
                });
            });

            describe('|PUBLIC_NAME|', () => {
                it('should verify the value', () => {
                    // Then
                    expect(DummyApiService.PUBLIC_NAME).toEqual('Dummy-Api-Service');
                });
            });
        });
    });

    describe('Properties::', () => {
        describe('|errorCodes|', () => {
            it('should verify value has keys only for public methods (methods that not start with underscore) and names are not in blacklist', () => {
                // Then
                expect(service.errorCodes).toBeDefined();
                expect(service.errorCodes).toBeInstanceOf(Object);
            });

            it('should verify expected keys are present', () => {
                // Then
                const keys = Object.keys(service.errorCodes);
                expect(keys.length).toEqual(3);
                expect(keys.findIndex((k) => k === 'doModify')).toBeGreaterThan(-1);
                expect(keys.findIndex((k) => k === 'modifyAssets')).toBeGreaterThan(-1);
                expect(keys.findIndex((k) => k === 'loadData')).toBeGreaterThan(-1);
            });

            it('should verify values for every public key as provided by intellisense', () => {
                // Then
                const methods: Array<keyof ErrorCodes<DummyApiService>> = ['loadData', 'modifyAssets'];
                const additionalDetails: Array<[keyof ServiceHttpErrorCodes, string]> = [
                    ['All', null],
                    ['BadRequest', `${HttpStatusCode.BadRequest}`],
                    ['Unauthorized', `${HttpStatusCode.Unauthorized}`],
                    ['Forbidden', `${HttpStatusCode.Forbidden}`],
                    ['NotFound', `${HttpStatusCode.NotFound}`],
                    ['MethodNotAllowed', `${HttpStatusCode.MethodNotAllowed}`],
                    ['Conflict', `${HttpStatusCode.Conflict}`],
                    ['UnprocessableEntity', `${HttpStatusCode.UnprocessableEntity}`],
                    ['InternalServerError', `${HttpStatusCode.InternalServerError}`],
                    ['ServiceUnavailable', `${HttpStatusCode.ServiceUnavailable}`],
                    ['Unknown', 'unknown']
                ];

                for (const method of methods) {
                    const numberOfAvailableErrorCodesPerMethod = Object.keys(service.errorCodes[method]).length;

                    // verify number of available error codes per method is 11
                    expect(numberOfAvailableErrorCodesPerMethod).toEqual(13);

                    for (const [key, code] of additionalDetails) {
                        // verify every error code is of the expected pattern
                        expect(service.errorCodes[method][key]).toEqual(
                            generateErrorCode(DummyApiService.CLASS_NAME, DummyApiService.PUBLIC_NAME, method, code)
                        );
                    }
                }
            });
        });

        describe('|objectUUID|', () => {
            it('should verify value is DummyApiService', () => {
                // Given
                spyOn(CollectionsUtil, 'generateObjectUUID').and.callFake((value) => value);

                // When
                service = new DummyApiService();

                // Then
                expect(service.objectUUID).toEqual('DummyApiService');
            });

            it('should verify value is TaurusBaseApiService', () => {
                // Given
                spyOn(CollectionsUtil, 'generateObjectUUID').and.callFake((value) => value);

                // When
                // @ts-ignore
                service = new TaurusBaseApiService();

                // Then
                expect(service.objectUUID).toEqual('TaurusBaseApiService');
            });
        });
    });

    describe('Methods::', () => {
        describe('|registerErrorCodes|', () => {
            it('should verify method is executed during the class initialization', () => {
                // Then
                expect(spyForRegisterErrorCodes).toHaveBeenCalled();
            });

            it('should verify thrown error will log in console', () => {
                // Given
                spyOn(CollectionsUtil, 'isFunction').and.throwError(new Error('Random Error'));
                const consoleSpy = spyOn(console, 'error').and.callFake(CallFake);

                // When
                service = new DummyApiService();

                // Then
                expect(consoleSpy).toHaveBeenCalledWith('Cannot register Service Error Codes!');
            });
        });
    });
});
