/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * ** System Event ID for navigation trigger.
 *
 *   - Send event [BLOCKING]
 *   - Every Handler should return Promise.
 *
 *   - Payload {url: string | string[], extras?: NavigationExtras}
 */
export const SE_NAVIGATE = 'SE_Navigate';

/**
 * ** System Event that could be consumed by Handlers.
 * <p>
 *   - Must return a Promise!
 *
 *   - Handlers will listen for all Events in the System.
 *   - They could be BLOCKING and NON-BLOCKING.
 *
 *   - Payload {any}
 */
export const SE_ALL_EVENTS = '*';
