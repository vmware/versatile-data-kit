/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021-2024 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.model;

import lombok.Value;

import java.util.Comparator;
import java.util.function.Predicate;

@Value
public class Criteria<T> {
  Predicate<T> predicate;
  Comparator<T> comparator;
}
