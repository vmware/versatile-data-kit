

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { CallFake } from '../../../unit-testing';

import { Comparable, Predicate } from '../../interfaces';

import { CompoundPredicate } from './base-compound.predicate';

describe('CompoundPredicate', () => {
    describe('Statics::', () => {
        describe('|of|', () => {
            it('should verify will throw Error', () => {
                // Given
                const predicate1: Predicate = { comparable: {} as Comparable, evaluate: CallFake };
                const predicate2: Predicate = { comparable: {} as Comparable, evaluate: CallFake };

                // When/Then
                expect(() => CompoundPredicate.of(predicate1, predicate2))
                    .toThrowError('Method have to be overridden in Subclasses.');
            });
        });
    });
});
