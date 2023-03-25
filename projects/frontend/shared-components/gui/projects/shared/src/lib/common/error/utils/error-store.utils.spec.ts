/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { CollectionsUtil } from '../../../utils';

import { generateErrorCode } from './error-store.utils';

describe('generateErrorCode', () => {
    it('should verify will return correct value', () => {
        // Given
        const className = 'ClassName';
        const publicName = 'PublicName';
        const methodName = 'methodName';
        const additionalDetails = '500';

        // When
        const errorCode = generateErrorCode(className, publicName, methodName, additionalDetails);

        // Then
        expect(errorCode).toEqual(`${className}_${publicName}_${methodName}_${additionalDetails}`);
    });

    it('should verify will generate random string if className is not provided', () => {
        // Given
        const className: string = null;
        const publicName = 'PublicName1';
        const methodName = 'methodName1';
        const additionalDetails = '503';
        const spy = spyOn(CollectionsUtil, 'generateRandomString').and.returnValue('ClassName1');

        // When
        const errorCode = generateErrorCode(className, publicName, methodName, additionalDetails);

        // Then
        expect(errorCode).toEqual(`ClassName1_${publicName}_${methodName}_${additionalDetails}`);
        expect(spy).toHaveBeenCalled();
    });
});
