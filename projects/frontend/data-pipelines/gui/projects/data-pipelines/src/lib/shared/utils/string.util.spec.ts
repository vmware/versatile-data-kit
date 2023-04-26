/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { StringUtil } from './string.util';

describe('StringUtil', () => {
    it('parsing string with single var', () => {
        expect(StringUtil.stringFormat('Hello {0}', 'World!')).toBe('Hello World!');
    });

    it('parsing string with multiple var', () => {
        expect(StringUtil.stringFormat('Hello {0} {1}', 'beautiful', 'World!')).toBe('Hello beautiful World!');
    });

    it('parsing string with multiple same var', () => {
        expect(StringUtil.stringFormat('Hello {0} {0}', 'beautiful', 'World!')).toBe('Hello beautiful beautiful');
    });

    it('parsing string with same var', () => {
        expect(StringUtil.stringFormat('Hello {0} {0}', 'beautiful')).toBe('Hello beautiful beautiful');
    });
});
