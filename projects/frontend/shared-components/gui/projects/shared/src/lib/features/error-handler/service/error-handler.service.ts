

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/unified-signatures */

import { Injectable } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';

import { Observable, throwError } from 'rxjs';

import { VmwToastType } from '../../../commons';

import { CollectionsUtil } from '../../../utils';

import { FormattedError, Toast } from '../../toasts/model';
import { ToastService } from '../../toasts/service';

export interface ErrorHandlerConfig {
    title?: Toast['title'];
    description?: Toast['description'];
    type?: Toast['type'];
}

/**
 * ** Error handler service.
 *
 *
 */
@Injectable()
export class ErrorHandlerService {
    /**
     * ** Constructor.
     */
    constructor(private readonly toastService: ToastService) {
    }

    /**
     * ** Handle Error in rxjs stream.
     *
     *   - Show Toast message
     *   - Log it to console
     *   - Re-throw new Error('Something unexpected happened')
     */
    handleError = (error: Error): Observable<never> => {
        this.processError(error);

        const newError = new Error('Something unexpected happened');

        return throwError(() => newError);
    };

    /**
     * ** Process Error.
     *
     *   - Show Toast message
     *   - Log it to console
     */
    processError(error: Error): void;
    processError(error: Error, overriddenConfig: ErrorHandlerConfig): void;
    processError(error: Error, overriddenConfig?: ErrorHandlerConfig): void {
        if (error instanceof HttpErrorResponse) {
            if (error.error instanceof ErrorEvent) { // A client-side or network error occurred.
                const toast = ErrorHandlerService._createToastConfigForError(error, overriddenConfig);

                console.error(`An error occurred: ${ error.error.message }`);

                this.toastService.show(toast);
            } else { // Server side error occurred.
                const toast = ErrorHandlerService._createToastConfigForHttpErrorResponse(error, overriddenConfig);

                console.error(error.error ?? error);

                this.toastService.show(toast);
            }
        } else { // Runtime error occurred, potential bug.
            const toast = ErrorHandlerService._createToastConfigForError(error, overriddenConfig);

            console.error(error);

            this.toastService.show(toast);
        }
    }

    /* eslint-disable @typescript-eslint/member-ordering */

    private static _createToastConfigForHttpErrorResponse(error: HttpErrorResponse, overriddenConfig: ErrorHandlerConfig): Toast {
        let title: string;
        let description: string;
        let rootError: Error = error.error as Error;
        const responseStatus = error.status;

        if (error.status === 403) {
            title = 'ACCESS DENIED';
            description = 'You are not authorized for this content!\ ' +
                'If you think it is a mistake please contact the data owners and request them to grant you access.';
        } else if (error.status === 500) {
            title = (error.error as FormattedError)?.what
                ? (error.error as FormattedError).what
                : 'Internal Server Error';
            description = (error.error as FormattedError)?.why
                ? (error.error as FormattedError).why
                : 'We are sorry for the inconvenience.' +
                'Please try again or come back later, and if the issue persists – please copy the details and report the error.';
        } else if (CollectionsUtil.isNil(error.error)) {
            title = ErrorHandlerService._getErrorTitle(error.status);
            description = 'Operation failed';
            rootError = error;
        } else if (error.error && (error.error as FormattedError).what && (error.error as FormattedError).why) {
            title = (error.error as FormattedError).what;
            description = (error.error as FormattedError).why;
        } else if (typeof error.error === 'string') {
            title = error.error;
            description = error.message;
        } else {
            title = ErrorHandlerService._getErrorTitle(error.status);
            description = error.message;
        }

        return ErrorHandlerService._createToastConfig(
            title,
            description,
            rootError,
            responseStatus,
            overriddenConfig
        );
    }

    private static _createToastConfigForError(error: Error, overriddenConfig: ErrorHandlerConfig): Toast {
        return ErrorHandlerService._createToastConfig(
            `An error occurred: ${ error?.message }`,
            'We are sorry for the inconvenience.' +
            'Please try again or come back later, and if the issue persists – please copy the details and report the error.',
            error,
            undefined,
            overriddenConfig
        );
    }

    private static _getErrorTitle(status: number): string {
        switch (status) {
            case 400:
                return 'Invalid param';
            case 401:
                return 'Unauthorized';
            case 404:
                return 'Not Found';
            case 405:
                return 'Not Allowed';
            case 422:
                return 'Invalid operation';
            default:
                return 'Unknown Error';
        }
    }

    private static _createToastConfig(
        title: string,
        description: string,
        error: Error,
        responseStatus: number = null,
        overriddenConfig: ErrorHandlerConfig = null): Toast {

        let toastConfig: Toast = {
            title,
            description,
            type: VmwToastType.FAILURE,
            error,
            responseStatus
        };

        if (CollectionsUtil.isDefined(overriddenConfig)) {
            toastConfig = {
                ...toastConfig,
                ...overriddenConfig,
                extendedData: {
                    title,
                    description
                }
            };
        }

        return toastConfig;
    }
}
