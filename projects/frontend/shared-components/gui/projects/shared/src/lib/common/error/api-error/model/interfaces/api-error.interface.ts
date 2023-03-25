/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * ** Api error format.
 */
export interface ApiError {
    status: number;
    error: ApiErrorMessage | string;
    message: string;
    opId: string;
    path?: string;
}

/**
 * ** Api error message format.
 */
export interface ApiErrorMessage {
    what: string;
    why: string;
    consequences?: string;
    countermeasures?: string;
}
