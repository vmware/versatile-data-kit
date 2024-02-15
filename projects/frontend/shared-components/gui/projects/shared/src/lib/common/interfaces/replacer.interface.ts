/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021-2024 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * ** Interface for generic replacer.
 */
export interface Replacer<T> {
    searchValue: T;
    replaceValue: T;
}
