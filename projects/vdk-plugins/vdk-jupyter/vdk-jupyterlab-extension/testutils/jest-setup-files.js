/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

globalThis.fetch = require('jest-fetch-mock');
// Use node crypto for crypto
globalThis.crypto = require('crypto');
