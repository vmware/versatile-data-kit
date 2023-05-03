/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/dot-notation */

import { ChangeDetectorRef, Component, ComponentRef, Input, ViewContainerRef, ViewRef } from '@angular/core';
import { fakeAsync, TestBed, tick } from '@angular/core/testing';

import { CollectionsUtil } from '../../../utils';

import { TaurusObject } from '../../../common';

import { CallFake } from '../../../unit-testing';

import { DynamicComponentsService } from '../../dynamic-components';

import {
    ConfirmationInputModel,
    ConfirmationModelImpl,
    ERROR_CODE_CONFIRMATION_FORCEFULLY_DESTROYED_COMPONENT
} from '../model/confirmation.model';

import { ConfirmationComponent, ConfirmationContainerComponent } from '../components';

import { ConfirmationService } from './confirmation.service';

describe('ConfirmationService', () => {
    let dynamicComponentsServiceStub: jasmine.SpyObj<DynamicComponentsService>;

    let acquiredDynamicViewComponentRef: jasmine.SpyObj<ViewContainerRef>;
    let acquiredDynamicHostViewStub: jasmine.SpyObj<ViewRef>;

    let containerChangeDetectorRefStub: jasmine.SpyObj<ChangeDetectorRef>;
    let containerViewContainerRefStub: jasmine.SpyObj<ViewContainerRef>;
    let containerComponentRefStub: jasmine.SpyObj<ComponentRef<ConfirmationContainerComponent>>;

    let confirmationChangeDetectorRefStub: jasmine.SpyObj<ChangeDetectorRef>;
    let confirmationComponentRefStub: jasmine.SpyObj<ComponentRef<ConfirmationComponent>>;
    let confirmationComponentHostViewStub: jasmine.SpyObj<ViewRef>;
    let confirmationComponentViewContainerRefStub: jasmine.SpyObj<ViewContainerRef>;
    let confirmationMessageComponentRefStub: jasmine.SpyObj<ComponentRef<DummyMessageComponent>>;

    let consoleErrorSpy: jasmine.Spy;

    let service: ConfirmationService;

    beforeEach(() => {
        dynamicComponentsServiceStub = jasmine.createSpyObj<DynamicComponentsService>('dynamicComponentsServiceStub', [
            'getUniqueViewContainerRef',
            'destroyUniqueViewContainerRef'
        ]);

        acquiredDynamicViewComponentRef = jasmine.createSpyObj<ViewContainerRef>('acquiredDynamicViewComponentRef', [
            'createComponent',
            'clear'
        ]);
        acquiredDynamicHostViewStub = jasmine.createSpyObj<ViewRef>('acquiredDynamicHostViewStub', ['destroy'], {
            destroyed: false
        });

        containerChangeDetectorRefStub = jasmine.createSpyObj<ChangeDetectorRef>('confirmationContainerChangeDetectorRefStub', [
            'detectChanges'
        ]);
        containerViewContainerRefStub = jasmine.createSpyObj<ViewContainerRef>(
            'confirmationContainerViewContainerRefStub',
            ['createComponent', 'clear', 'indexOf', 'remove'],
            {
                length: 0
            }
        );
        containerComponentRefStub = jasmine.createSpyObj<ComponentRef<ConfirmationContainerComponent>>(
            'confirmationContainerComponentRefStub',
            ['destroy'],
            {
                changeDetectorRef: containerChangeDetectorRefStub,
                instance: {
                    viewContainerRef: containerViewContainerRefStub,
                    open: false
                },
                hostView: {
                    destroyed: false
                } as ViewRef
            }
        );

        confirmationChangeDetectorRefStub = jasmine.createSpyObj<ChangeDetectorRef>('confirmationComponentChangeDetectorRefStub', [
            'detectChanges'
        ]);
        confirmationComponentHostViewStub = jasmine.createSpyObj<ViewRef>('confirmationComponentHostViewStub', ['destroy'], {
            destroyed: false
        });
        confirmationComponentViewContainerRefStub = jasmine.createSpyObj<ViewContainerRef>('confirmationComponentViewContainerRefStub', [
            'createComponent'
        ]);
        confirmationComponentRefStub = jasmine.createSpyObj<ComponentRef<ConfirmationComponent>>(
            'confirmationComponentRefStub',
            ['destroy'],
            {
                changeDetectorRef: confirmationChangeDetectorRefStub,
                instance: {
                    model: null,
                    doNotShowFutureConfirmation: false,
                    viewContainerRef: confirmationComponentViewContainerRefStub as ViewContainerRef
                } as ConfirmationComponent,
                hostView: confirmationComponentHostViewStub
            }
        );
        confirmationMessageComponentRefStub = jasmine.createSpyObj<ComponentRef<DummyMessageComponent>>(
            'confirmationMessageComponentRefStub',
            ['destroy'],
            {
                instance: {
                    messageCode: undefined
                } as DummyMessageComponent
            }
        );

        consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);

        TestBed.configureTestingModule({
            declarations: [DummyMessageComponent],
            providers: [{ provide: DynamicComponentsService, useValue: dynamicComponentsServiceStub }, ConfirmationService]
        });

        service = TestBed.inject(ConfirmationService);
    });

    it('should verify instance is created', () => {
        // Then
        expect(service).toBeDefined();
        expect(service).toBeInstanceOf(ConfirmationService);
        expect(service).toBeInstanceOf(TaurusObject);
    });

    describe('Statics::', () => {
        describe('Properties::', () => {
            describe('|CLASS_NAME|', () => {
                it('should verify the value', () => {
                    // Then
                    expect(ConfirmationService.CLASS_NAME).toEqual('ConfirmationService');
                });
            });
        });
    });

    describe('Properties::', () => {
        describe('|objectUUID|', () => {
            it('should verify value is ConfirmationService', () => {
                // Then
                expect(/^ConfirmationService/.test(service.objectUUID)).toBeTrue();
            });
        });
    });

    describe('Methods::', () => {
        const setupTestPrerequisites = () => {
            const inputModel: ConfirmationInputModel = { title: 'Confirm title', message: 'Confirm message' };
            dynamicComponentsServiceStub.getUniqueViewContainerRef.and.returnValue({
                uuid: CollectionsUtil.generateUUID(),
                viewContainerRef: acquiredDynamicViewComponentRef,
                hostView: acquiredDynamicHostViewStub
            });
            acquiredDynamicViewComponentRef.createComponent.and.returnValue(containerComponentRefStub);
            containerViewContainerRefStub.createComponent.and.returnValue(confirmationComponentRefStub);
            containerViewContainerRefStub.indexOf.and.returnValue(0);

            return inputModel;
        };

        describe('|initialize|', () => {
            it(`should verify invoking won't throw error`, () => {
                // When/Then
                expect(() => service.initialize()).not.toThrowError();
                expect(consoleErrorSpy).not.toHaveBeenCalled();
            });
        });

        describe('|confirm|', () => {
            const verifyExpectationsInsidePromise = () => {
                expect(containerViewContainerRefStub.indexOf).toHaveBeenCalledWith(confirmationComponentHostViewStub);
                expect(containerViewContainerRefStub.remove).toHaveBeenCalledWith(0);

                expect(containerChangeDetectorRefStub.detectChanges).toHaveBeenCalledTimes(3);

                expect(confirmationComponentRefStub.destroy).toHaveBeenCalledTimes(1);

                expect(containerComponentRefStub.instance.open).toBeFalse();
            };
            const verifyExpectationsOutsidePromise = (inputModel: ConfirmationInputModel, verifyCreationOnly = false) => {
                expect(dynamicComponentsServiceStub.getUniqueViewContainerRef).toHaveBeenCalledTimes(1);

                expect(acquiredDynamicViewComponentRef.createComponent).toHaveBeenCalledTimes(1);
                // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
                expect(acquiredDynamicViewComponentRef.createComponent).toHaveBeenCalledWith(ConfirmationContainerComponent as any);

                expect(containerViewContainerRefStub.createComponent).toHaveBeenCalledTimes(1);
                // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
                expect(containerViewContainerRefStub.createComponent).toHaveBeenCalledWith(ConfirmationComponent as any);

                if (verifyCreationOnly) {
                    return;
                }

                expect(containerChangeDetectorRefStub.detectChanges).toHaveBeenCalledTimes(2);
                expect(confirmationChangeDetectorRefStub.detectChanges).toHaveBeenCalledTimes(1);

                expect(containerComponentRefStub.instance.open).toBeTrue();
                expect(confirmationComponentRefStub.instance.model).toBeInstanceOf(ConfirmationModelImpl);
                expect(confirmationComponentRefStub.instance.model.title).toEqual(inputModel.title);
                expect(confirmationComponentRefStub.instance.model.message).toEqual(inputModel.message);
                expect(confirmationComponentRefStub.instance.model.messageComponent).toBeUndefined();
                expect(confirmationComponentRefStub.instance.model.messageCode).toBeUndefined();
                expect(confirmationComponentRefStub.instance.model.handler).toEqual({
                    confirm: jasmine.any(Function),
                    dismiss: jasmine.any(Function)
                });
            };

            it('should verify will reject when cannot acquired ViewContainerRef from DynamicComponentsService', (done) => {
                // Given
                const assertionError = `${ConfirmationService.CLASS_NAME}: Potential bug found, cannot acquire unique ViewContainerRef where to insert confirmation Views`;
                dynamicComponentsServiceStub.getUniqueViewContainerRef.and.returnValue(null);

                // When/Then
                service
                    .confirm({
                        title: 'Confirm title',
                        message: 'Confirm message'
                    })
                    .catch((reason) => {
                        expect(dynamicComponentsServiceStub.getUniqueViewContainerRef).toHaveBeenCalledTimes(1);
                        expect(reason).toEqual(new Error(assertionError));
                        expect(consoleErrorSpy).toHaveBeenCalledWith(assertionError);
                        done();
                    });
            });

            it('should verify will reject when thrown error when creating ConfirmationContainerComponent', (done) => {
                // Given
                const assertionError = `${ConfirmationService.CLASS_NAME}: Potential bug found, Failed to create instance of ConfirmationContainerComponent`;
                dynamicComponentsServiceStub.getUniqueViewContainerRef.and.returnValue({
                    uuid: CollectionsUtil.generateUUID(),
                    viewContainerRef: acquiredDynamicViewComponentRef,
                    hostView: acquiredDynamicHostViewStub
                });
                acquiredDynamicViewComponentRef.createComponent.and.throwError(new Error('Error'));

                // When/Then
                service
                    .confirm({
                        title: 'Confirm title',
                        message: 'Confirm message'
                    })
                    .catch((reason) => {
                        expect(dynamicComponentsServiceStub.getUniqueViewContainerRef).toHaveBeenCalledTimes(1);
                        expect(acquiredDynamicViewComponentRef.createComponent).toHaveBeenCalledTimes(1);
                        expect(containerChangeDetectorRefStub.detectChanges).not.toHaveBeenCalled();
                        expect(reason).toEqual(new Error(assertionError));
                        expect(consoleErrorSpy).toHaveBeenCalledWith(assertionError);
                        done();
                    });
            });

            it('should verify will reject when thrown error when creating ConfirmationComponent', (done) => {
                // Given
                const assertionError = `${ConfirmationService.CLASS_NAME}: Potential bug found, Failed to create instance of ConfirmationComponent`;
                dynamicComponentsServiceStub.getUniqueViewContainerRef.and.returnValue({
                    uuid: CollectionsUtil.generateUUID(),
                    viewContainerRef: acquiredDynamicViewComponentRef,
                    hostView: acquiredDynamicHostViewStub
                });
                acquiredDynamicViewComponentRef.createComponent.and.returnValue(containerComponentRefStub);
                containerViewContainerRefStub.createComponent.and.throwError(new Error('Error'));

                // When/Then
                service
                    .confirm({
                        title: 'Confirm title',
                        message: 'Confirm message'
                    })
                    .catch((reason) => {
                        expect(dynamicComponentsServiceStub.getUniqueViewContainerRef).toHaveBeenCalledTimes(1);
                        expect(acquiredDynamicViewComponentRef.createComponent).toHaveBeenCalledTimes(1);
                        expect(containerViewContainerRefStub.createComponent).toHaveBeenCalledTimes(1);
                        expect(containerChangeDetectorRefStub.detectChanges).toHaveBeenCalledTimes(1);
                        expect(confirmationChangeDetectorRefStub.detectChanges).not.toHaveBeenCalled();
                        expect(reason).toEqual(new Error(assertionError));
                        expect(consoleErrorSpy).toHaveBeenCalledWith(assertionError);
                        done();
                    });
            });

            it('should verify will reject when thrown error when creating component for message inside ConfirmationComponent', (done) => {
                // Given
                const assertionError = `${ConfirmationService.CLASS_NAME}: Potential bug found, Failed to create Component instance for Confirmation Message`;
                dynamicComponentsServiceStub.getUniqueViewContainerRef.and.returnValue({
                    uuid: CollectionsUtil.generateUUID(),
                    viewContainerRef: acquiredDynamicViewComponentRef,
                    hostView: acquiredDynamicHostViewStub
                });
                acquiredDynamicViewComponentRef.createComponent.and.returnValue(containerComponentRefStub);
                containerViewContainerRefStub.createComponent.and.returnValue(confirmationComponentRefStub);
                containerViewContainerRefStub.indexOf.and.returnValue(0);
                confirmationComponentViewContainerRefStub.createComponent.and.throwError(new Error('Error'));

                // When/Then
                service
                    .confirm({
                        title: 'Confirm title',
                        messageComponent: DummyMessageComponent
                    })
                    .catch((reason) => {
                        expect(dynamicComponentsServiceStub.getUniqueViewContainerRef).toHaveBeenCalledTimes(1);
                        expect(acquiredDynamicViewComponentRef.createComponent).toHaveBeenCalledTimes(1);
                        expect(containerViewContainerRefStub.createComponent).toHaveBeenCalledTimes(1);
                        expect(containerChangeDetectorRefStub.detectChanges).toHaveBeenCalledTimes(1);
                        expect(confirmationComponentViewContainerRefStub.createComponent).toHaveBeenCalledTimes(1);
                        expect(confirmationChangeDetectorRefStub.detectChanges).not.toHaveBeenCalled();
                        expect(reason).toEqual(new Error(assertionError));
                        expect(consoleErrorSpy).toHaveBeenCalledWith(assertionError);
                        done();
                    });
            });

            it('should verify will render message Component and resolve when handler is resolved', (done) => {
                // Given
                dynamicComponentsServiceStub.getUniqueViewContainerRef.and.returnValue({
                    uuid: CollectionsUtil.generateUUID(),
                    viewContainerRef: acquiredDynamicViewComponentRef,
                    hostView: acquiredDynamicHostViewStub
                });
                acquiredDynamicViewComponentRef.createComponent.and.returnValue(containerComponentRefStub);
                containerViewContainerRefStub.createComponent.and.returnValue(confirmationComponentRefStub);
                containerViewContainerRefStub.indexOf.and.returnValue(0);
                confirmationComponentViewContainerRefStub.createComponent.and.returnValue(confirmationMessageComponentRefStub);

                // When/Then
                service
                    .confirm({
                        title: 'some title',
                        messageComponent: DummyMessageComponent,
                        messageCode: 'msg_code_100'
                    })
                    .then((data) => {
                        verifyExpectationsInsidePromise();

                        expect(data).toEqual({ doNotShowFutureConfirmation: true });

                        expect(consoleErrorSpy).not.toHaveBeenCalled();

                        done();
                    });

                // Then 1
                verifyExpectationsOutsidePromise(null, true);

                expect(confirmationComponentViewContainerRefStub.createComponent).toHaveBeenCalledTimes(1);
                // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
                expect(confirmationComponentViewContainerRefStub.createComponent).toHaveBeenCalledWith(DummyMessageComponent as any);
                expect(containerChangeDetectorRefStub.detectChanges).toHaveBeenCalledTimes(2);
                expect(confirmationChangeDetectorRefStub.detectChanges).toHaveBeenCalledTimes(1);

                expect(containerComponentRefStub.instance.open).toBeTrue();
                expect(confirmationComponentRefStub.instance.model).toBeInstanceOf(ConfirmationModelImpl);
                expect(confirmationComponentRefStub.instance.model.title).toEqual('some title');
                expect(confirmationComponentRefStub.instance.model.message).toBeUndefined();
                expect(confirmationComponentRefStub.instance.model.messageComponent).toBeUndefined();
                expect(confirmationComponentRefStub.instance.model.messageCode).toBeUndefined();
                expect(confirmationComponentRefStub.instance.model.handler).toEqual({
                    confirm: jasmine.any(Function),
                    dismiss: jasmine.any(Function)
                });

                expect(confirmationMessageComponentRefStub.instance.messageCode).toEqual('msg_code_100');

                confirmationComponentRefStub.instance.model.handler.confirm({ doNotShowFutureConfirmation: true });
            });

            it('should verify will resolve when handler is resolved and will clean resources after resolving', (done) => {
                // Given
                const inputModel: ConfirmationInputModel = setupTestPrerequisites();

                // When/Then
                service.confirm(inputModel).then((data) => {
                    verifyExpectationsInsidePromise();

                    expect(data).toEqual({ doNotShowFutureConfirmation: true });

                    expect(consoleErrorSpy).not.toHaveBeenCalled();
                    done();
                });

                // Then 1
                verifyExpectationsOutsidePromise(inputModel);

                confirmationComponentRefStub.instance.model.handler.confirm({ doNotShowFutureConfirmation: true });
            });

            it('should verify will resolve when handler is resolved and will fail to clean resources after resolving', (done) => {
                // Given
                const inputModel: ConfirmationInputModel = setupTestPrerequisites();
                containerViewContainerRefStub.remove.and.throwError(new Error('Error'));

                // When/Then
                service.confirm(inputModel).then((data) => {
                    expect(containerViewContainerRefStub.indexOf).toHaveBeenCalledWith(confirmationComponentHostViewStub);
                    expect(containerViewContainerRefStub.remove).toHaveBeenCalledWith(0);

                    expect(containerChangeDetectorRefStub.detectChanges).toHaveBeenCalledTimes(3);

                    expect(confirmationComponentRefStub.destroy).not.toHaveBeenCalled();

                    expect(containerComponentRefStub.instance.open).toBeFalse();

                    expect(data).toEqual({ doNotShowFutureConfirmation: false });

                    expect(consoleErrorSpy).toHaveBeenCalledWith(
                        `${ConfirmationService.CLASS_NAME}: Potential bug found, failed to cleanup confirmation views after User action`
                    );
                    done();
                });

                // Then 1
                verifyExpectationsOutsidePromise(inputModel);

                confirmationComponentRefStub.instance.model.handler.confirm({ doNotShowFutureConfirmation: false });
            });

            it('should verify will resolve when handler is resolved and will fail to clean resources with total damage for UX', (done) => {
                // Given
                const inputModel: ConfirmationInputModel = setupTestPrerequisites();
                let counter = 0;
                containerChangeDetectorRefStub.detectChanges.and.callFake(() => {
                    if (++counter >= 3) {
                        throw new Error('Error');
                    }
                });

                // When/Then
                service.confirm(inputModel).then((data) => {
                    expect(containerViewContainerRefStub.indexOf).toHaveBeenCalledWith(confirmationComponentHostViewStub);
                    expect(containerViewContainerRefStub.remove).toHaveBeenCalledWith(0);

                    expect(containerChangeDetectorRefStub.detectChanges).toHaveBeenCalledTimes(4);

                    expect(confirmationComponentRefStub.destroy).toHaveBeenCalled();

                    expect(containerComponentRefStub.instance.open).toBeFalse();

                    expect(data).toEqual({ doNotShowFutureConfirmation: false });

                    expect(consoleErrorSpy.calls.argsFor(0)).toEqual([
                        `${ConfirmationService.CLASS_NAME}: Potential bug found, failed to cleanup confirmation views after User action`
                    ]);
                    expect(consoleErrorSpy.calls.argsFor(1)).toEqual([
                        `${ConfirmationService.CLASS_NAME}: Potential bug found, failed to force container to hide`
                    ]);
                    done();
                });

                // Then 1
                verifyExpectationsOutsidePromise(inputModel);

                confirmationComponentRefStub.instance.model.handler.confirm({ doNotShowFutureConfirmation: false });
            });

            it('should verify will resolve when handler is resolved and on second invoke will acquire and create new reference because of unhealthy state', fakeAsync(() => {
                // Given
                const uuid = CollectionsUtil.generateUUID();
                const inputModel: ConfirmationInputModel = { title: 'Confirm title 50', message: 'Confirm message 50' };
                dynamicComponentsServiceStub.getUniqueViewContainerRef.and.returnValue({
                    uuid,
                    viewContainerRef: acquiredDynamicViewComponentRef,
                    hostView: jasmine.createSpyObj<ViewRef>('acquiredDynamicHostViewStub', ['destroy'], {
                        destroyed: true
                    })
                });
                acquiredDynamicViewComponentRef.createComponent.and.returnValue(containerComponentRefStub);
                containerViewContainerRefStub.createComponent.and.returnValue(confirmationComponentRefStub);
                containerViewContainerRefStub.indexOf.and.returnValue(0);

                // When/Then 1
                service.confirm(inputModel).then((data) => {
                    expect(containerViewContainerRefStub.indexOf).toHaveBeenCalledWith(confirmationComponentHostViewStub);
                    expect(containerViewContainerRefStub.remove).toHaveBeenCalledWith(0);

                    expect(containerChangeDetectorRefStub.detectChanges).toHaveBeenCalledTimes(3);

                    expect(confirmationComponentRefStub.destroy).toHaveBeenCalled();

                    expect(containerComponentRefStub.instance.open).toBeFalse();

                    expect(data).toEqual({ doNotShowFutureConfirmation: false });
                });

                // Then 1
                verifyExpectationsOutsidePromise(inputModel);

                confirmationComponentRefStub.instance.model.handler.confirm({ doNotShowFutureConfirmation: false });

                tick(1000);

                // When/Then 2
                service.confirm(inputModel).then((data) => {
                    expect(containerViewContainerRefStub.indexOf).toHaveBeenCalledWith(confirmationComponentHostViewStub);
                    expect(containerViewContainerRefStub.remove).toHaveBeenCalledWith(0);

                    expect(containerChangeDetectorRefStub.detectChanges).toHaveBeenCalledTimes(6);

                    expect(confirmationComponentRefStub.destroy).toHaveBeenCalled();

                    expect(containerComponentRefStub.instance.open).toBeFalse();

                    expect(data).toEqual({ doNotShowFutureConfirmation: true });
                });

                // Then 2
                // clean resources
                expect(confirmationComponentRefStub.destroy).toHaveBeenCalledTimes(1);
                expect(acquiredDynamicViewComponentRef.clear).toHaveBeenCalledTimes(1);
                expect(dynamicComponentsServiceStub.destroyUniqueViewContainerRef).toHaveBeenCalledTimes(1);
                expect(dynamicComponentsServiceStub.destroyUniqueViewContainerRef).toHaveBeenCalledWith(uuid);

                expect(dynamicComponentsServiceStub.getUniqueViewContainerRef).toHaveBeenCalledTimes(2);
                expect(acquiredDynamicViewComponentRef.createComponent).toHaveBeenCalledTimes(2);
                expect(containerViewContainerRefStub.createComponent).toHaveBeenCalledTimes(2);
                expect(containerChangeDetectorRefStub.detectChanges).toHaveBeenCalledTimes(5);
                expect(confirmationChangeDetectorRefStub.detectChanges).toHaveBeenCalledTimes(2);

                expect(containerComponentRefStub.instance.open).toBeTrue();
                expect(confirmationComponentRefStub.instance.model).toBeInstanceOf(ConfirmationModelImpl);

                confirmationComponentRefStub.instance.model.handler.confirm({ doNotShowFutureConfirmation: true });

                tick(1000);
            }));

            it('should verify will reject when handler is rejected and will clean resources after resolving', (done) => {
                // Given
                const inputModel: ConfirmationInputModel = setupTestPrerequisites();

                // When/Then
                service
                    .confirm(inputModel)
                    .then(() => {
                        done.fail(`Should not enter here`);
                    })
                    .catch((reason) => {
                        verifyExpectationsInsidePromise();

                        expect(reason).toEqual('Rejecting on user behalf');

                        expect(consoleErrorSpy).not.toHaveBeenCalled();
                        done();
                    });

                // Then 1
                verifyExpectationsOutsidePromise(inputModel);

                confirmationComponentRefStub.instance.model.handler.dismiss('Rejecting on user behalf');
            });

            it('should verify will reject when handler is rejected and will clean resources after resolving and log error because forcefully destroyed', (done) => {
                // Given
                const inputModel: ConfirmationInputModel = setupTestPrerequisites();

                // When/Then
                service
                    .confirm(inputModel)
                    .then(() => {
                        done.fail(`Should not enter here`);
                    })
                    .catch((reason) => {
                        verifyExpectationsInsidePromise();

                        expect(reason).toEqual(new Error(ERROR_CODE_CONFIRMATION_FORCEFULLY_DESTROYED_COMPONENT));

                        expect(consoleErrorSpy).toHaveBeenCalledWith(
                            `${ConfirmationService.CLASS_NAME}: Potential bug found, views where destroyed externally from unknown source`
                        );
                        done();
                    });

                // Then 1
                verifyExpectationsOutsidePromise(inputModel);

                confirmationComponentRefStub.instance.model.handler.dismiss(
                    new Error(ERROR_CODE_CONFIRMATION_FORCEFULLY_DESTROYED_COMPONENT)
                );
            });
        });

        describe('|ngOnDestroy|', () => {
            it('should verify will try to clean resources, there is empty state', () => {
                // When
                service.ngOnDestroy();

                // Then
                expect(consoleErrorSpy).not.toHaveBeenCalled();
                expect(confirmationComponentRefStub.destroy).not.toHaveBeenCalled();
                expect(acquiredDynamicViewComponentRef.clear).not.toHaveBeenCalled();
                expect(dynamicComponentsServiceStub.destroyUniqueViewContainerRef).not.toHaveBeenCalled();
            });

            it('should verify will clean resources, there is state', () => {
                // Given
                const inputModel: ConfirmationInputModel = setupTestPrerequisites();

                // When/Then
                service.confirm(inputModel).then(() => {
                    // No-op.
                });

                // When
                service.ngOnDestroy();

                // Then
                expect(consoleErrorSpy).not.toHaveBeenCalled();
                expect(containerComponentRefStub.destroy).toHaveBeenCalledTimes(1);
                expect(acquiredDynamicViewComponentRef.clear).toHaveBeenCalledTimes(1);
                expect(dynamicComponentsServiceStub.destroyUniqueViewContainerRef).toHaveBeenCalledTimes(1);
            });

            it('should verify will try to clean resources, but error would be thrown', () => {
                // Given
                const inputModel: ConfirmationInputModel = setupTestPrerequisites();

                containerComponentRefStub.destroy.and.throwError(new Error('Error'));
                acquiredDynamicViewComponentRef.clear.and.throwError(new Error('Error'));

                // When/Then
                service.confirm(inputModel).then(() => {
                    // No-op.
                });

                // When
                service.ngOnDestroy();

                // Then
                expect(containerComponentRefStub.destroy).toHaveBeenCalledTimes(1);
                expect(acquiredDynamicViewComponentRef.clear).toHaveBeenCalledTimes(1);
                expect(dynamicComponentsServiceStub.destroyUniqueViewContainerRef).toHaveBeenCalledTimes(1);
                expect(consoleErrorSpy.calls.argsFor(0)).toEqual([
                    `${ConfirmationService.CLASS_NAME}: Potential bug found, failed to destroy ConfirmationContainerComponent reference`
                ]);
                expect(consoleErrorSpy.calls.argsFor(1)).toEqual([
                    `${ConfirmationService.CLASS_NAME}: Potential bug found, failed to clear views in acquired ViewContainerRef`
                ]);
            });
        });
    });
});

@Component({
    selector: 'shared-dummy-message-component',
    template: `<p>some text</p>`
})
class DummyMessageComponent {
    @Input() messageCode: string;
}
