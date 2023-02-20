

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { fakeAsync, tick } from '@angular/core/testing';

import { SE_NAVIGATE } from '../event';

import { SystemEventHandlerRegistry } from './registry';
import { SystemEventDispatcher } from './event.dispatcher';
import { SystemEventHandlerRef } from './models';

describe('SystemEventDispatcher', () => {
    describe('Statics::', () => {
        describe('Methods::()', () => {
            describe('|post|', () => {
                it('should verify will post NON-BLOCKING System Event to 2 Handlers', fakeAsync(() => {
                    // Given
                    const spyHandler1: jasmine.SpyObj<{ evaluate: SystemEventHandlerRef }> = jasmine.createSpyObj('handler1', ['evaluate']);
                    const spyHandler2: jasmine.SpyObj<{ evaluate: SystemEventHandlerRef }> = jasmine.createSpyObj('handler2', ['evaluate']);
                    const spyRegistryPrepared = spyOn(SystemEventHandlerRegistry, 'getPreparedArrayOfHandlers').and.returnValue([
                        { handlerRef: spyHandler1.evaluate, handlerClassInstance: spyHandler1 },
                        { handlerRef: spyHandler2.evaluate, handlerClassInstance: spyHandler2 }
                    ]);
                    const spyRegistryFind = spyOn(SystemEventHandlerRegistry, 'findHandlerByReference').and.returnValue({
                        handlerRef: () => Promise.resolve(true),
                        handlerRecord: {
                            handlerRef: () => Promise.resolve(true),
                            handlerClassInstance: null,
                            handlerFilterExpression: null
                        },
                        active: true
                    });
                    const payload = {};

                    // When
                    SystemEventDispatcher.post(SE_NAVIGATE, payload);

                    // Then
                    tick(100);
                    expect(spyRegistryPrepared).toHaveBeenCalled();
                    expect(spyHandler1.evaluate).toHaveBeenCalledWith(payload, SE_NAVIGATE);
                    expect(spyHandler2.evaluate).toHaveBeenCalledWith(payload, SE_NAVIGATE);
                    expect(spyRegistryFind).toHaveBeenCalledTimes(2);
                }));

                it('should verify will post NON-BLOCKING System Event to 1 Handler and will skip the second one', fakeAsync(() => {
                    // Given
                    const spyHandler1: jasmine.SpyObj<{ evaluate: SystemEventHandlerRef }> = jasmine.createSpyObj('handler1', ['evaluate']);
                    const spyHandler2: jasmine.SpyObj<{ evaluate: SystemEventHandlerRef }> = jasmine.createSpyObj('handler2', ['evaluate']);
                    const spyRegistryPrepared = spyOn(SystemEventHandlerRegistry, 'getPreparedArrayOfHandlers').and.returnValue([
                        { handlerRef: spyHandler1.evaluate, handlerClassInstance: spyHandler1 },
                        { handlerRef: spyHandler2.evaluate, handlerClassInstance: spyHandler2 }
                    ]);
                    const spyRegistryFind = spyOn(SystemEventHandlerRegistry, 'findHandlerByReference').and.returnValue({
                        handlerRef: () => Promise.resolve(true),
                        handlerRecord: {
                            handlerRef: () => Promise.resolve(true),
                            handlerClassInstance: null,
                            handlerFilterExpression: null
                        },
                        active: true
                    });
                    const payload = {};

                    // When
                    SystemEventDispatcher.post(SE_NAVIGATE, payload, 1);

                    // Then
                    tick(100);
                    expect(spyRegistryPrepared).toHaveBeenCalled();
                    expect(spyHandler1.evaluate).toHaveBeenCalledWith(payload, SE_NAVIGATE);
                    expect(spyHandler2.evaluate).not.toHaveBeenCalled();
                    expect(spyRegistryFind).toHaveBeenCalledTimes(1);
                }));
            });

            describe('|send|', () => {
                it('should verify will send BLOCKING System Event to 2 Handlers', fakeAsync(() => {
                    // Given
                    const spyHandler1: jasmine.SpyObj<{ evaluate: SystemEventHandlerRef }> = jasmine.createSpyObj('handler1', ['evaluate']);
                    const spyHandler2: jasmine.SpyObj<{ evaluate: SystemEventHandlerRef }> = jasmine.createSpyObj('handler2', ['evaluate']);
                    spyHandler1.evaluate.and.returnValue(Promise.resolve(true));
                    spyHandler2.evaluate.and.returnValue(Promise.resolve(true));

                    const spyRegistryPrepared = spyOn(SystemEventHandlerRegistry, 'getPreparedArrayOfHandlers').and.returnValue([
                        { handlerRef: spyHandler1.evaluate, handlerClassInstance: spyHandler1 },
                        { handlerRef: spyHandler2.evaluate, handlerClassInstance: spyHandler2 }
                    ]);
                    const payload = {};

                    // When
                    SystemEventDispatcher
                        .send(SE_NAVIGATE, payload)
                        .then(() => {
                            // No-op.
                        });

                    tick(100);

                    // Then
                    expect(spyRegistryPrepared).toHaveBeenCalled();
                    expect(spyHandler1.evaluate).toHaveBeenCalledWith(payload, SE_NAVIGATE);
                    expect(spyHandler2.evaluate).toHaveBeenCalledWith(payload, SE_NAVIGATE);
                }));

                it('should verify will send BLOCKING System Event to 1 Handler and will skip the second one', fakeAsync(() => {
                    // Given
                    const spyHandler1: jasmine.SpyObj<{ evaluate: SystemEventHandlerRef }> = jasmine.createSpyObj('handler1', ['evaluate']);
                    const spyHandler2: jasmine.SpyObj<{ evaluate: SystemEventHandlerRef }> = jasmine.createSpyObj('handler2', ['evaluate']);
                    spyHandler1.evaluate.and.returnValue(Promise.resolve(true));
                    spyHandler2.evaluate.and.returnValue(Promise.resolve(true));

                    const spyRegistryPrepared = spyOn(SystemEventHandlerRegistry, 'getPreparedArrayOfHandlers').and.returnValue([
                        { handlerRef: spyHandler1.evaluate, handlerClassInstance: spyHandler1 },
                        { handlerRef: spyHandler2.evaluate, handlerClassInstance: spyHandler2 }
                    ]);
                    const payload = {};

                    // When
                    SystemEventDispatcher
                        .send(SE_NAVIGATE, payload, 1)
                        .then(() => {
                            // No-op.
                        });

                    tick(100);

                    // Then
                    expect(spyRegistryPrepared).toHaveBeenCalled();
                    expect(spyHandler1.evaluate).not.toHaveBeenCalled();
                    expect(spyHandler2.evaluate).toHaveBeenCalledWith(payload, SE_NAVIGATE);
                }));
            });
        });
    });
});
