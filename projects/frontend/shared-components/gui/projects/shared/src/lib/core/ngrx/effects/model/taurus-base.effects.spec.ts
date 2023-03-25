/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Directive, Injectable } from '@angular/core';
import { TestBed } from '@angular/core/testing';

import { Subject } from 'rxjs';

import { Actions } from '@ngrx/effects';

import { provideMockActions } from '@ngrx/effects/testing';

import { TaurusObject } from '../../../../common';

import { ComponentService } from '../../../component';

import { TaurusBaseEffects } from './taurus-base.effects';

@Injectable()
class TaurusBaseEffectsStub extends TaurusBaseEffects {
    static override readonly CLASS_NAME: string = 'TaurusBaseEffectsStub';

    constructor(actions$: Actions, componentService: ComponentService) {
        super(actions$, componentService, TaurusBaseEffectsStub.CLASS_NAME);
    }

    protected registerEffectsErrorCodes(): void {
        // No-op.
    }
}

@Directive()
class TaurusBaseEffectsStubV1 extends TaurusBaseEffects {
    constructor(actions$: Actions, componentService: ComponentService, className: string) {
        super(actions$, componentService, className);
    }

    protected registerEffectsErrorCodes(): void {
        // No-op.
    }
}

describe('TaurusBaseEffects', () => {
    let componentServiceStub: jasmine.SpyObj<ComponentService>;

    let effectService: TaurusBaseEffects;

    beforeEach(() => {
        componentServiceStub = jasmine.createSpyObj<ComponentService>('componentServiceStub', ['load']);

        TestBed.configureTestingModule({
            providers: [
                TaurusBaseEffectsStub,
                { provide: ComponentService, useValue: componentServiceStub },
                provideMockActions(() => new Subject())
            ]
        });

        effectService = TestBed.inject(TaurusBaseEffectsStub);
    });

    it('should verify effect class is created', () => {
        // When
        // @ts-ignore
        const effectService1 = new TaurusBaseEffectsStubV1(null, null, null);

        // Then
        expect(effectService).toBeDefined();
        expect(effectService).toBeInstanceOf(TaurusBaseEffectsStub);
        expect(effectService).toBeInstanceOf(TaurusBaseEffects);
        expect(effectService).toBeInstanceOf(TaurusObject);

        expect(effectService1).toBeDefined();
        expect(effectService1).toBeInstanceOf(TaurusBaseEffectsStubV1);
        expect(effectService1).toBeInstanceOf(TaurusBaseEffects);
        expect(effectService1).toBeInstanceOf(TaurusObject);
    });

    describe('Statics::', () => {
        describe('|CLASS_NAME|', () => {
            it('should verify value', () => {
                // Then
                expect(TaurusBaseEffects.CLASS_NAME).toEqual('TaurusBaseEffects');
            });
        });

        describe('|PUBLIC_NAME|', () => {
            it('should verify value', () => {
                // Then
                expect(TaurusBaseEffects.PUBLIC_NAME).toEqual('Taurus-Base-Effects');
            });
        });
    });
});
