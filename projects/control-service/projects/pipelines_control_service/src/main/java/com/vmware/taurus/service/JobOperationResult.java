/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.vmware.taurus.service.webhook.WebHookResult;
import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class JobOperationResult {
  private boolean completed;
  private WebHookResult webHookResult;
}
