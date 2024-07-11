/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.secrets.service.vault;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.vault.repository.mapping.Secret;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Secret
public class VaultTeamCredentials {

  @Id private String teamName;

  private String clientId;

  private String clientSecret;
}