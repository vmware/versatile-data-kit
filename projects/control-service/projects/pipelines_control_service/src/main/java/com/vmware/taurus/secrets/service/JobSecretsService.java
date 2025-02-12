/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.secrets.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.vmware.taurus.secrets.service.vault.VaultTeamCredentials;

import java.util.Map;

/** Interface for managing job secrets and team OAuth credentials. */
public interface JobSecretsService {

  /**
   * Updates the secrets for a specified job.
   *
   * @param teamName the name of the team
   * @param jobName the name of the job
   * @param secrets a map containing the secrets to be updated
   */
  void updateJobSecrets(String teamName, String jobName, Map<String, Object> secrets);

  /**
   * Reads the secrets for a specified job.
   *
   * @param teamName the name of the team
   * @param jobName the name of the job
   * @return a map containing the secrets of the specified job
   * @throws JsonProcessingException if there is an error processing the JSON
   */
  Map<String, Object> readJobSecrets(String teamName, String jobName)
      throws JsonProcessingException;

  /**
   * Updates the OAuth credentials for a specified team.
   *
   * @param teamName the name of the team
   * @param clientId the OAuth client ID
   * @param clientSecret the OAuth client secret
   */
  void updateTeamOauthCredentials(String teamName, String clientId, String clientSecret);

  /**
   * Reads the OAuth credentials for a specified team.
   *
   * @param teamName the name of the team
   * @return the OAuth credentials of the specified team
   */
  VaultTeamCredentials readTeamOauthCredentials(String teamName);

  /**
   * Returns the name of the team associated with the given OAuth Client Id or null if not found.
   *
   * @param clientId the Client Id to be looked up
   * @return the Team name which corresponds to the Client Id or null
   */
  String getTeamIdForClientId(String clientId);
}
