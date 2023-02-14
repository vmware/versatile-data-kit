/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.model;

import com.vmware.taurus.service.model.DataJobExecution_;
import com.vmware.taurus.service.model.DataJob_;
import com.vmware.taurus.service.model.JobConfig_;
import lombok.Builder;
import lombok.Data;
import org.springframework.data.domain.Sort;

import java.util.Map;
import java.util.Set;

@Data
@Builder
public class DataJobExecutionOrder {

  public static final String DATA_JOB_NAME = "jobName";
  public static final String DATA_JOB_TEAM = "jobTeam";

  public static final Set<String> AVAILABLE_PROPERTIES =
      Set.of(
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
          DataJobExecution_.VDK_VERSION,
          DATA_JOB_NAME,
          DATA_JOB_TEAM);

  public static final Map<String, String> PUBLIC_NAME_TO_DB_ENTITY_MAP =
      Map.of(
          DATA_JOB_NAME, DataJobExecution_.DATA_JOB + "." + DataJob_.NAME,
          DATA_JOB_TEAM,
              DataJobExecution_.DATA_JOB + "." + DataJob_.JOB_CONFIG + "." + JobConfig_.TEAM);

  public static final String PROPERTY_FIELD = "property";
  public static final String DIRECTION_FIELD = "direction";

  private String property;
  private Sort.Direction direction;

  public DataJobExecutionOrder(String property, Sort.Direction direction) {
    this.property = property;
    this.direction = direction;
  }
}
