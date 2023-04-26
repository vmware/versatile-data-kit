/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/no-unsafe-argument */

import { Component, Input } from '@angular/core';
import { TestBed } from '@angular/core/testing';

import { CookieService } from 'ngx-cookie-service';

import { TaurusObject } from '../../../common';

import { NavigationService } from '../../../core';

import { CallFake } from '../../../unit-testing';

import { ConfirmationService } from '../../confirmation';

import { UrlOpenerModel } from '../model';

import { UrlOpenerService } from './url-opener.service';

describe('UrlOpenerService', () => {
    let navigationServiceStub: jasmine.SpyObj<NavigationService>;
    let confirmationServiceStub: jasmine.SpyObj<ConfirmationService>;
    let cookieServiceStub: jasmine.SpyObj<CookieService>;

    let service: UrlOpenerService;

    beforeEach(() => {
        navigationServiceStub = jasmine.createSpyObj<NavigationService>('navigationServiceStub', ['navigate']);
        confirmationServiceStub = jasmine.createSpyObj<ConfirmationService>('confirmationServiceStub', ['confirm']);
        cookieServiceStub = jasmine.createSpyObj<CookieService>('cookieServiceStub', ['get', 'set']);

        TestBed.configureTestingModule({
            declarations: [DummyMessageComponent],
            providers: [
                { provide: NavigationService, useValue: navigationServiceStub },
                { provide: ConfirmationService, useValue: confirmationServiceStub },
                { provide: CookieService, useValue: cookieServiceStub },
                UrlOpenerService
            ]
        });

        service = TestBed.inject(UrlOpenerService);
    });

    it('should verify instance is created', () => {
        // Then
        expect(service).toBeDefined();
        expect(service).toBeInstanceOf(UrlOpenerService);
        expect(service).toBeInstanceOf(TaurusObject);
    });

    describe('Statics::', () => {
        describe('Properties::', () => {
            describe('|CLASS_NAME|', () => {
                it('should verify the value', () => {
                    // Then
                    expect(UrlOpenerService.CLASS_NAME).toEqual('UrlOpenerService');
                });
            });
        });
    });

    describe('Properties::', () => {
        describe('|objectUUID|', () => {
            it('should verify value is UrlOpenerService', () => {
                // Then
                expect(/^UrlOpenerService_/.test(service.objectUUID)).toBeTrue();
            });
        });
    });

    describe('Methods::', () => {
        describe('|initialize|', () => {
            const parameters = [
                [null, null],
                [
                    'аусеров random 72636åßß∂ƒ©˚∆˙˙',
                    `${UrlOpenerService.CLASS_NAME}: Potential bug found, provided value cannot be decoded from base64`
                ],
                [btoa('{"name":"auserov'), `${UrlOpenerService.CLASS_NAME}: Potential bug found, cannot parse provided JSON`],
                [btoa('{"name":"auserov"}'), null]
            ];

            for (const [cookieValue, consoleErrorValue] of parameters) {
                it(`should verify invoking won't throw error when cookie service return -> ${cookieValue}`, () => {
                    // Given
                    const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);
                    cookieServiceStub.get.and.returnValue(cookieValue);

                    // When/Then
                    expect(() => service.initialize()).not.toThrowError();
                    if (consoleErrorValue) {
                        expect(consoleErrorSpy).toHaveBeenCalledWith(consoleErrorValue);
                    }
                });
            }
        });

        describe('|open|', () => {
            describe('Internal_Url::', () => {
                it('should verify will open only url', (done) => {
                    // Given
                    const url = 'http://localhost:9876/pathname/context/10';

                    // When
                    service.open(url).then((value) => {
                        expect(value).toBeTrue();
                        done();
                    });
                });

                it('should verify will open url and target', (done) => {
                    // Given
                    const url = 'http://localhost:9876/pathname/context/12?param1=value10&param2=value20';
                    navigationServiceStub.navigate.and.returnValue(Promise.resolve(true));

                    // When
                    service.open(url, '_self').then((value) => {
                        expect(value).toBeTrue();
                        expect(navigationServiceStub.navigate).toHaveBeenCalledWith('http://localhost:9876/pathname/context/12', {
                            queryParams: {
                                param1: 'value10',
                                param2: 'value20'
                            }
                        });
                        done();
                    });
                });

                it(`should verify will open url and target _self and won't throw error when query extraction fails`, (done) => {
                    // Given
                    const url = 'http://localhost:9876/pathname/context/14?param1=value10&param2=value20';
                    const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);
                    spyOn(URLSearchParams.prototype, 'forEach').and.throwError(new Error('error'));
                    navigationServiceStub.navigate.and.returnValue(Promise.resolve(true));

                    // When
                    service.open(url, '_self').then((value) => {
                        expect(value).toBeTrue();
                        expect(consoleErrorSpy).toHaveBeenCalledWith(
                            `${UrlOpenerService.CLASS_NAME}: Potential bug found, Exception thrown while extracting query string for internal navigation`
                        );
                        expect(navigationServiceStub.navigate).toHaveBeenCalledWith('http://localhost:9876/pathname/context/14', {
                            queryParams: {}
                        });
                        done();
                    });
                });

                it(`should verify will open url and target _blank and will leverage persisted data`, (done) => {
                    // Given
                    const url = 'http://localhost:9876/pathname/context/16';
                    cookieServiceStub.get.and.returnValue(btoa(JSON.stringify({ 'http://localhost:9876/pathname/context/16': '1' })));
                    service.initialize();

                    // When
                    service.open(url, '_blank').then((value) => {
                        expect(value).toBeTrue();
                        done();
                    });
                });

                it('should verify will open url, target _blank and confirmation model', (done) => {
                    // Given
                    const url = 'http://localhost:9876/pathname/context/18';
                    confirmationServiceStub.confirm.and.returnValue(Promise.resolve({ doNotShowFutureConfirmation: true }));

                    // When
                    service.open(url, '_blank', { explicitConfirmation: true } as UrlOpenerModel).then((value) => {
                        expect(value).toBeTrue();
                        expect(confirmationServiceStub.confirm).toHaveBeenCalledWith({
                            title: `Proceed to <code>${url}</code>`,
                            explicitConfirmation: true,
                            confirmBtnModel: {
                                text: 'Proceed'
                            }
                        } as UrlOpenerModel);
                        expect(cookieServiceStub.set).toHaveBeenCalledWith(
                            service['_cookieKey'],
                            btoa(JSON.stringify({ 'http://localhost:9876/pathname/context/18': '1' }))
                        );
                        done();
                    });
                });

                it(`should verify will open url, target _blank and confirmation model and won't persist opt-out because cannot be encoded base64`, (done) => {
                    // Given
                    const url = 'http://localhost:9876/pathname/context/20/аусеров';
                    const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);
                    confirmationServiceStub.confirm.and.returnValue(Promise.resolve({ doNotShowFutureConfirmation: true }));

                    // When
                    service.open(url, '_blank', { explicitConfirmation: true } as UrlOpenerModel).then((value) => {
                        expect(value).toBeTrue();
                        expect(consoleErrorSpy).toHaveBeenCalledWith(
                            `${UrlOpenerService.CLASS_NAME}: Potential bug found, provided value cannot be encoded to base64`
                        );
                        expect(cookieServiceStub.set).not.toHaveBeenCalled();
                        done();
                    });
                });

                it(`should verify will open url, target _blank and confirmation model and won't persist opt-out because cannot be JSON stringify`, (done) => {
                    // Given
                    const url = 'http://localhost:9876/pathname/context/22';
                    spyOn(JSON, 'stringify').and.throwError(new Error('error'));
                    const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);
                    confirmationServiceStub.confirm.and.returnValue(Promise.resolve({ doNotShowFutureConfirmation: true }));

                    // When
                    service.open(url, '_blank', { explicitConfirmation: true } as UrlOpenerModel).then((value) => {
                        expect(value).toBeTrue();
                        expect(consoleErrorSpy).toHaveBeenCalledWith(
                            `${UrlOpenerService.CLASS_NAME}: Potential bug found, cannot serialize provided object`
                        );
                        expect(cookieServiceStub.set).not.toHaveBeenCalled();
                        done();
                    });
                });

                it(`should verify will reject if cannot open external url`, (done) => {
                    // Given
                    const url = 'http://localhost:9876/pathname/context/24';
                    // @ts-ignore
                    spyOn(UrlOpenerService, '_openExternalUrl').and.returnValue(false);
                    confirmationServiceStub.confirm.and.returnValue(Promise.resolve({ doNotShowFutureConfirmation: false }));

                    // When
                    service
                        .open(url, '_blank', {
                            explicitConfirmation: true,
                            message: 'some message',
                            messageComponent: DummyMessageComponent,
                            messageCode: 'some_code_100',
                            confirmBtnModel: {
                                text: null
                            }
                        } as UrlOpenerModel)
                        .then(() => {
                            done.fail(`should not enter here`);
                        })
                        .catch((reason) => {
                            expect(confirmationServiceStub.confirm).toHaveBeenCalledWith({
                                title: `Proceed to <code>${url}</code>`,
                                message: 'some message',
                                messageComponent: DummyMessageComponent,
                                messageCode: 'some_code_100',
                                explicitConfirmation: true,
                                confirmBtnModel: {
                                    text: 'Proceed'
                                }
                            } as UrlOpenerModel);
                            expect(reason).toEqual(
                                new Error(`${UrlOpenerService.CLASS_NAME}: Exception thrown, cannot open Super Collider url in a new tab`)
                            );
                            done();
                        });
                });
            });

            describe('External_Url::', () => {
                it('should verify will open confirmation by default and after will open url', (done) => {
                    // Given
                    const url = 'http://unknown.something.auserov/pathname/context/10';
                    confirmationServiceStub.confirm.and.returnValue(Promise.resolve({ doNotShowFutureConfirmation: false }));

                    // When
                    service.open(url).then((value) => {
                        expect(value).toBeTrue();
                        expect(confirmationServiceStub.confirm).toHaveBeenCalledWith({
                            title: `Proceed to <code>${url}</code>`,
                            closable: true,
                            confirmBtnModel: {
                                text: 'Proceed'
                            }
                        } as UrlOpenerModel);
                        expect(cookieServiceStub.set).not.toHaveBeenCalled();
                        done();
                    });
                });

                it('should verify will open confirmation by default and after will open url and target', (done) => {
                    // Given
                    const url = 'http://unknown.something.auserov/pathname/context/12';
                    confirmationServiceStub.confirm.and.returnValue(Promise.resolve({ doNotShowFutureConfirmation: false }));

                    // When
                    service.open(url, '_blank').then((value) => {
                        expect(value).toBeTrue();
                        expect(confirmationServiceStub.confirm).toHaveBeenCalledWith({
                            title: `Proceed to <code>${url}</code>`,
                            closable: true,
                            confirmBtnModel: {
                                text: 'Proceed'
                            }
                        } as UrlOpenerModel);
                        expect(cookieServiceStub.set).not.toHaveBeenCalled();
                        done();
                    });
                });

                it(`should verify won't open confirmation and will open url and target, leveraging persisted data`, (done) => {
                    // Given
                    const url = 'http://unknown.something.auserov/pathname/context/14';
                    cookieServiceStub.get.and.returnValue(btoa(JSON.stringify({ 'http://unknown.something.auserov': '1' })));
                    service.initialize();

                    // When
                    service.open(url, '_blank').then((value) => {
                        expect(value).toBeTrue();
                        expect(confirmationServiceStub.confirm).not.toHaveBeenCalled();
                        expect(cookieServiceStub.set).not.toHaveBeenCalled();
                        done();
                    });
                });

                it(`should verify will open confirmation and after will open url, for malformed url and won't persist opt-out data`, (done) => {
                    // Given
                    const url = 'http::://unknown.something.auserov/pathname/context/14';
                    const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);
                    confirmationServiceStub.confirm.and.returnValue(Promise.resolve({ doNotShowFutureConfirmation: true }));

                    // When
                    service.open(url).then((value) => {
                        expect(value).toBeTrue();
                        expect(confirmationServiceStub.confirm).toHaveBeenCalledWith({
                            title: `Proceed to <code>${url}</code>`,
                            closable: true,
                            confirmBtnModel: {
                                text: 'Proceed'
                            }
                        } as UrlOpenerModel);
                        expect(consoleErrorSpy).toHaveBeenCalledWith(
                            `${UrlOpenerService.CLASS_NAME}: Potential bug found, cannot extract origin from url`
                        );
                        expect(cookieServiceStub.set).not.toHaveBeenCalled();
                        done();
                    });
                });

                it(`should verify will open confirmation and after will open url, and will persist opt-out data for non-english origin`, (done) => {
                    // Given
                    const url = 'http://unknown.something.аусеров/pathname/context/18';
                    const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);
                    confirmationServiceStub.confirm.and.returnValue(Promise.resolve({ doNotShowFutureConfirmation: true }));

                    // When
                    service.open(url).then((value) => {
                        expect(value).toBeTrue();
                        expect(confirmationServiceStub.confirm).toHaveBeenCalledWith({
                            title: `Proceed to <code>${url}</code>`,
                            closable: true,
                            confirmBtnModel: {
                                text: 'Proceed'
                            }
                        } as UrlOpenerModel);
                        expect(consoleErrorSpy).not.toHaveBeenCalled();
                        expect(cookieServiceStub.set).toHaveBeenCalledWith(
                            service['_cookieKey'],
                            btoa(JSON.stringify({ 'http://unknown.something.xn--80aei0bjen': '1' }))
                        );
                        done();
                    });
                });

                it(`should verify will open confirmation and after will open url, and will persist opt-out data for english origin`, (done) => {
                    // Given
                    const url = 'http://unknown.something.auserov/pathname/context/30';
                    confirmationServiceStub.confirm.and.returnValue(Promise.resolve({ doNotShowFutureConfirmation: true }));

                    // When
                    service.open(url).then((value) => {
                        expect(value).toBeTrue();
                        expect(confirmationServiceStub.confirm).toHaveBeenCalledWith({
                            title: `Proceed to <code>${url}</code>`,
                            closable: true,
                            confirmBtnModel: {
                                text: 'Proceed'
                            }
                        } as UrlOpenerModel);
                        expect(cookieServiceStub.set).toHaveBeenCalledWith(
                            service['_cookieKey'],
                            btoa(JSON.stringify({ 'http://unknown.something.auserov': '1' }))
                        );
                        done();
                    });
                });

                it(`should verify will open confirmation and after will open url, target and model, and won't persist opt-out data because cannot be encoded base64`, (done) => {
                    // Given
                    const url = 'http://unknown.something.аусеров/pathname/context/20';
                    const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);
                    confirmationServiceStub.confirm.and.returnValue(Promise.resolve({ doNotShowFutureConfirmation: true }));
                    spyOnProperty(URL.prototype, 'origin', 'get').and.returnValue('аусеров');

                    // When
                    service
                        .open(url, '_blank', {
                            title: `Proceed to ${url}`,
                            message: 'Random message',
                            closable: false,
                            confirmBtnModel: {
                                text: null,
                                iconShape: 'window-close',
                                iconPosition: 'right'
                            }
                        })
                        .then((value) => {
                            expect(value).toBeTrue();
                            expect(confirmationServiceStub.confirm).toHaveBeenCalledWith({
                                title: `Proceed to ${url}`,
                                message: 'Random message',
                                closable: false,
                                confirmBtnModel: {
                                    text: 'Proceed',
                                    iconShape: 'window-close',
                                    iconPosition: 'right'
                                }
                            } as UrlOpenerModel);
                            expect(consoleErrorSpy).toHaveBeenCalledWith(
                                `${UrlOpenerService.CLASS_NAME}: Potential bug found, provided value cannot be encoded to base64`
                            );
                            expect(cookieServiceStub.set).not.toHaveBeenCalled();
                            done();
                        });
                });

                it(`should verify will open confirmation and after will open url, target and model, and won't persist opt-out because cannot be JSON stringify`, (done) => {
                    // Given
                    const url = 'http://unknown.something.аусеров/pathname/context/22';
                    spyOn(JSON, 'stringify').and.throwError(new Error('error'));
                    const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);
                    confirmationServiceStub.confirm.and.returnValue(Promise.resolve({ doNotShowFutureConfirmation: true }));

                    // When
                    service
                        .open(url, '_blank', {
                            title: `Proceed to ${url} 2`,
                            messageComponent: DummyMessageComponent,
                            closable: false,
                            confirmBtnModel: {
                                text: 'Proceed 10',
                                iconShape: 'close',
                                iconPosition: 'left'
                            }
                        })
                        .then((value) => {
                            expect(value).toBeTrue();
                            expect(confirmationServiceStub.confirm).toHaveBeenCalledWith({
                                title: `Proceed to ${url} 2`,
                                messageComponent: DummyMessageComponent,
                                closable: false,
                                confirmBtnModel: {
                                    text: 'Proceed 10',
                                    iconShape: 'close',
                                    iconPosition: 'left'
                                }
                            } as UrlOpenerModel);
                            expect(consoleErrorSpy).toHaveBeenCalledWith(
                                `${UrlOpenerService.CLASS_NAME}: Potential bug found, cannot serialize provided object`
                            );
                            expect(cookieServiceStub.set).not.toHaveBeenCalled();
                            done();
                        });
                });

                it(`should verify will reject if cannot open external url`, (done) => {
                    // Given
                    const url = 'http://unknown.something.аусеров/pathname/context/100';
                    // @ts-ignore
                    spyOn(UrlOpenerService, '_openExternalUrl').and.returnValue(false);
                    confirmationServiceStub.confirm.and.returnValue(Promise.resolve({ doNotShowFutureConfirmation: true }));

                    // When
                    service
                        .open(url, '_blank', {
                            title: 'Proceed title 100',
                            message: 'Proceed message 100',
                            confirmBtnModel: {
                                text: 'Some text button proceed'
                            }
                        })
                        .then(() => {
                            done.fail(`should not enter here`);
                        })
                        .catch((reason) => {
                            expect(confirmationServiceStub.confirm).toHaveBeenCalledWith({
                                title: 'Proceed title 100',
                                message: 'Proceed message 100',
                                closable: true,
                                confirmBtnModel: {
                                    text: 'Some text button proceed'
                                }
                            } as UrlOpenerModel);
                            expect(reason).toEqual(new Error(`${UrlOpenerService.CLASS_NAME}: Exception thrown cannot open external url`));
                            done();
                        });
                });
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
