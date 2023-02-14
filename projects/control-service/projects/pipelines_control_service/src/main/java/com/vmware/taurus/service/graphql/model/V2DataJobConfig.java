/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.model;

import com.vmware.taurus.controlplane.model.data.DataJobContacts;
import lombok.Data;

@Data
public class V2DataJobConfig {
  private String dbDefaultType;
  private String team;
  private String description;
  private V2DataJobSchedule schedule;
  private DataJobContacts contacts;
  private Boolean generateKeytab = true;
  private String sourceUrl;
}
