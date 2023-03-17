/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/naming-convention,
                  @typescript-eslint/restrict-template-expressions,
                  @typescript-eslint/no-unsafe-member-access */

import { HttpErrorResponse, HttpStatusCode } from '@angular/common/http';

import { CollectionsUtil } from '../../../utils';

import { ApiErrorMessage, ErrorRecord, ServiceHttpErrorCodes } from '../../../common';

import { getApiFormattedErrorMessage, getHumanReadableStatusText, processServiceRequestError } from './error.utils';

describe('processServiceRequestError', () => {
    describe('should verify will return ErrorRecord for potential code bugs, when', () => {
        const error = new Error('Random Error');
        const syntaxError = new SyntaxError('Unsupported action');
        const params: Array<[string, string, Record<keyof ServiceHttpErrorCodes, string>, unknown, ErrorRecord, number]> = [
            [
                'objectUUID is null, ServiceHttpErrorCodes is null and error is literal object',
                null,
                null,
                {},
                {
                    code: 'UnknownClassName_UnknownPublicName_UnknownMethodName_Generic',
                    error: null,
                    objectUUID: 'ErrorCodeClass_uuid'
                },
                1
            ],
            [
                'objectUUID is provided, ServiceHttpErrorCodes is undefined and error is Error provided',
                'ErrorCodeClass_uuid_111',
                undefined,
                error,
                {
                    code: 'UnknownClassName_UnknownPublicName_UnknownMethodName_Generic',
                    error,
                    objectUUID: 'ErrorCodeClass_uuid_111'
                },
                0
            ],
            [
                'objectUUID is undefined, ServiceHttpErrorCodes is Map and error is Array',
                undefined,
                new Map<keyof ServiceHttpErrorCodes, string>() as any,
                [],
                {
                    code: 'UnknownClassName_UnknownPublicName_UnknownMethodName_Generic',
                    error: null,
                    objectUUID: 'ErrorCodeClass_uuid'
                },
                1
            ],
            [
                'objectUUID is provided, ServiceHttpErrorCodes is Array and error is SyntaxError provided',
                'ErrorCodeClass_uuid_222',
                [] as any,
                syntaxError,
                {
                    code: 'UnknownClassName_UnknownPublicName_UnknownMethodName_Generic',
                    error: syntaxError,
                    objectUUID: 'ErrorCodeClass_uuid_222'
                },
                0
            ]
        ];

        for (const [description, objectUUID, serviceHttpErrorCodes, _error, assertion, numberOfInvoke] of params) {
            it(`${description}`, () => {
                // Given
                const spyGenerateObjectUUID = spyOn(CollectionsUtil, 'generateObjectUUID').and.returnValue('ErrorCodeClass_uuid');

                // When
                const errorRecord = processServiceRequestError(objectUUID, serviceHttpErrorCodes, _error);

                // Then
                expect(errorRecord).toEqual(assertion);

                expect(spyGenerateObjectUUID).toHaveBeenCalledTimes(numberOfInvoke);
                if (numberOfInvoke > 0) {
                    expect(spyGenerateObjectUUID).toHaveBeenCalledWith('UnknownClassName');
                }
            });
        }
    });

    describe('should verify will return ErrorRecord for usual scenarios when errorCode is', () => {
        const serviceHttpErrorCodes: Record<keyof ServiceHttpErrorCodes, string> = {
            All: 'ErrorCodeClass_SpiedPublicName_andMethod_',
            ClientErrors: 'ErrorCodeClass_SpiedPublicName_andMethod_4\\d\\d',
            BadRequest: 'ErrorCodeClass_SpiedPublicName_andMethod_400',
            Unauthorized: 'ErrorCodeClass_SpiedPublicName_andMethod_401',
            Forbidden: 'ErrorCodeClass_SpiedPublicName_andMethod_403',
            NotFound: 'ErrorCodeClass_SpiedPublicName_andMethod_404',
            MethodNotAllowed: 'ErrorCodeClass_SpiedPublicName_andMethod_405',
            Conflict: 'ErrorCodeClass_SpiedPublicName_andMethod_409',
            UnprocessableEntity: 'ErrorCodeClass_SpiedPublicName_andMethod_422',
            ServerErrors: 'ErrorCodeClass_SpiedPublicName_andMethod_5\\d\\d',
            InternalServerError: 'ErrorCodeClass_SpiedPublicName_andMethod_500',
            ServiceUnavailable: 'ErrorCodeClass_SpiedPublicName_andMethod_503',
            Unknown: 'ErrorCodeClass_SpiedPublicName_andMethod_unknown'
        };
        const errors: Partial<Record<keyof ServiceHttpErrorCodes, HttpErrorResponse>> = {
            BadRequest: new HttpErrorResponse({
                status: HttpStatusCode.BadRequest,
                error: new Error(`${HttpStatusCode.BadRequest}`)
            }),
            Unauthorized: new HttpErrorResponse({
                status: HttpStatusCode.Unauthorized,
                error: new Error(`${HttpStatusCode.Unauthorized}`)
            }),
            Forbidden: new HttpErrorResponse({
                status: HttpStatusCode.Forbidden,
                error: new Error(`${HttpStatusCode.Forbidden}`)
            }),
            NotFound: new HttpErrorResponse({
                status: HttpStatusCode.NotFound,
                error: new Error(`${HttpStatusCode.NotFound}`)
            }),
            MethodNotAllowed: new HttpErrorResponse({
                status: HttpStatusCode.MethodNotAllowed,
                error: new Error(`${HttpStatusCode.MethodNotAllowed}`)
            }),
            Conflict: new HttpErrorResponse({
                status: HttpStatusCode.Conflict,
                error: new Error(`${HttpStatusCode.Conflict}`)
            }),
            UnprocessableEntity: new HttpErrorResponse({
                status: HttpStatusCode.UnprocessableEntity,
                error: new Error(`${HttpStatusCode.UnprocessableEntity}`)
            }),
            InternalServerError: new HttpErrorResponse({
                status: HttpStatusCode.InternalServerError,
                error: new Error(`${HttpStatusCode.InternalServerError}`)
            }),
            ServiceUnavailable: new HttpErrorResponse({
                status: HttpStatusCode.ServiceUnavailable,
                error: new Error(`${HttpStatusCode.ServiceUnavailable}`)
            }),
            Unknown: new HttpErrorResponse({
                status: HttpStatusCode.BadGateway,
                error: new Error(`${HttpStatusCode.BadGateway}`)
            })
        };
        const params: Array<[string, string, Record<keyof ServiceHttpErrorCodes, string>, HttpErrorResponse, ErrorRecord, number]> = [
            [
                `"${serviceHttpErrorCodes.BadRequest}" for HttpStatusCode "${HttpStatusCode.BadRequest}"`,
                null,
                serviceHttpErrorCodes,
                errors.BadRequest,
                {
                    code: serviceHttpErrorCodes.BadRequest,
                    error: errors.BadRequest,
                    objectUUID: 'ErrorCodeClass_uuid',
                    httpStatusCode: HttpStatusCode.BadRequest
                },
                1
            ],
            [
                `"${serviceHttpErrorCodes.Unauthorized}" for HttpStatusCode "${HttpStatusCode.Unauthorized}"`,
                'ErrorCodeClass_uuid_111',
                serviceHttpErrorCodes,
                errors.Unauthorized,
                {
                    code: serviceHttpErrorCodes.Unauthorized,
                    error: errors.Unauthorized,
                    objectUUID: 'ErrorCodeClass_uuid_111',
                    httpStatusCode: HttpStatusCode.Unauthorized
                },
                0
            ],
            [
                `"${serviceHttpErrorCodes.Forbidden}" for HttpStatusCode "${HttpStatusCode.Forbidden}"`,
                'ErrorCodeClass_uuid_112',
                serviceHttpErrorCodes,
                errors.Forbidden,
                {
                    code: serviceHttpErrorCodes.Forbidden,
                    error: errors.Forbidden,
                    objectUUID: 'ErrorCodeClass_uuid_112',
                    httpStatusCode: HttpStatusCode.Forbidden
                },
                0
            ],
            [
                `"${serviceHttpErrorCodes.NotFound}" for HttpStatusCode "${HttpStatusCode.NotFound}"`,
                undefined,
                serviceHttpErrorCodes,
                errors.NotFound,
                {
                    code: serviceHttpErrorCodes.NotFound,
                    error: errors.NotFound,
                    objectUUID: 'ErrorCodeClass_uuid',
                    httpStatusCode: HttpStatusCode.NotFound
                },
                1
            ],
            [
                `"${serviceHttpErrorCodes.MethodNotAllowed}" for HttpStatusCode "${HttpStatusCode.MethodNotAllowed}"`,
                'ErrorCodeClass_uuid_113',
                serviceHttpErrorCodes,
                errors.MethodNotAllowed,
                {
                    code: serviceHttpErrorCodes.MethodNotAllowed,
                    error: errors.MethodNotAllowed,
                    objectUUID: 'ErrorCodeClass_uuid_113',
                    httpStatusCode: HttpStatusCode.MethodNotAllowed
                },
                0
            ],
            [
                `"${serviceHttpErrorCodes.Conflict}" for HttpStatusCode "${HttpStatusCode.Conflict}"`,
                'ErrorCodeClass_uuid_114',
                serviceHttpErrorCodes,
                errors.Conflict,
                {
                    code: serviceHttpErrorCodes.Conflict,
                    error: errors.Conflict,
                    objectUUID: 'ErrorCodeClass_uuid_114',
                    httpStatusCode: HttpStatusCode.Conflict
                },
                0
            ],
            [
                `"${serviceHttpErrorCodes.UnprocessableEntity}" for HttpStatusCode "${HttpStatusCode.UnprocessableEntity}"`,
                'ErrorCodeClass_uuid_115',
                serviceHttpErrorCodes,
                errors.UnprocessableEntity,
                {
                    code: serviceHttpErrorCodes.UnprocessableEntity,
                    error: errors.UnprocessableEntity,
                    objectUUID: 'ErrorCodeClass_uuid_115',
                    httpStatusCode: HttpStatusCode.UnprocessableEntity
                },
                0
            ],
            [
                `"${serviceHttpErrorCodes.InternalServerError}" for HttpStatusCode "${HttpStatusCode.InternalServerError}"`,
                'ErrorCodeClass_uuid_116',
                serviceHttpErrorCodes,
                errors.InternalServerError,
                {
                    code: serviceHttpErrorCodes.InternalServerError,
                    error: errors.InternalServerError,
                    objectUUID: 'ErrorCodeClass_uuid_116',
                    httpStatusCode: HttpStatusCode.InternalServerError
                },
                0
            ],
            [
                `"${serviceHttpErrorCodes.ServiceUnavailable}" for HttpStatusCode "${HttpStatusCode.ServiceUnavailable}"`,
                'ErrorCodeClass_uuid_117',
                serviceHttpErrorCodes,
                errors.ServiceUnavailable,
                {
                    code: serviceHttpErrorCodes.ServiceUnavailable,
                    error: errors.ServiceUnavailable,
                    objectUUID: 'ErrorCodeClass_uuid_117',
                    httpStatusCode: HttpStatusCode.ServiceUnavailable
                },
                0
            ],
            [
                `"${serviceHttpErrorCodes.Unknown}" for HttpStatusCode "${HttpStatusCode.BadGateway}"`,
                'ErrorCodeClass_uuid_118',
                serviceHttpErrorCodes,
                errors.Unknown,
                {
                    code: serviceHttpErrorCodes.Unknown,
                    error: errors.Unknown,
                    objectUUID: 'ErrorCodeClass_uuid_118',
                    httpStatusCode: HttpStatusCode.BadGateway
                },
                0
            ]
        ];

        for (const [_description, _objectUUID, _serviceHttpErrorCodes, _error, _assertion, _numberOfInvoke] of params) {
            it(`${_description}`, () => {
                // Given
                const spyGenerateObjectUUID = spyOn(CollectionsUtil, 'generateObjectUUID').and.returnValue('ErrorCodeClass_uuid');

                // When
                const _errorRecord = processServiceRequestError(_objectUUID, _serviceHttpErrorCodes, _error);

                // Then
                expect(_errorRecord).toEqual(_assertion);
                expect(spyGenerateObjectUUID).toHaveBeenCalledTimes(_numberOfInvoke);
                if (_numberOfInvoke > 0) {
                    expect(spyGenerateObjectUUID).toHaveBeenCalledWith('UnknownClassName');
                }
            });
        }
    });

    describe('should verify will return ErrorRecord for various cases when serviceHttpErrorRecords are provided and error is not HttpErrorResponse', () => {
        // Given
        const serviceHttpErrorCodes: Record<keyof ServiceHttpErrorCodes, string> = {
            All: 'ErrorCodeClass_SpiedPublicName_andMethod_',
            ClientErrors: 'ErrorCodeClass_SpiedPublicName_andMethod_4\\d\\d',
            BadRequest: 'ErrorCodeClass_SpiedPublicName_andMethod_400',
            Unauthorized: 'ErrorCodeClass_SpiedPublicName_andMethod_401',
            Forbidden: 'ErrorCodeClass_SpiedPublicName_andMethod_403',
            NotFound: 'ErrorCodeClass_SpiedPublicName_andMethod_404',
            MethodNotAllowed: 'ErrorCodeClass_SpiedPublicName_andMethod_405',
            Conflict: 'ErrorCodeClass_SpiedPublicName_andMethod_409',
            UnprocessableEntity: 'ErrorCodeClass_SpiedPublicName_andMethod_422',
            ServerErrors: 'ErrorCodeClass_SpiedPublicName_andMethod_5\\d\\d',
            InternalServerError: 'ErrorCodeClass_SpiedPublicName_andMethod_500',
            ServiceUnavailable: 'ErrorCodeClass_SpiedPublicName_andMethod_503',
            Unknown: 'ErrorCodeClass_SpiedPublicName_andMethod_unknown'
        };
        const errors: unknown[] = [new Error(`Random Error 1`), null, new Error(`Random Error 3`)];
        const params: Array<[string, string, Record<keyof ServiceHttpErrorCodes, string>, unknown, ErrorRecord, number]> = [
            [
                `error is instanceof Error`,
                null,
                serviceHttpErrorCodes,
                errors[0],
                {
                    code: serviceHttpErrorCodes.Unknown,
                    error: errors[0] as any,
                    objectUUID: 'ErrorCodeClass_uuid'
                },
                1
            ],
            [
                `error is null`,
                'ErrorCodeClass_uuid_111',
                serviceHttpErrorCodes,
                errors[1],
                {
                    code: serviceHttpErrorCodes.Unknown,
                    error: errors[1] as any,
                    objectUUID: 'ErrorCodeClass_uuid_111'
                },
                0
            ],
            [
                `error is instanceof Error`,
                'ErrorCodeClass_uuid_112',
                serviceHttpErrorCodes,
                errors[2],
                {
                    code: serviceHttpErrorCodes.Unknown,
                    error: errors[2] as any,
                    objectUUID: 'ErrorCodeClass_uuid_112'
                },
                0
            ]
        ];

        for (const [_description, _objectUUID, _serviceHttpErrorCodes, _error, _assertion, _numberOfInvoke] of params) {
            it(`${_description}`, () => {
                // Given
                const spyGenerateObjectUUID = spyOn(CollectionsUtil, 'generateObjectUUID').and.returnValue('ErrorCodeClass_uuid');

                // When
                const _errorRecord = processServiceRequestError(_objectUUID, _serviceHttpErrorCodes, _error);

                // Then
                expect(_errorRecord).toEqual(_assertion);
                expect(spyGenerateObjectUUID).toHaveBeenCalledTimes(_numberOfInvoke);
                if (_numberOfInvoke > 0) {
                    expect(spyGenerateObjectUUID).toHaveBeenCalledWith('UnknownClassName');
                }
            });
        }
    });
});

describe('getApiFormattedErrorMessage', () => {
    describe('parameterized_test', () => {
        const errors: HttpErrorResponse[] = [
            new HttpErrorResponse({
                status: HttpStatusCode.InternalServerError,
                error: `Something bad happened and it's string`
            }),
            new HttpErrorResponse({
                status: HttpStatusCode.InternalServerError,
                error: {
                    what: `text what`,
                    why: `text why`,
                    consequences: `text consequences`,
                    countermeasures: `text countermeasures`
                }
            }),
            new HttpErrorResponse({
                status: HttpStatusCode.InternalServerError,
                error: null
            }),
            new HttpErrorResponse({
                status: HttpStatusCode.BadGateway,
                error: undefined
            }),
            new SyntaxError('Unsupported Action') as HttpErrorResponse
        ];
        const params: Array<[string, Error, ApiErrorMessage]> = [
            [
                'error is HttpErrorResponse and nested error is string',
                errors[0],
                { what: `${errors[0].error}`, why: `${errors[0].message}` }
            ],
            [
                'error is HttpErrorResponse and nested error is formatted ApiErrorMessage',
                errors[1],
                {
                    what: `${errors[1].error.what}`,
                    why: `${errors[1].error.why}`,
                    consequences: `${errors[1].error.consequences}`,
                    countermeasures: `${errors[1].error.countermeasures}`
                }
            ],
            [
                'error is HttpErrorResponse and nested error is null',
                errors[2],
                {
                    what: 'Please contact Superollider and report the issue',
                    why: 'Internal Server Error'
                }
            ],
            [
                'error is HttpErrorResponse and nested error is undefined',
                errors[3],
                {
                    what: 'Please contact Superollider and report the issue',
                    why: 'Unknown Error'
                }
            ],
            [
                'error is not HttpErrorResponse',
                errors[4],
                {
                    what: 'Please contact Superollider and report the issue',
                    why: 'Unknown Error'
                }
            ]
        ];

        for (const [description, error, assertion] of params) {
            it(`should verify will return ApiErrorMessage when ${description}`, () => {
                // When
                const apiMessage = getApiFormattedErrorMessage(error);

                // Then
                expect(apiMessage).toEqual(assertion);
            });
        }
    });
});

describe('getHumanReadableStatusText', () => {
    describe('parameterized_test', () => {
        const params: Array<[HttpStatusCode, string]> = [
            [HttpStatusCode.BadRequest, 'Invalid param'],
            [HttpStatusCode.Unauthorized, 'Unauthorized'],
            [HttpStatusCode.Forbidden, 'Forbidden'],
            [HttpStatusCode.NotFound, 'Not Found'],
            [HttpStatusCode.MethodNotAllowed, 'Not Allowed'],
            [HttpStatusCode.Conflict, 'Conflict'],
            [HttpStatusCode.UnprocessableEntity, 'Invalid operation'],
            [HttpStatusCode.InternalServerError, 'Internal Server Error'],
            [HttpStatusCode.ServiceUnavailable, 'Service Unavailable'],
            [HttpStatusCode.BadGateway, 'Unknown Error']
        ];

        for (const [statusCode, assertion] of params) {
            it(`should verify will return "${assertion}" for status code "${statusCode}"`, () => {
                // When
                const returnedText = getHumanReadableStatusText(statusCode);

                // Then
                expect(returnedText).toEqual(assertion);
            });
        }
    });
});
