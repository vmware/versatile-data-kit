/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.secrets.service;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.vault.repository.mapping.Secret;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Secret
public class JobSecrets {

  @Id private String jobName;

  private String secretsJson;
}
