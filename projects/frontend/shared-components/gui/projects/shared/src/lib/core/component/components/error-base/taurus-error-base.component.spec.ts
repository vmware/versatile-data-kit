/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { generateErrorCodes } from '../../../../unit-testing';

import { ErrorCodes, ErrorRecord } from '../../../../common';

import { TaurusErrorBaseComponent } from './taurus-error-base.component';

@Component({
    selector: 'shared-taurus-error-base-subclass-component',
    template: ''
})
// eslint-disable-next-line @angular-eslint/component-class-suffix
class TaurusErrorBaseComponentStub extends TaurusErrorBaseComponent {
    /**
     * @inheritDoc
     */
    static override readonly CLASS_NAME: string = 'TaurusErrorBaseComponentStub';

    /**
     * @inheritDoc
     */
    static override readonly PUBLIC_NAME: string = 'Taurus-Error-Base-Component-Stub';

    constructor() {
        super(TaurusErrorBaseComponentStub.CLASS_NAME);
    }
}

describe('TaurusErrorBaseComponent', () => {
    let randomServiceStub: jasmine.SpyObj<{ load: () => void; errorCodes: ErrorCodes<{ load: () => void }> }>;

    let fixture: ComponentFixture<TaurusErrorBaseComponentStub>;
    let component: TaurusErrorBaseComponentStub;

    beforeEach(() => {
        randomServiceStub = jasmine.createSpyObj<{ load: () => void; errorCodes: ErrorCodes<{ load: () => void }> }>('randomServiceStub', [
            'load'
        ]);

        TestBed.configureTestingModule({
            declarations: [TaurusErrorBaseComponentStub],
            schemas: [CUSTOM_ELEMENTS_SCHEMA]
        });

        fixture = TestBed.createComponent(TaurusErrorBaseComponentStub);
        component = fixture.componentInstance;
    });

    it('should verify component is created', () => {
        // When
        const component1 = new TaurusErrorBaseComponent();

        // Then
        expect(component).toBeDefined();
        expect(component).toBeInstanceOf(TaurusErrorBaseComponentStub);
        expect(component).toBeInstanceOf(TaurusErrorBaseComponent);
        expect(component1).toBeDefined();
        expect(component1).toBeInstanceOf(TaurusErrorBaseComponent);
    });

    describe('Angular lifecycle hooks::', () => {
        describe('|ngOnDestroy|', () => {
            it('should verify will dispose error records in error store', () => {
                // Given
                const spyErrorStoreDispose = spyOn(component.errors, 'dispose').and.callThrough();

                // When
                fixture.destroy();

                // Then
                expect(spyErrorStoreDispose).toHaveBeenCalled();
            });
        });
    });

    describe('Methods::', () => {
        describe('|generateErrorCode|', () => {
            it('should verify will return error code', () => {
                // When
                // @ts-ignore
                const errorCode = component.generateErrorCode('ClassName', 'Public-Name', 'methodName', 'unknown');

                // Then
                expect(errorCode).toEqual('ClassName_Public-Name_methodName_unknown');
            });
        });

        describe('|processServiceRequestError|', () => {
            it('should verify will process error and record in local store', () => {
                // Given
                const error = new Error('Random Error');
                const spyErrorRecord = spyOn(component.errors, 'record').and.callThrough();

                generateErrorCodes(randomServiceStub, ['load'], 'ClassName', 'Public-Name');

                // When
                // @ts-ignore
                component.processServiceRequestError(randomServiceStub.errorCodes.load, error);

                // Then
                expect(spyErrorRecord).toHaveBeenCalledWith({
                    code: randomServiceStub.errorCodes.load.Unknown,
                    objectUUID: component.objectUUID,
                    error
                } as ErrorRecord);
            });
        });
    });
});
