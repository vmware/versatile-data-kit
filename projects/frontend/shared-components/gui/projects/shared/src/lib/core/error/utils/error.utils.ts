/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpErrorResponse, HttpStatusCode } from '@angular/common/http';

import { CollectionsUtil } from '../../../utils';

import { ApiErrorMessage, ErrorRecord, generateErrorCode, ServiceHttpErrorCodes } from '../../../common';

/**
 * ** Process service HTTP request error and return ErrorRecord.
 *
 * @param {string} objectUUID - is objectUUID of the Object for which processing error is invoked
 * @param {Record<keyof ServiceHttpErrorCodes, string>} serviceHttpErrorCodes - is map of Service method supported error codes auto-handling
 * @param {unknown} error - is actual error object reference
 */
export const processServiceRequestError = (
    objectUUID: string,
    serviceHttpErrorCodes: Record<keyof ServiceHttpErrorCodes, string>,
    error: unknown
): ErrorRecord => {
    const _objectUUID = CollectionsUtil.isDefined(objectUUID) ? objectUUID : CollectionsUtil.generateObjectUUID('UnknownClassName');

    if (!CollectionsUtil.isLiteralObject(serviceHttpErrorCodes)) {
        return {
            code: generateErrorCode('UnknownClassName', 'UnknownPublicName', 'UnknownMethodName', 'Generic'),
            objectUUID: _objectUUID,
            error: error instanceof Error ? error : null
        };
    }

    if (error instanceof HttpErrorResponse) {
        let code: string;

        switch (error.status) {
            case HttpStatusCode.BadRequest:
                code = serviceHttpErrorCodes.BadRequest;
                break;
            case HttpStatusCode.Unauthorized:
                code = serviceHttpErrorCodes.Unauthorized;
                break;
            case HttpStatusCode.Forbidden:
                code = serviceHttpErrorCodes.Forbidden;
                break;
            case HttpStatusCode.NotFound:
                code = serviceHttpErrorCodes.NotFound;
                break;
            case HttpStatusCode.MethodNotAllowed:
                code = serviceHttpErrorCodes.MethodNotAllowed;
                break;
            case HttpStatusCode.Conflict:
                code = serviceHttpErrorCodes.Conflict;
                break;
            case HttpStatusCode.UnprocessableEntity:
                code = serviceHttpErrorCodes.UnprocessableEntity;
                break;
            case HttpStatusCode.InternalServerError:
                code = serviceHttpErrorCodes.InternalServerError;
                break;
            case HttpStatusCode.ServiceUnavailable:
                code = serviceHttpErrorCodes.ServiceUnavailable;
                break;
            default:
                code = serviceHttpErrorCodes.Unknown;
        }

        return {
            code,
            objectUUID: _objectUUID,
            error,
            httpStatusCode: error.status
        };
    }

    return {
        code: serviceHttpErrorCodes.Unknown,
        objectUUID: _objectUUID,
        error: error instanceof Error ? error : null
    };
};

/**
 * ** Get API formatted error message from provided Error.
 */
export const getApiFormattedErrorMessage = (error: Error): ApiErrorMessage => {
    let statusCode: number = null;

    if (error instanceof HttpErrorResponse) {
        if (CollectionsUtil.isString(error.error)) {
            return {
                what: `${error.error}`,
                why: `${error.message}`
            };
        }

        if (CollectionsUtil.isLiteralObject(error.error)) {
            return {
                what: `${(error.error as ApiErrorMessage).what}`,
                why: `${(error.error as ApiErrorMessage).why}`,
                consequences: `${(error.error as ApiErrorMessage).consequences}`,
                countermeasures: `${(error.error as ApiErrorMessage).countermeasures}`
            };
        }

        statusCode = error.status;
    }

    return {
        what: 'Please contact Superollider and report the issue',
        why: getHumanReadableStatusText(statusCode)
    };
};

/**
 * ** Get Human readable text from HTTP error status code.
 */
export const getHumanReadableStatusText = (httpErrorStatus: number): string => {
    switch (httpErrorStatus) {
        case HttpStatusCode.BadRequest:
            return 'Invalid param';
        case HttpStatusCode.Unauthorized:
            return 'Unauthorized';
        case HttpStatusCode.Forbidden:
            return 'Forbidden';
        case HttpStatusCode.NotFound:
            return 'Not Found';
        case HttpStatusCode.MethodNotAllowed:
            return 'Not Allowed';
        case HttpStatusCode.Conflict:
            return 'Conflict';
        case HttpStatusCode.UnprocessableEntity:
            return 'Invalid operation';
        case HttpStatusCode.InternalServerError:
            return 'Internal Server Error';
        case HttpStatusCode.ServiceUnavailable:
            return 'Service Unavailable';
        default:
            return 'Unknown Error';
    }
};
