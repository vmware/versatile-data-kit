/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.model;

import lombok.AccessLevel;
import lombok.Data;
import lombok.Setter;

@Data
public class V2DataJobSchedule {
  private String scheduleCron;

  @Setter(AccessLevel.NONE)
  private int nextRunEpochSeconds;

  public void setNextRunEpochSeconds(long nextRunEpochSeconds) {
    // TODO: rework this if needed, currently it will throw exception for a dates after year 2038
    // Currently the workaround for this is large, due to lack of native long attribute in
    // Read more https://en.wikipedia.org/wiki/Year_2038_problem
    this.nextRunEpochSeconds = Math.toIntExact(nextRunEpochSeconds);
  }
}
