/*
 * Copyright 2023-2026 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * ** Interface for generic replacer.
 */
export interface Replacer<T> {
  searchValue: T;
  replaceValue: T;
}
