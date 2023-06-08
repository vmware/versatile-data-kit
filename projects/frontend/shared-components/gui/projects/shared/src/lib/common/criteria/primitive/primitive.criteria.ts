/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { get } from 'lodash';

import { Criteria } from '../../interfaces';

/**
 * ** Primitive Criteria that check equals by reference or if primitive by value, using ===
 */
export class PrimitiveCriteria<T extends object> implements Criteria<T> {
    private _property: keyof T;
    private _assertionValue: T[keyof T];

    /**
     * ** Constructor.
     */
    constructor(property: keyof T, assertionValue: T[keyof T]) {
        this._property = property;
        this._assertionValue = assertionValue;
    }

    /**
     * @inheritDoc
     */
    meetCriteria(elements: T[]): T[] {
        return [...(elements ?? [])].filter((element) => {
            const value = get<T, keyof T>(element, this._property);

            return value === this._assertionValue;
        });
    }
}
