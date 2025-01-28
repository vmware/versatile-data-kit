/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/no-explicit-any */

/**
 * ** Interface for Equality of two Object.
 */
export interface Equals<T extends Record<any, any>> {
    /**
     * ** Make equality comparison between two objects of same type, current and provided.
     */
    equals(obj: T): boolean;
}
