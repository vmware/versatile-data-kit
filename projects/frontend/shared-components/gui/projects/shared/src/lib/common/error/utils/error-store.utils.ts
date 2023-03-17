/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpStatusCode } from '@angular/common/http';

import { CollectionsUtil } from '../../../utils';

import { ServiceHttpErrorCodes } from '../ui-error/model/interfaces';

/**
 * ** Generates Error code (token).
 *
 *      - Code (token) starts with
 *      - Class name,
 *      - then followed by underscore and class PUBLIC_NAME,
 *      - then followed by underscore and method name or underscore with some error specifics,
 *      - then followed by underscore and additional details to avoid overlaps with other Class errors.
 *        <b>(for http requests it should be HTTP Status Code)</b>
 *
 * <br/>
 * <i>returned value pattern</i>:
 * <p>
 *     <Class Name><b>_</b><Class PUBLIC_NAME><b>_</b><Class method name><b>_</b><additional details, like HTTP Status Code>
 * </p>
 */
export const generateErrorCode = (className: string, classPublicName: string, methodName: string, additionalDetails: string): string => {
    let errorCode = '';

    if (CollectionsUtil.isString(className)) {
        errorCode += `${className}`;
    } else {
        errorCode += CollectionsUtil.generateRandomString();
    }

    if (CollectionsUtil.isString(classPublicName)) {
        errorCode += `_${classPublicName}`;
    }

    if (CollectionsUtil.isString(methodName)) {
        errorCode += `_${methodName}`;
    }

    if (CollectionsUtil.isString(additionalDetails)) {
        errorCode += `_${additionalDetails}`;
    } else {
        errorCode += '_';
    }

    return errorCode;
};

/**
 * ** Generates supported error codes for provided className, publicName and methodName.
 */
/* eslint-disable @typescript-eslint/no-unsafe-argument,
                  @typescript-eslint/no-unsafe-member-access,
                  @typescript-eslint/no-explicit-any */
export const generateSupportedHttpErrorCodes = (className: string, publicName: string, method: string): ServiceHttpErrorCodes => {
    const errorCodes: ServiceHttpErrorCodes = {} as ServiceHttpErrorCodes;

    errorCodes.All = generateErrorCode(className, publicName, method, null);
    errorCodes.ClientErrors = generateErrorCode(className, publicName, method, '4\\d\\d');
    errorCodes.BadRequest = generateErrorCode(className, publicName, method, `${HttpStatusCode.BadRequest}`);
    errorCodes.Unauthorized = generateErrorCode(className, publicName, method, `${HttpStatusCode.Unauthorized}`);
    errorCodes.Forbidden = generateErrorCode(className, publicName, method, `${HttpStatusCode.Forbidden}`);
    errorCodes.NotFound = generateErrorCode(className, publicName, method, `${HttpStatusCode.NotFound}`);
    errorCodes.MethodNotAllowed = generateErrorCode(className, publicName, method, `${HttpStatusCode.MethodNotAllowed}`);
    errorCodes.Conflict = generateErrorCode(className, publicName, method, `${HttpStatusCode.Conflict}`);
    errorCodes.UnprocessableEntity = generateErrorCode(className, publicName, method, `${HttpStatusCode.UnprocessableEntity}`);
    errorCodes.ServerErrors = generateErrorCode(className, publicName, method, '5\\d\\d');
    errorCodes.InternalServerError = generateErrorCode(className, publicName, method, `${HttpStatusCode.InternalServerError}`);
    errorCodes.ServiceUnavailable = generateErrorCode(className, publicName, method, `${HttpStatusCode.ServiceUnavailable}`);
    errorCodes.Unknown = generateErrorCode(className, publicName, method, 'unknown');

    return errorCodes;
};
/* eslint-enable @typescript-eslint/no-unsafe-argument,
                  @typescript-eslint/no-unsafe-member-access,
                  @typescript-eslint/no-explicit-any */
