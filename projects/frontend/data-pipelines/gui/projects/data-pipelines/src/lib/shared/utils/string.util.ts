/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

export class StringUtil {
    static stringFormat = (str: string, ...args: string[]) => str.replace(/{(\d+)}/g, (match, index: number) => args[index] || '');
}
