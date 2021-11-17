/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.model;

import java.util.Set;

import lombok.Builder;
import lombok.Data;
import org.springframework.data.domain.Sort;

import com.vmware.taurus.service.model.DataJobExecution_;

@Data
@Builder
public class DataJobExecutionOrder {

   public static final Set<String> AVAILABLE_PROPERTIES = Set.of(
         DataJobExecution_.MESSAGE,
         DataJobExecution_.TYPE,
         DataJobExecution_.JOB_SCHEDULE,
         DataJobExecution_.START_TIME,
         DataJobExecution_.END_TIME,
         DataJobExecution_.JOB_VERSION,
         DataJobExecution_.ID,
         DataJobExecution_.OP_ID,
         DataJobExecution_.LAST_DEPLOYED_DATE,
         DataJobExecution_.LAST_DEPLOYED_BY,
         DataJobExecution_.STARTED_BY,
         DataJobExecution_.STATUS,
         DataJobExecution_.VDK_VERSION);

   public static final String PROPERTY_FIELD = "property";
   public static final String DIRECTION_FIELD = "direction";

   private String property;
   private Sort.Direction direction;

   public DataJobExecutionOrder(String property, Sort.Direction direction) {
      this.property = property;
      this.direction = direction;
   }
}
