/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/no-unsafe-argument,@typescript-eslint/dot-notation */

import { ChangeDetectorRef, ComponentRef, ViewContainerRef, ViewRef } from '@angular/core';
import { TestBed } from '@angular/core/testing';

import { CollectionsUtil } from '../../../utils';

import { TaurusObject } from '../../../common';

import { CallFake } from '../../../unit-testing';

import { DynamicContainerComponent, DynamicContextComponent } from '../components';

import { DynamicComponentsService } from './dynamic-components.service';

describe('DynamicComponentsService', () => {
    let appRootViewContainerRefStub: jasmine.SpyObj<ViewContainerRef>;

    let containerChangeDetectorRefStub: jasmine.SpyObj<ChangeDetectorRef>;
    let containerViewContainerRefStub: jasmine.SpyObj<ViewContainerRef>;
    let containerComponentRefStub: jasmine.SpyObj<ComponentRef<DynamicContainerComponent>>;
    let containerComponentHostViewStub: jasmine.SpyObj<ViewRef>;

    let contextChangeDetectorRefStub: jasmine.SpyObj<ChangeDetectorRef>;
    let contextViewContainerRefStub: jasmine.SpyObj<ViewContainerRef>;
    let contextComponentRefStub: jasmine.SpyObj<ComponentRef<DynamicContextComponent>>;
    let contextComponentHostViewStub: jasmine.SpyObj<ViewRef>;

    let service: DynamicComponentsService;

    beforeEach(() => {
        appRootViewContainerRefStub = jasmine.createSpyObj<ViewContainerRef>('appRootViewContainerRefStub', ['createComponent', 'clear']);

        containerChangeDetectorRefStub = jasmine.createSpyObj<ChangeDetectorRef>('dynamicContainerChangeDetectorRefStub', [
            'detectChanges'
        ]);
        containerViewContainerRefStub = jasmine.createSpyObj<ViewContainerRef>('dynamicContainerViewContainerRefStub', [
            'createComponent',
            'clear'
        ]);
        containerComponentHostViewStub = jasmine.createSpyObj<ViewRef>('containerComponentHostViewStub', ['destroy'], {
            destroyed: false
        });
        containerComponentRefStub = jasmine.createSpyObj<ComponentRef<DynamicContainerComponent>>(
            'dynamicContainerComponentRefStub',
            ['destroy'],
            {
                changeDetectorRef: containerChangeDetectorRefStub,
                instance: {
                    viewContainerRef: containerViewContainerRefStub
                },
                hostView: containerComponentHostViewStub
            }
        );

        contextChangeDetectorRefStub = jasmine.createSpyObj<ChangeDetectorRef>('dynamicContextChangeDetectorRefStub', ['detectChanges']);
        contextViewContainerRefStub = jasmine.createSpyObj<ViewContainerRef>('dynamicContextViewContainerRefStub', [
            'createComponent',
            'clear'
        ]);
        contextComponentHostViewStub = jasmine.createSpyObj<ViewRef>('contextComponentHostViewStub', ['destroy'], {
            destroyed: false
        });
        contextComponentRefStub = jasmine.createSpyObj<ComponentRef<DynamicContainerComponent>>(
            'dynamicContextComponentRefStub',
            ['destroy'],
            {
                changeDetectorRef: contextChangeDetectorRefStub,
                instance: {
                    viewContainerRef: contextViewContainerRefStub
                },
                hostView: contextComponentHostViewStub
            }
        );

        TestBed.configureTestingModule({
            providers: [DynamicComponentsService]
        });

        service = TestBed.inject(DynamicComponentsService);
    });

    it('should verify instance is created', () => {
        // Then
        expect(service).toBeDefined();
        expect(service).toBeInstanceOf(DynamicComponentsService);
        expect(service).toBeInstanceOf(TaurusObject);
    });

    describe('Statics::', () => {
        describe('Properties::', () => {
            describe('|CLASS_NAME|', () => {
                it('should verify the value', () => {
                    // Then
                    expect(DynamicComponentsService.CLASS_NAME).toEqual('DynamicComponentsService');
                });
            });
        });
    });

    describe('Properties::', () => {
        describe('|objectUUID|', () => {
            it('should verify value is DynamicComponentsService', () => {
                // Then
                expect(/^DynamicComponentsService/.test(service.objectUUID)).toBeTrue();
            });
        });
    });

    describe('Methods::', () => {
        describe('|initialize|', () => {
            const parameters: Array<[string, ViewContainerRef]> = [
                ['null', null],
                ['undefined', undefined],
                ['ViewContainerRef', jasmine.createSpyObj<ViewContainerRef>('viewContainerRefStub', ['createComponent'])]
            ];

            for (const [context, viewContainerRef] of parameters) {
                it(`should verify invoking won't throw error when providing ${context}`, () => {
                    // Given
                    const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);

                    // When/Then
                    expect(() => service.initialize(viewContainerRef)).not.toThrowError();
                    expect(consoleErrorSpy).not.toHaveBeenCalled();
                });
            }
        });

        describe('|getUniqueViewContainerRef|', () => {
            it('should verify will return null, when there is no app root ViewContainerRef', () => {
                // When
                const viewContainerRef1 = service.getUniqueViewContainerRef();
                const viewContainerRef2 = service.getUniqueViewContainerRef(CollectionsUtil.generateUUID());

                // Then
                expect(viewContainerRef1).toBeNull();
                expect(viewContainerRef2).toBeNull();
            });

            it('should verify will return null, when trying to create DynamicContainerComponent, but factory throws error', () => {
                // Given
                const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);
                appRootViewContainerRefStub.createComponent.and.throwError(new Error('error'));
                service.initialize(appRootViewContainerRefStub);

                // When
                const acquiredReference = service.getUniqueViewContainerRef();

                // Then
                expect(acquiredReference).toBeNull();
                expect(appRootViewContainerRefStub.createComponent).toHaveBeenCalledWith(DynamicContainerComponent as any);
                expect(consoleErrorSpy).toHaveBeenCalledWith(
                    `${DynamicComponentsService.CLASS_NAME}: Potential bug found, Failed to create instance of DynamicContainerComponent`
                );
            });

            it('should verify will return null, when DynamicContainerComponent is created but validation fail, ViewContainerRef is missing', () => {
                // Given
                const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);
                // clear ViewContainerRef from stub
                // @ts-ignore
                containerComponentRefStub.instance['viewContainerRef'] = null;
                appRootViewContainerRefStub.createComponent.and.returnValue(containerComponentRefStub);
                service.initialize(appRootViewContainerRefStub);

                // When
                const acquiredReference = service.getUniqueViewContainerRef();

                // Then
                expect(acquiredReference).toBeNull();
                expect(appRootViewContainerRefStub.createComponent).toHaveBeenCalledWith(DynamicContainerComponent as any);
                expect(containerChangeDetectorRefStub.detectChanges).toHaveBeenCalled();
                expect(consoleErrorSpy).toHaveBeenCalledWith(
                    `${DynamicComponentsService.CLASS_NAME}: Potential bug found, Service is not initialized correctly ` +
                        `or during initialization failed to create instance of DynamicContainerComponent`
                );
            });

            it('should verify will return null, when trying to create DynamicContextComponent, but factory throws error', () => {
                // Given
                const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);
                appRootViewContainerRefStub.createComponent.and.returnValue(containerComponentRefStub);
                containerViewContainerRefStub.createComponent.and.throwError(new Error('Error'));
                service.initialize(appRootViewContainerRefStub);

                // When
                const acquiredReference = service.getUniqueViewContainerRef();

                // Then
                expect(acquiredReference).toBeNull();
                expect(appRootViewContainerRefStub.createComponent).toHaveBeenCalledWith(DynamicContainerComponent as any);
                expect(containerViewContainerRefStub.createComponent).toHaveBeenCalledWith(DynamicContextComponent as any);
                expect(consoleErrorSpy).toHaveBeenCalledWith(
                    `${DynamicComponentsService.CLASS_NAME}: Potential bug found, Failed to create instance of DynamicContextComponent`
                );
            });

            it('should verify will return null, when DynamicContextComponent is created but validation fail, ViewContainerRef is missing', () => {
                // Given
                const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);
                // clear ViewContainerRef from stub
                // @ts-ignore
                contextComponentRefStub.instance['viewContainerRef'] = null;
                appRootViewContainerRefStub.createComponent.and.returnValue(containerComponentRefStub);
                containerViewContainerRefStub.createComponent.and.returnValue(contextComponentRefStub);
                service.initialize(appRootViewContainerRefStub);

                // When
                const acquiredReference = service.getUniqueViewContainerRef();

                // Then
                expect(acquiredReference).toBeNull();
                expect(appRootViewContainerRefStub.createComponent).toHaveBeenCalledWith(DynamicContainerComponent as any);
                expect(containerChangeDetectorRefStub.detectChanges).toHaveBeenCalled();
                expect(containerViewContainerRefStub.createComponent).toHaveBeenCalledWith(DynamicContextComponent as any);
                expect(contextChangeDetectorRefStub.detectChanges).toHaveBeenCalled();
                expect(consoleErrorSpy).toHaveBeenCalledWith(
                    `${DynamicComponentsService.CLASS_NAME}: Potential bug found, Failed to retrieve context instance of DynamicContextComponent`
                );
            });

            it('should verify will return expected value uuid, ViewContainerRef and ViewRef', () => {
                // Given
                const uuid = CollectionsUtil.generateUUID();
                spyOn(CollectionsUtil, 'generateUUID').and.returnValue(uuid);
                appRootViewContainerRefStub.createComponent.and.returnValue(containerComponentRefStub);
                containerViewContainerRefStub.createComponent.and.returnValue(contextComponentRefStub);
                service.initialize(appRootViewContainerRefStub);

                // When
                const acquiredReference = service.getUniqueViewContainerRef();

                // Then
                expect(acquiredReference).toEqual({
                    uuid,
                    viewContainerRef: contextViewContainerRefStub,
                    hostView: contextComponentHostViewStub
                });
                expect(appRootViewContainerRefStub.createComponent).toHaveBeenCalledWith(DynamicContainerComponent as any);
                expect(containerChangeDetectorRefStub.detectChanges).toHaveBeenCalled();
                expect(containerViewContainerRefStub.createComponent).toHaveBeenCalledWith(DynamicContextComponent as any);
                expect(contextChangeDetectorRefStub.detectChanges).toHaveBeenCalled();
            });

            it('should verify will retrieve existing uuid, ViewContainerRef and ViewRef', () => {
                // Given
                const uuid1 = CollectionsUtil.generateUUID();
                const uuid2 = CollectionsUtil.generateUUID();
                spyOn(CollectionsUtil, 'generateUUID').and.returnValues(uuid1, uuid2);
                appRootViewContainerRefStub.createComponent.and.returnValue(containerComponentRefStub);
                containerViewContainerRefStub.createComponent.and.returnValue(contextComponentRefStub);
                service.initialize(appRootViewContainerRefStub);

                // When
                const acquiredReference1 = service.getUniqueViewContainerRef();
                const acquiredReference2 = service.getUniqueViewContainerRef(uuid1);
                const acquiredReference3 = service.getUniqueViewContainerRef();
                const acquiredReference4 = service.getUniqueViewContainerRef(uuid2);

                // Then
                expect(acquiredReference1).toEqual({
                    uuid: uuid1,
                    viewContainerRef: contextViewContainerRefStub,
                    hostView: contextComponentHostViewStub
                });
                expect(acquiredReference2).toEqual({
                    uuid: uuid1,
                    viewContainerRef: contextViewContainerRefStub,
                    hostView: contextComponentHostViewStub
                });
                expect(acquiredReference3).toEqual({
                    uuid: uuid2,
                    viewContainerRef: contextViewContainerRefStub,
                    hostView: contextComponentHostViewStub
                });
                expect(acquiredReference4).toEqual({
                    uuid: uuid2,
                    viewContainerRef: contextViewContainerRefStub,
                    hostView: contextComponentHostViewStub
                });
                expect(appRootViewContainerRefStub.createComponent).toHaveBeenCalledTimes(1);
                expect(containerChangeDetectorRefStub.detectChanges).toHaveBeenCalledTimes(1);
                expect(containerViewContainerRefStub.createComponent).toHaveBeenCalledTimes(2);
                expect(contextChangeDetectorRefStub.detectChanges).toHaveBeenCalledTimes(2);
            });
        });

        describe('|destroyUniqueViewContainerRef|', () => {
            it('should verify will return null when ViewContainerRef cannot be found for provided UUID', () => {
                // Given
                const uuid = CollectionsUtil.generateUUID();

                // When
                const isDestroyed = service.destroyUniqueViewContainerRef(uuid);

                // Then
                expect(isDestroyed).toBeNull();
            });

            it('should verify will return false if destroying ViewContainerRef throws error', () => {
                // Given
                const uuid = CollectionsUtil.generateUUID();
                spyOn(CollectionsUtil, 'generateUUID').and.returnValue(uuid);
                const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);
                contextComponentRefStub.destroy.and.throwError(new Error('Error'));
                appRootViewContainerRefStub.createComponent.and.returnValue(containerComponentRefStub);
                containerViewContainerRefStub.createComponent.and.returnValue(contextComponentRefStub);
                service.initialize(appRootViewContainerRefStub);

                // When 1
                const acquiredReference = service.getUniqueViewContainerRef();

                // Then 1
                expect(acquiredReference).toBeDefined();
                expect(service['_uniqueComponentRefsStore'].size).toEqual(1);
                expect(service['_uniqueComponentRefsStore'].get(uuid)).toEqual(contextComponentRefStub);

                // When
                const isDestroyed = service.destroyUniqueViewContainerRef(uuid);

                // Then
                expect(isDestroyed).toBeFalse();
                expect(contextComponentRefStub.destroy).toHaveBeenCalledTimes(1);
                expect(service['_uniqueComponentRefsStore'].size).toEqual(1);
                expect(service['_uniqueComponentRefsStore'].get(uuid)).toEqual(contextComponentRefStub);
                expect(consoleErrorSpy).toHaveBeenCalledWith(
                    `${DynamicComponentsService.CLASS_NAME}: Potential bug found, Failed to destroy unique ViewContainerRef instance in DynamicContextComponent`
                );
            });

            it('should verify will return true if destroying ViewContainerRef is successful', () => {
                // Given
                const uuid = CollectionsUtil.generateUUID();
                spyOn(CollectionsUtil, 'generateUUID').and.returnValue(uuid);
                appRootViewContainerRefStub.createComponent.and.returnValue(containerComponentRefStub);
                containerViewContainerRefStub.createComponent.and.returnValue(contextComponentRefStub);
                service.initialize(appRootViewContainerRefStub);

                // When 1
                const acquiredReference = service.getUniqueViewContainerRef();

                // Then 1
                expect(acquiredReference).toBeDefined();
                expect(service['_uniqueComponentRefsStore'].size).toEqual(1);
                expect(service['_uniqueComponentRefsStore'].get(uuid)).toEqual(contextComponentRefStub);

                // When
                const isDestroyed = service.destroyUniqueViewContainerRef(uuid);

                // Then
                expect(isDestroyed).toBeTrue();
                expect(contextComponentRefStub.destroy).toHaveBeenCalledTimes(1);
                expect(service['_uniqueComponentRefsStore'].size).toEqual(0);
            });
        });

        describe('|ngOnDestroy|', () => {
            it('should verify will clear all resources when invoked', () => {
                // Given
                appRootViewContainerRefStub.createComponent.and.returnValue(containerComponentRefStub);
                containerViewContainerRefStub.createComponent.and.returnValue(contextComponentRefStub);
                service.initialize(appRootViewContainerRefStub);

                // When 1
                const acquiredReference1 = service.getUniqueViewContainerRef();
                const acquiredReference2 = service.getUniqueViewContainerRef();
                const acquiredReference3 = service.getUniqueViewContainerRef();

                // Then 1
                expect(contextComponentHostViewStub.destroy).not.toHaveBeenCalled();
                expect(acquiredReference1).toBeDefined();
                expect(acquiredReference2).toBeDefined();
                expect(acquiredReference3).toBeDefined();
                expect(service['_uniqueComponentRefsStore'].size).toEqual(3);

                // When 2
                service.ngOnDestroy();

                // Then 2
                expect(service['_uniqueComponentRefsStore'].size).toEqual(0);
                expect(contextComponentRefStub.destroy).toHaveBeenCalledTimes(3);
                expect(containerComponentRefStub.destroy).toHaveBeenCalledTimes(1);
                expect(appRootViewContainerRefStub.clear).toHaveBeenCalledTimes(1);
            });

            it(`should verify won't throw error when invoked and there is error thrown inside`, () => {
                // Given
                const uuid1 = CollectionsUtil.generateUUID();
                const uuid2 = CollectionsUtil.generateUUID();
                const uuid3 = CollectionsUtil.generateUUID();
                spyOn(CollectionsUtil, 'generateUUID').and.returnValues(uuid1, uuid2, uuid3);
                const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);
                containerComponentRefStub.destroy.and.throwError(new Error('Error 1'));
                appRootViewContainerRefStub.createComponent.and.returnValue(containerComponentRefStub);
                contextComponentRefStub.destroy.and.throwError(new Error('Error 2'));
                containerViewContainerRefStub.createComponent.and.returnValue(contextComponentRefStub);
                appRootViewContainerRefStub.clear.and.throwError(new Error('Error 3'));
                service.initialize(appRootViewContainerRefStub);

                // When 1
                const acquiredReference1 = service.getUniqueViewContainerRef();
                const acquiredReference2 = service.getUniqueViewContainerRef();
                const acquiredReference3 = service.getUniqueViewContainerRef();

                // Then 1
                expect(contextComponentHostViewStub.destroy).not.toHaveBeenCalled();
                expect(acquiredReference1).toBeDefined();
                expect(acquiredReference2).toBeDefined();
                expect(acquiredReference3).toBeDefined();
                expect(service['_uniqueComponentRefsStore'].size).toEqual(3);

                // When 2
                service.ngOnDestroy();

                // Then 2
                expect(service['_uniqueComponentRefsStore'].size).toEqual(0);
                expect(contextComponentRefStub.destroy).toHaveBeenCalledTimes(3);
                expect(containerComponentRefStub.destroy).toHaveBeenCalledTimes(1);
                expect(appRootViewContainerRefStub.clear).toHaveBeenCalledTimes(1);

                expect(consoleErrorSpy).toHaveBeenCalledTimes(5);
                expect(consoleErrorSpy.calls.argsFor(0)).toEqual([
                    `${DynamicComponentsService.CLASS_NAME}: Potential bug found, failed to destroy unique component ref ${uuid1}`
                ]);
                expect(consoleErrorSpy.calls.argsFor(1)).toEqual([
                    `${DynamicComponentsService.CLASS_NAME}: Potential bug found, failed to destroy unique component ref ${uuid2}`
                ]);
                expect(consoleErrorSpy.calls.argsFor(2)).toEqual([
                    `${DynamicComponentsService.CLASS_NAME}: Potential bug found, failed to destroy unique component ref ${uuid3}`
                ]);
                expect(consoleErrorSpy.calls.argsFor(3)).toEqual([
                    `${DynamicComponentsService.CLASS_NAME}: Potential bug found, failed to destroy DynamicContextContainer ref`
                ]);
                expect(consoleErrorSpy.calls.argsFor(4)).toEqual([
                    `${DynamicComponentsService.CLASS_NAME}: Potential bug found, failed to destroy root ViewContainerRef`
                ]);
            });
        });
    });
});
