

/* eslint-disable max-len */

import { HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { fakeAsync, TestBed, tick } from '@angular/core/testing';

import { Observable } from 'rxjs';

import { VmwToastType } from '../../../commons';

import { CallFake } from '../../../unit-testing';

import { ToastService } from '../../toasts/service';
import { FormattedError } from '../../toasts/model';

import { ErrorHandlerService } from './error-handler.service';

describe('ErrorHandlerService', () => {
    let toastServiceStub: jasmine.SpyObj<ToastService>;
    let service: ErrorHandlerService;

    beforeEach(() => {
        toastServiceStub = jasmine.createSpyObj<ToastService>('toastService', ['show']);

        TestBed.configureTestingModule({
            providers: [
                { provide: ToastService, useValue: toastServiceStub },
                ErrorHandlerService
            ]
        });

        service = TestBed.inject(ErrorHandlerService);
    });

    it('should verify instance is created', () => {
        // Then
        expect(service).toBeDefined();
    });

    describe('Methods::', () => {
        describe('|handleError|', () => {
            it('should verify will return Observable in error state', fakeAsync(() => {
                // Given
                const rootError = new Error('some error');
                const processErrorSpy: jasmine.Spy<(error: Error) => void> = spyOn(service, 'processError');

                // When
                const observable$ = service.handleError(rootError);

                // Then
                expect(processErrorSpy).toHaveBeenCalledWith(rootError);
                expect(observable$).toBeInstanceOf(Observable);

                observable$.subscribe(
                    CallFake,
                    (error: unknown) => {
                        expect(error).toEqual(new Error('Something unexpected happened'));
                    });

                tick(100);
            }));
        });

        describe('|processError|', () => {
            let logErrorSpy: jasmine.Spy;
            let url: string;

            beforeEach(() => {
                logErrorSpy = spyOn(console, 'error').and.callFake(CallFake);
                url = '/shared/resources/statistics/15';
            });

            describe('should verify will invoke ToastService with expected Toast:', () => {
                it('Error is Nil', () => {
                    // Given
                    const rootError: Error = null;

                    // When
                    service.processError(rootError);

                    // Then
                    expect(logErrorSpy).toHaveBeenCalledWith(rootError);
                    expect(toastServiceStub.show).toHaveBeenCalledWith({
                        type: VmwToastType.FAILURE,
                        title: `An error occurred: undefined`,
                        description: 'We are sorry for the inconvenience.' +
                            'Please try again or come back later, and if the issue persists – please copy the details and report the error.',
                        error: rootError,
                        responseStatus: null
                    });
                });

                it('Error of type SyntaxError', () => {
                    // Given
                    const rootError = new SyntaxError('Uncaught SyntaxError: Function statements require a function name');

                    // When
                    service.processError(rootError);

                    // Then
                    expect(logErrorSpy).toHaveBeenCalledWith(rootError);
                    expect(toastServiceStub.show).toHaveBeenCalledWith({
                        type: VmwToastType.FAILURE,
                        title: `An error occurred: ${ rootError.message }`,
                        description: 'We are sorry for the inconvenience.' +
                            'Please try again or come back later, and if the issue persists – please copy the details and report the error.',
                        error: rootError,
                        responseStatus: null
                    });
                });

                it('Error of type SyntaxError and provided additional ErrorHandlerConfig', () => {
                    // Given
                    const rootError = new SyntaxError('Uncaught SyntaxError: Function statements require a function name');

                    // When
                    service.processError(
                        rootError,
                        {
                            title: '---> Unknown error happened',
                            description: '---> Please try again later, or contact you administrator.',
                            type: VmwToastType.INFO
                        }
                    );

                    // Then
                    expect(logErrorSpy).toHaveBeenCalledWith(rootError);
                    expect(toastServiceStub.show).toHaveBeenCalledWith({
                        title: '---> Unknown error happened',
                        description: '---> Please try again later, or contact you administrator.',
                        type: VmwToastType.INFO,
                        error: rootError,
                        responseStatus: null,
                        extendedData: {
                            title: `An error occurred: ${ rootError.message }`,
                            description: 'We are sorry for the inconvenience.' +
                                'Please try again or come back later, and if the issue persists – please copy the details and report the error.'
                        }
                    });
                });

                it('Error of type HttpErrorResponse when sub-error is of type ErrorEvent', () => {
                    // Given
                    const topRootError = new ErrorEvent('Connection lost');
                    const rootError = new HttpErrorResponse({
                        error: topRootError,
                        status: 0,
                        url,
                        headers: new HttpHeaders()
                    });

                    // When
                    service.processError(rootError);

                    // Then
                    expect(logErrorSpy).toHaveBeenCalledWith(`An error occurred: ${ (rootError.error as Error).message }`);
                    expect(toastServiceStub.show).toHaveBeenCalledWith({
                        type: VmwToastType.FAILURE,
                        title: `An error occurred: ${ rootError.message }`,
                        description: 'We are sorry for the inconvenience.' +
                            'Please try again or come back later, and if the issue persists – please copy the details and report the error.',
                        error: rootError,
                        responseStatus: null
                    });
                });

                it('Error of type HttpErrorResponse when status 403 and sub-error is server side error', () => {
                    // Given
                    const topRootError = { message: 'Access Denied' } as Error;
                    const rootError = new HttpErrorResponse({
                        error: topRootError,
                        status: 403,
                        url,
                        headers: new HttpHeaders()
                    });

                    // When
                    service.processError(rootError);

                    // Then
                    expect(logErrorSpy).toHaveBeenCalledWith(topRootError);
                    expect(toastServiceStub.show).toHaveBeenCalledWith({
                        type: VmwToastType.FAILURE,
                        title: 'ACCESS DENIED',
                        description: 'You are not authorized for this content!\ ' +
                            'If you think it is a mistake please contact the data owners and request them to grant you access.',
                        error: topRootError,
                        responseStatus: 403
                    });
                });

                it('Error of type HttpErrorResponse when status 500 and sub-error is Nil', () => {
                    // Given
                    const topRootError = null;
                    const rootError = new HttpErrorResponse({
                        error: topRootError,
                        status: 500,
                        url,
                        headers: new HttpHeaders()
                    });

                    // When
                    service.processError(rootError);

                    // Then
                    expect(logErrorSpy).toHaveBeenCalledWith(rootError);
                    expect(toastServiceStub.show).toHaveBeenCalledWith({
                        type: VmwToastType.FAILURE,
                        title: 'Internal Server Error',
                        description: 'We are sorry for the inconvenience.' +
                            'Please try again or come back later, and if the issue persists – please copy the details and report the error.',
                        error: topRootError,
                        responseStatus: 500
                    });
                });

                it('Error of type HttpErrorResponse when status 500 and sub-error is server side error with what and why', () => {
                    // Given
                    const topRootError = {
                        message: 'Internal Server Error',
                        what: 'Server is down, internal server error',
                        why: 'Unknown error happened on server side'
                    };
                    const rootError = new HttpErrorResponse({
                        error: topRootError,
                        status: 500,
                        url,
                        headers: new HttpHeaders()
                    });

                    // When
                    service.processError(rootError);

                    // Then
                    expect(logErrorSpy).toHaveBeenCalledWith(topRootError);
                    expect(toastServiceStub.show).toHaveBeenCalledWith({
                        type: VmwToastType.FAILURE,
                        title: topRootError.what,
                        description: topRootError.why,
                        error: topRootError,
                        responseStatus: 500
                    });
                });

                it('Error of type HttpErrorResponse when status 500 and sub-error is server side error', () => {
                    // Given
                    const topRootError = {
                        message: 'Internal Server Error'
                    } as Error;
                    const rootError = new HttpErrorResponse({
                        error: topRootError,
                        status: 500,
                        url,
                        headers: new HttpHeaders()
                    });

                    // When
                    service.processError(rootError);

                    // Then
                    expect(logErrorSpy).toHaveBeenCalledWith(topRootError);
                    expect(toastServiceStub.show).toHaveBeenCalledWith({
                        type: VmwToastType.FAILURE,
                        title: 'Internal Server Error',
                        description: 'We are sorry for the inconvenience.' +
                            'Please try again or come back later, and if the issue persists – please copy the details and report the error.',
                        error: topRootError,
                        responseStatus: 500
                    });
                });

                it('Error of type HttpErrorResponse when status 400 and sub-error is Nil', () => {
                    // Given
                    const rootError = new HttpErrorResponse({
                        error: null,
                        status: 400,
                        url,
                        headers: new HttpHeaders()
                    });

                    // When
                    service.processError(rootError);

                    // Then
                    expect(logErrorSpy).toHaveBeenCalledWith(rootError);
                    expect(toastServiceStub.show).toHaveBeenCalledWith({
                        type: VmwToastType.FAILURE,
                        title: 'Invalid param',
                        description: 'Operation failed',
                        error: rootError,
                        responseStatus: 400
                    });
                });

                it('Error of type HttpErrorResponse when status 401 and sub-error is Nil', () => {
                    // Given
                    const rootError = new HttpErrorResponse({
                        error: null,
                        status: 401,
                        url,
                        headers: new HttpHeaders()
                    });

                    // When
                    service.processError(rootError);

                    // Then
                    expect(logErrorSpy).toHaveBeenCalledWith(rootError);
                    expect(toastServiceStub.show).toHaveBeenCalledWith({
                        type: VmwToastType.FAILURE,
                        title: 'Unauthorized',
                        description: 'Operation failed',
                        error: rootError,
                        responseStatus: 401
                    });
                });

                it('Error of type HttpErrorResponse when status 404 and sub-error is Nil', () => {
                    // Given
                    const rootError = new HttpErrorResponse({
                        error: null,
                        status: 404,
                        url,
                        headers: new HttpHeaders()
                    });

                    // When
                    service.processError(rootError);

                    // Then
                    expect(logErrorSpy).toHaveBeenCalledWith(rootError);
                    expect(toastServiceStub.show).toHaveBeenCalledWith({
                        type: VmwToastType.FAILURE,
                        title: 'Not Found',
                        description: 'Operation failed',
                        error: rootError,
                        responseStatus: 404
                    });
                });

                it('Error of type HttpErrorResponse when status 405 and sub-error is Nil', () => {
                    // Given
                    const rootError = new HttpErrorResponse({
                        error: null,
                        status: 405,
                        url,
                        headers: new HttpHeaders()
                    });

                    // When
                    service.processError(rootError);

                    // Then
                    expect(logErrorSpy).toHaveBeenCalledWith(rootError);
                    expect(toastServiceStub.show).toHaveBeenCalledWith({
                        type: VmwToastType.FAILURE,
                        title: 'Not Allowed',
                        description: 'Operation failed',
                        error: rootError,
                        responseStatus: 405
                    });
                });

                it('Error of type HttpErrorResponse when status 422 and sub-error is Nil', () => {
                    // Given
                    const rootError = new HttpErrorResponse({
                        error: null,
                        status: 422,
                        url,
                        headers: new HttpHeaders()
                    });

                    // When
                    service.processError(rootError);

                    // Then
                    expect(logErrorSpy).toHaveBeenCalledWith(rootError);
                    expect(toastServiceStub.show).toHaveBeenCalledWith({
                        type: VmwToastType.FAILURE,
                        title: 'Invalid operation',
                        description: 'Operation failed',
                        error: rootError,
                        responseStatus: 422
                    });
                });

                it('Error of type HttpErrorResponse when status 501 and sub-error is Nil', () => {
                    // Given
                    const rootError = new HttpErrorResponse({
                        error: null,
                        status: 501,
                        url,
                        headers: new HttpHeaders()
                    });

                    // When
                    service.processError(rootError);

                    // Then
                    expect(logErrorSpy).toHaveBeenCalledWith(rootError);
                    expect(toastServiceStub.show).toHaveBeenCalledWith({
                        type: VmwToastType.FAILURE,
                        title: 'Unknown Error',
                        description: 'Operation failed',
                        error: rootError,
                        responseStatus: 501
                    });
                });

                it('Error of type HttpErrorResponse when status 507 and sub-error is server side error with what and why', () => {
                    // Given
                    const rootError = new HttpErrorResponse({
                        error: {
                            message: 'Insufficient Storage',
                            what: 'Insufficient Storage on server',
                            why: 'Cloud storage id down'
                        },
                        status: 507,
                        url,
                        headers: new HttpHeaders()
                    });

                    // When
                    service.processError(rootError);

                    // Then
                    expect(logErrorSpy).toHaveBeenCalledWith(rootError.error);
                    expect(toastServiceStub.show).toHaveBeenCalledWith({
                        type: VmwToastType.FAILURE,
                        title: (rootError.error as FormattedError).what,
                        description: (rootError.error as FormattedError).why,
                        error: rootError.error,
                        responseStatus: 507
                    });
                });

                it('Error of type HttpErrorResponse when status 423 and sub-error is of type string', () => {
                    // Given
                    const rootError = new HttpErrorResponse({
                        error: 'Entity is locked',
                        status: 423,
                        url,
                        headers: new HttpHeaders()
                    });

                    // When
                    service.processError(rootError);

                    // Then
                    expect(logErrorSpy).toHaveBeenCalledWith(rootError.error);
                    expect(toastServiceStub.show).toHaveBeenCalledWith({
                        type: VmwToastType.FAILURE,
                        title: rootError.error,
                        description: rootError.message,
                        error: rootError.error,
                        responseStatus: 423
                    });
                });

                it('Error of type HttpErrorResponse when status 417 and sub-error is server side error', () => {
                    // Given
                    const rootError = new HttpErrorResponse({
                        error: {
                            message: 'Expectation Failed'
                        },
                        status: 417,
                        url,
                        headers: new HttpHeaders()
                    });

                    // When
                    service.processError(rootError);

                    // Then
                    expect(logErrorSpy).toHaveBeenCalledWith(rootError.error);
                    expect(toastServiceStub.show).toHaveBeenCalledWith({
                        type: VmwToastType.FAILURE,
                        title: 'Unknown Error',
                        description: rootError.message,
                        error: rootError.error,
                        responseStatus: 417
                    });
                });
            });
        });
    });
});
