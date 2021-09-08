/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import lombok.AllArgsConstructor;
import lombok.Getter;

@AllArgsConstructor
public enum TerminationStatus {
    NONE(-1),
    SUCCESS(0),
    PLATFORM_ERROR(1),
    USER_ERROR(3),
    SKIPPED(4);

    @Getter
    private final int value;
}
