/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/no-explicit-any,@typescript-eslint/naming-convention */

import { HttpStatusCode } from '@angular/common/http';

/**
 * ** Error Record.
 */
export interface ErrorRecord {
    /**
     * ** Error code (token).
     *
     *      - Code (token) should start with Class name,
     *              then followed by underscore and class PUBLIC_NAME,
     *              then followed by underscore and method name or underscore with some error specifics,
     *              and followed by underscore and additional details to avoid overlaps with other Class errors.
     *
     * <br/>
     * <i>pattern</i>:
     * <p>
     *     <Class Name><b>_</b><class PUBLIC_NAME><b>_</b><class method name><b>_</b><additional details, like HTTP Status Code>
     * </p>
     */
    code: string;

    /**
     * ** Object UUID.
     */
    objectUUID: string;

    /**
     * ** Actual error object.
     */
    error: Error;

    /**
     * ** Timestamp in milliseconds when Error is recorded in Store.
     *
     *      - Generated using Date.now(), when record is written in store.
     */
    time?: number;

    /**
     * ** Http status code.
     *
     *      - if present assume it is Http request error.
     */
    httpStatusCode?: HttpStatusCode;
}

/**
 * ** Auto generated error codes for every method of TaurusBaseApiService subclasses.
 */
export type ServiceHttpErrorCodes = {
    /**
     * ** Service method error code that match all method error codes if used as error code pattern (translated in RegExp).
     */
    All: string;

    /**
     * ** Service method error code that match all method error codes from group 4xx if used as error code pattern (translated in RegExp).
     */
    ClientErrors: string;

    /**
     * ** Service method error code for Bad request.
     *
     *      - code: 400
     */
    BadRequest: string;

    /**
     * ** Service method error code for Unauthorized.
     *
     *      - code: 401
     */
    Unauthorized: string;

    /**
     * ** Service method error code for Forbidden.
     *
     *      - code: 403
     */
    Forbidden: string;

    /**
     * ** Service method error code for Not found.
     *
     *      - code: 404
     */
    NotFound: string;

    /**
     * ** Service method error code for Method Not Allowed.
     *
     *      - code: 405
     */
    MethodNotAllowed: string;

    /**
     * ** Service method error code for Conflict.
     *
     *      - code: 409
     */
    Conflict: string;

    /**
     * ** Service method code for Unprocessable entity.
     *
     *      - code: 422
     */
    UnprocessableEntity: string;

    /**
     * ** Service method error code that match all method error codes from group 5xx if used as error code pattern (translated in RegExp).
     */
    ServerErrors: string;

    /**
     * ** Service method error code for Internal Server Error.
     *
     *      - code: 500
     */
    InternalServerError: string;

    /**
     * ** Service method error code for Service Unavailable.
     *
     *      - code: 503
     */
    ServiceUnavailable: string;

    /**
     * ** Service method error code for Unknown Error.
     */
    Unknown: string;
};
