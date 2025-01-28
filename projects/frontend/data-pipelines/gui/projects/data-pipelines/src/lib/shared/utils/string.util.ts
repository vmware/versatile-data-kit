/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

export class StringUtil {
    static stringFormat = (str: string, ...args: string[]) => str.replace(/{(\d+)}/g, (match, index: number) => args[index] || '');
}
