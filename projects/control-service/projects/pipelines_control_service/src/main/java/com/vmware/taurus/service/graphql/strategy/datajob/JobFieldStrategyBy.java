/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.strategy.datajob;

import com.vmware.taurus.service.graphql.strategy.JobFieldStrategyFactory;

import java.util.Arrays;

/**
 * Enum to distinguish between different strategies (fields and paths)
 * Using doubled string instead of prefilled & preformatted hashmap to map the incoming (field) vs outgoing (path) names
 * In future the order could be meaningful (due to dependencies across strategy fields),
 * but it could be controlled with the {@link JobFieldStrategyFactory}
 */
public enum JobFieldStrategyBy {
   JOB_NAME("jobName", "content/jobName"),
   DEPLOYMENT("deployments", "content/deployments"),
   DEPLOYMENT_ENABLED("deployments.enabled", "content/deployments/enabled"),
   TEAM("config.team", "content/config/team"),
   DESCRIPTION("config.description", "content/config/description"),
   SOURCE_URL("config.sourceUrl", "content/config/sourceUrl"),
   NEXT_RUN_EPOCH_SECS("config.schedule.nextRunEpochSeconds", "content/config/schedule/nextRunEpochSeconds"),
   SCHEDULE_CRON("config.schedule.scheduleCron", "content/config/schedule/scheduleCron");

   private final String field;
   private final String path;

   JobFieldStrategyBy(String field, String path) {
      this.field = field;
      this.path = path;
   }

   public String getField() {
      return field;
   }

   public String getPath() {
      return path;
   }

   public static JobFieldStrategyBy field(String field) {
      return Arrays.stream(JobFieldStrategyBy.values())
            .filter(strategy -> strategy.getField().equalsIgnoreCase(field))
            .findAny()
            .orElse(null);
   }

   public static JobFieldStrategyBy path(String path) {
      return Arrays.stream(JobFieldStrategyBy.values())
            .filter(strategy -> strategy.getPath().equalsIgnoreCase(path))
            .findAny()
            .orElse(null);
   }
}
