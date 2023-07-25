/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

globalThis.fetch = require('jest-fetch-mock');
// Use node crypto for crypto
globalThis.crypto = require('crypto');
