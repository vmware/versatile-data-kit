/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import java.time.OffsetDateTime;

public interface DataJobExecutionIdAndEndTime {
  String getId();

  OffsetDateTime getEndTime();
}
