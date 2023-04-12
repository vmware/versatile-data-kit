/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';
import { ParseEpochPipe } from './parse-epoch.pipe';

describe('ParseEpochPipe', () => {
    let pipe: ParseEpochPipe;
    const TEST_EPOCH_SECONDS = 1522668899;
    const MILLIS_MULTIPLIER = 1000;

    beforeEach(() => {
        TestBed.configureTestingModule({ providers: [ParseEpochPipe] });
        pipe = TestBed.inject(ParseEpochPipe);
    });

    it('can instantiate', () => {
        expect(pipe).toBeTruthy();
    });

    it('transforms missing epoch to emtpy result', () => {
        expect(pipe.transform(-1)).toBeNull();
    });

    it('transforms valid epoch to valid result', () => {
        const result = pipe.transform(TEST_EPOCH_SECONDS);
        expect(result).toBeDefined();
        expect(result).toEqual(new Date(TEST_EPOCH_SECONDS * MILLIS_MULTIPLIER));
    });
});
