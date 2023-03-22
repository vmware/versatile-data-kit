/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { CollectionsUtil, FilterMethods } from '../../utils';

import { ErrorCodes, ExcludedMethods } from '../../common';

import { generateSupportedHttpErrorCodes } from '../../common/error/utils';

/**
 * ** Generates error codes for provided method names.
 *
 *      - !!! Important: Only for Unit tests purposes, not for production.
 *
 *      - Optionally could be provided ClassName and PublicName, otherwise will be auto-generated random strings.
 */
/* eslint-disable @typescript-eslint/no-unsafe-argument,
                  @typescript-eslint/no-unsafe-member-access,
                  @typescript-eslint/no-unsafe-assignment,
                  @typescript-eslint/ban-ts-comment,
                  @typescript-eslint/dot-notation */
export const generateErrorCodes = <CType>(
    serviceStub: CType,
    methodNames: Array<keyof FilterMethods<CType, ExcludedMethods>>,
    className?: string,
    publicName?: string
): ErrorCodes<CType> => {
    const _className = className ?? CollectionsUtil.generateRandomString();
    const _publicName = publicName ?? CollectionsUtil.generateRandomString();
    const _errorCodes: ErrorCodes<CType> = {} as ErrorCodes<CType>;

    // @ts-ignore
    methodNames.forEach((method: string) => {
        _errorCodes[method] = generateSupportedHttpErrorCodes(_className, _publicName, method);
    });

    serviceStub['errorCodes'] = _errorCodes;

    return _errorCodes;
};
/* eslint-enable @typescript-eslint/no-unsafe-argument,
                 @typescript-eslint/no-unsafe-member-access,
                  @typescript-eslint/no-unsafe-assignment,
                 @typescript-eslint/ban-ts-comment,
                 @typescript-eslint/dot-notation */
