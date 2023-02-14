/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import org.springframework.data.domain.Sort;

@Data
@AllArgsConstructor
public class Filter {
  private String property;
  private String pattern;
  private Sort.Direction sort;

  public static Filter of(String property, String pattern, Sort.Direction sort) {
    return new Filter(property, pattern, sort);
  }
}
