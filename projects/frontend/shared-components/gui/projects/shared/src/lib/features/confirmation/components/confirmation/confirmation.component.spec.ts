/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { DebugElement, ViewContainerRef } from '@angular/core';
import { ComponentFixture, fakeAsync, TestBed, tick } from '@angular/core/testing';
import { BrowserModule, By } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';

import { ClarityModule } from '@clr/angular';

import { CallFake } from '../../../../unit-testing';

import {
    ConfirmationHandler,
    ConfirmationInputModel,
    ConfirmationModelImpl,
    ERROR_CODE_CONFIRMATION_FORCEFULLY_DESTROYED_COMPONENT
} from '../../model/confirmation.model';

import { ConfirmationComponent } from './confirmation.component';

describe('ConfirmationComponent', () => {
    let dummyModel: ConfirmationModelImpl;

    let component: ConfirmationComponent;
    let fixture: ComponentFixture<ConfirmationComponent>;

    beforeEach(async () => {
        dummyModel = new ConfirmationModelImpl({} as ConfirmationInputModel);
        dummyModel.handler.confirm = CallFake;
        dummyModel.handler.dismiss = CallFake;

        await TestBed.configureTestingModule({
            imports: [BrowserModule, FormsModule, ClarityModule],
            declarations: [ConfirmationComponent]
        }).compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(ConfirmationComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    afterEach(() => {
        component.model = dummyModel;
    });

    it('should verify component is created', () => {
        // Then
        expect(component).toBeTruthy();
    });

    describe('Properties::', () => {
        describe('|viewContainerRef|', () => {
            it('should verify value is populate after component is created', () => {
                // Then
                expect(component.viewContainerRef).toBeInstanceOf(ViewContainerRef);
            });
        });

        describe('|model|', () => {
            it('should verify default value', () => {
                // Then
                expect(component.model).toEqual({} as ConfirmationModelImpl);
            });
        });

        describe('|doNotShowFutureConfirmation|', () => {
            it('should verify default value', () => {
                // Then
                expect(component.doNotShowFutureConfirmation).toBeFalse();
            });
        });
    });

    describe('Template::', () => {
        it('should verify will render title, message, confirm button', fakeAsync(() => {
            // Then 1
            const titleElement: HTMLHeadingElement = fixture.debugElement.query(By.css('.confirmation__header-title')).nativeElement;
            const messageDebugElement: DebugElement = fixture.debugElement.query(By.css('.confirmation__body-message'));
            const confirmationBtnElement: HTMLButtonElement = fixture.debugElement.query(
                By.css('.confirmation__footer-confirm-btn')
            ).nativeElement;
            expect(titleElement.innerHTML).toEqual('');
            expect(messageDebugElement).toBeNull();
            expect(confirmationBtnElement.innerText.trim()).toEqual('');

            // Given
            const model = new ConfirmationModelImpl({
                title: '<b>Confirmation Test</b>',
                message: `Test message, that want <b>explicit</b> confirmation!`,
                confirmBtnModel: {
                    text: 'Test Confirm Btn Text'
                }
            });
            model.handler.confirm = CallFake;
            model.handler.dismiss = CallFake;

            // When
            component.model = model;
            fixture.detectChanges();
            tick(500);

            // Then
            const messageElement: HTMLParagraphElement = fixture.debugElement.query(By.css('.confirmation__body-message')).nativeElement;
            expect(titleElement.innerHTML).toEqual('<b>Confirmation Test</b>');
            expect(messageElement.innerHTML).toEqual('Test message, that want <b>explicit</b> confirmation!');
            expect(confirmationBtnElement.innerText.trim()).toEqual('Test Confirm Btn Text');
            expect(fixture.debugElement.query(By.css('.confirmation__header-close-btn'))).toBeNull();
            expect(fixture.debugElement.query(By.css('.confirmation__body-checkbox-opt-out input'))).toBeNull();
            expect(fixture.debugElement.query(By.css('.confirmation__footer-cancel-btn'))).toBeNull();
            expect(fixture.debugElement.query(By.css('.confirmation__footer-confirm-btn-icon'))).toBeNull();
        }));

        it(`should verify won't render message if not supplied`, fakeAsync(() => {
            // Then 1
            let messageDebugElement: DebugElement = fixture.debugElement.query(By.css('.confirmation__body-message'));
            expect(messageDebugElement).toBeNull();

            // Given
            const model = new ConfirmationModelImpl({
                title: '<b>Confirmation Test</b>',
                confirmBtnModel: {
                    text: 'Test Confirm Btn Text'
                }
            });
            model.handler.confirm = CallFake;
            model.handler.dismiss = CallFake;

            // When
            component.model = model;
            fixture.detectChanges();
            tick(500);

            // Then
            messageDebugElement = fixture.debugElement.query(By.css('.confirmation__body-message'));
            expect(messageDebugElement).toBeNull();
        }));

        it('should verify will render title, close button, message, opt-out checkbox, cancel and confirm buttons with icons', fakeAsync(() => {
            // Then 1
            const titleElement: HTMLHeadingElement = fixture.debugElement.query(By.css('.confirmation__header-title')).nativeElement;
            const messageDebugElement: DebugElement = fixture.debugElement.query(By.css('.confirmation__body-message'));
            const confirmationBtnElement: HTMLButtonElement = fixture.debugElement.query(
                By.css('.confirmation__footer-confirm-btn')
            ).nativeElement;
            expect(titleElement.innerHTML).toEqual('');
            expect(messageDebugElement).toBeNull();
            expect(confirmationBtnElement.innerText.trim()).toEqual('');
            expect(fixture.debugElement.query(By.css('.confirmation__header-close-btn'))).toBeNull();
            expect(fixture.debugElement.query(By.css('.confirmation__body-checkbox-opt-out input'))).toBeNull();
            expect(fixture.debugElement.query(By.css('.confirmation__footer-cancel-btn'))).toBeNull();
            expect(fixture.debugElement.query(By.css('.confirmation__footer-confirm-btn-icon'))).toBeNull();

            // Given
            const model = new ConfirmationModelImpl({
                title: '<pre>Confirmation Test</pre>',
                message: `Test message, that want <i>explicit</i> confirmation!`,
                closable: true,
                optionDoNotShowFutureConfirmation: true,
                cancelBtnModel: {
                    text: 'Test Cancel Btn Text Case 1',
                    iconShape: 'angle',
                    iconPosition: 'right',
                    iconDirection: 'left',
                    iconBadge: 'warning',
                    iconInverse: true,
                    iconSize: 'lg',
                    iconSolid: true,
                    iconStatus: 'danger'
                },
                confirmBtnModel: {
                    text: 'Test Confirm Btn Text Case 1',
                    iconShape: 'pop-out',
                    iconPosition: 'left',
                    iconDirection: 'down',
                    iconBadge: 'info',
                    iconInverse: true,
                    iconSize: 'md',
                    iconSolid: true,
                    iconStatus: 'warning'
                }
            });
            model.handler.confirm = CallFake;
            model.handler.dismiss = CallFake;

            // When
            component.model = model;
            fixture.detectChanges();
            tick(500);

            // Then
            const messageElement: HTMLParagraphElement = fixture.debugElement.query(By.css('.confirmation__body-message')).nativeElement;
            expect(titleElement.innerHTML).toEqual('<pre>Confirmation Test</pre>');
            expect(messageElement.innerHTML).toEqual('Test message, that want <i>explicit</i> confirmation!');
            expect(confirmationBtnElement.innerText.trim()).toEqual('Test Confirm Btn Text Case 1');

            // close button
            const closeDebugElement = fixture.debugElement.query(By.css('.confirmation__header-close-btn'));
            const closeIconElement: HTMLElement = closeDebugElement.query(By.css('clr-icon')).nativeElement;
            expect(closeDebugElement.nativeElement).toBeDefined();
            expect(closeIconElement.getAttribute('shape')).toEqual('window-close');

            // confirmation
            const checkboxElement = fixture.debugElement.query(By.css('.confirmation__body-checkbox-opt-out input'));
            expect(checkboxElement.nativeElement).toBeDefined();
            const labelElement: HTMLLabelElement = fixture.debugElement.query(
                By.css('.confirmation__body-checkbox-wrapper label')
            ).nativeElement;
            expect(labelElement.innerText).toEqual('Do not show this message again.');

            // cancel button
            const cancelButtonDebugElement = fixture.debugElement.query(By.css('.confirmation__footer-cancel-btn'));
            const cancelButtonElement: HTMLButtonElement = cancelButtonDebugElement.nativeElement;
            expect(cancelButtonElement).toBeDefined();
            expect(cancelButtonElement.innerText).toEqual('Test Cancel Btn Text Case 1');
            const buttonCancelIconElement: HTMLElement = cancelButtonDebugElement.query(
                By.css('.confirmation__footer-confirm-btn-icon')
            ).nativeElement;
            expect(buttonCancelIconElement).toBeDefined();
            expect(buttonCancelIconElement.getAttribute('shape')).toEqual('angle');
            expect(buttonCancelIconElement.getAttribute('direction')).toEqual('left');
            expect(buttonCancelIconElement.getAttribute('size')).toEqual('lg');
            expect(buttonCancelIconElement.getAttribute('solid')).toEqual('true');
            expect(buttonCancelIconElement.getAttribute('inverse')).toEqual('true');
            expect(buttonCancelIconElement.getAttribute('status')).toEqual('danger');
            expect(buttonCancelIconElement.getAttribute('badge')).toEqual('warning');

            // confirm button
            const confirmButtonDebugElement = fixture.debugElement.query(By.css('.confirmation__footer-confirm-btn'));
            const confirmButtonElement: HTMLButtonElement = confirmButtonDebugElement.nativeElement;
            expect(confirmButtonElement).toBeDefined();
            expect(confirmButtonElement.innerText).toEqual('Test Confirm Btn Text Case 1');
            const buttonConfirmIconElement: HTMLElement = confirmButtonDebugElement.query(
                By.css('.confirmation__footer-confirm-btn-icon')
            ).nativeElement;
            expect(buttonConfirmIconElement).toBeDefined();
            expect(buttonConfirmIconElement.getAttribute('shape')).toEqual('pop-out');
            expect(buttonConfirmIconElement.getAttribute('direction')).toEqual('down');
            expect(buttonConfirmIconElement.getAttribute('size')).toEqual('md');
            expect(buttonConfirmIconElement.getAttribute('solid')).toEqual('true');
            expect(buttonConfirmIconElement.getAttribute('inverse')).toEqual('true');
            expect(buttonConfirmIconElement.getAttribute('status')).toEqual('warning');
            expect(buttonConfirmIconElement.getAttribute('badge')).toEqual('info');

            // footer buttons position, first cancel then confirm
            expect(cancelButtonElement.nextElementSibling.classList.contains('confirmation__footer-confirm-btn')).toBeTrue();
        }));

        const parameters: Array<[string, boolean, string, string, any]> = [
            ['close', false, '.confirmation__header-close-btn', 'dismiss', 'Confirmation canceled on User behalf'],
            ['cancel', false, '.confirmation__footer-cancel-btn', 'dismiss', 'Confirmation canceled on User behalf'],
            ['confirm', false, '.confirmation__footer-confirm-btn', 'confirm', { doNotShowFutureConfirmation: false }],
            ['close', true, '.confirmation__header-close-btn', 'dismiss', 'Confirmation canceled on User behalf'],
            ['cancel', true, '.confirmation__footer-cancel-btn', 'dismiss', 'Confirmation canceled on User behalf'],
            ['confirm', true, '.confirmation__footer-confirm-btn', 'confirm', { doNotShowFutureConfirmation: true }]
        ];
        for (const [context, isCheckedOptOut, selector, handlerMethod, assertion] of parameters) {
            it(`should verify ${context} view will invoke ${handlerMethod} handler method and opt-out is ${
                isCheckedOptOut as any as string
            }`, fakeAsync(() => {
                // Given
                const handlerStub = jasmine.createSpyObj<ConfirmationHandler>('handlerStub', ['confirm', 'dismiss']);
                const model = new ConfirmationModelImpl({
                    title: 'Confirmation title',
                    message: `Confirmation message`,
                    closable: true,
                    optionDoNotShowFutureConfirmation: true,
                    cancelBtnModel: {
                        text: 'Cancel'
                    },
                    confirmBtnModel: {
                        text: 'Confirm',
                        iconShape: 'pop-out'
                    }
                });
                // @ts-ignore
                model['handler'] = handlerStub; // eslint-disable-line @typescript-eslint/dot-notation

                // When 1
                component.model = model;
                fixture.detectChanges();
                tick(500);
                if (isCheckedOptOut) {
                    const optOutCheckbox: HTMLInputElement = fixture.debugElement.query(
                        By.css('.confirmation__body-checkbox-opt-out input')
                    ).nativeElement;
                    optOutCheckbox.click();
                    tick(500);
                }
                const actionElement: HTMLButtonElement = fixture.debugElement.query(By.css(selector)).nativeElement;
                actionElement.click();
                tick(500);

                // Then
                expect(handlerStub[handlerMethod]).toHaveBeenCalledTimes(1);
                expect(handlerStub[handlerMethod]).toHaveBeenCalledWith(assertion);
            }));
        }

        it('should verify without user interaction when component is forcefully destroyed will throw Error with code', fakeAsync(() => {
            // Given
            const handlerStub = jasmine.createSpyObj<ConfirmationHandler>('handlerStub', ['confirm', 'dismiss']);
            const model = new ConfirmationModelImpl({
                title: 'Confirmation title error thrown',
                message: `Confirmation message error thrown`,
                cancelBtnModel: {
                    text: null
                },
                confirmBtnModel: {
                    text: 'Confirm',
                    iconShape: 'pop-out'
                }
            });
            // @ts-ignore
            model['handler'] = handlerStub; // eslint-disable-line @typescript-eslint/dot-notation

            // When 1
            component.model = model;
            fixture.detectChanges();
            tick(500);
            fixture.destroy();

            // Then
            expect(handlerStub.dismiss).toHaveBeenCalledWith(new Error(ERROR_CODE_CONFIRMATION_FORCEFULLY_DESTROYED_COMPONENT));
        }));
    });
});
