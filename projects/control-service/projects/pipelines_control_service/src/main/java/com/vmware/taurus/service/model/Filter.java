/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class Filter {
   private String property;
   private String pattern;
   private Direction sort;

   public static Filter of(String property, String pattern, Direction sort) {
      return new Filter(property, pattern, sort);
   }

   public enum Direction {
      ASC, DESC
   }
}
