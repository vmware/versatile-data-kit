/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import lombok.AllArgsConstructor;
import lombok.Getter;

@AllArgsConstructor
public enum ExecutionTerminationStatus {
    NONE("None", -1),
    SUCCESS("Success", 0),
    PLATFORM_ERROR("Platform error", 1),
    USER_ERROR("User error", 3),
    SKIPPED("Skipped", 4);

    @Getter
    private final String string;

    @Getter
    private final Integer integer;
}
