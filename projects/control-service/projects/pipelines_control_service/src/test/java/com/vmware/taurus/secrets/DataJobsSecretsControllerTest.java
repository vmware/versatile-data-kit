/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.secrets;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.vmware.taurus.exception.DataJobSecretsException;
import com.vmware.taurus.exception.SecretStorageNotConfiguredException;
import com.vmware.taurus.secrets.controller.DataJobsSecretsController;
import com.vmware.taurus.secrets.controller.NoOpDataJobsSecretsController;
import com.vmware.taurus.secrets.service.JobSecretsService;
import com.vmware.taurus.secrets.service.vault.VaultTeamCredentials;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class DataJobsSecretsControllerTest {

  @Mock private JobSecretsService jobSecretsService;

  @InjectMocks private DataJobsSecretsController controller;
  @InjectMocks private NoOpDataJobsSecretsController noOpsController;

  @Test
  void testDataJobSecretsUpdate() {
    String jobName = "testJob";
    String teamName = "testTeam";
    Map<String, Object> requestBody = new HashMap<>();

    ResponseEntity<Void> expectedResponse = ResponseEntity.noContent().build();

    doNothing().when(jobSecretsService).updateJobSecrets(teamName, jobName, requestBody);

    ResponseEntity<Void> actualResponse =
        controller.dataJobSecretsUpdate(teamName, jobName, null, requestBody);

    verify(jobSecretsService, times(1)).updateJobSecrets(teamName, jobName, requestBody);

    assertEquals(expectedResponse.getStatusCode(), actualResponse.getStatusCode());
  }

  @Test
  void testDataJobSecretsRead() throws JsonProcessingException {
    String jobName = "testJob";
    String teamName = "testTeam";
    Map<String, Object> expectedSecrets = new HashMap<>();

    when(jobSecretsService.readJobSecrets(teamName, jobName)).thenReturn(expectedSecrets);

    ResponseEntity<Map<String, Object>> expectedResponse = ResponseEntity.ok(expectedSecrets);

    ResponseEntity<Map<String, Object>> actualResponse =
        controller.dataJobSecretsRead(teamName, jobName, null);

    verify(jobSecretsService, times(1)).readJobSecrets(teamName, jobName);

    assertEquals(expectedResponse.getStatusCode(), actualResponse.getStatusCode());
    assertEquals(expectedResponse.getBody(), actualResponse.getBody());
  }

  @Test
  void testDataJobSecretsRead_JsonProcessingException() throws JsonProcessingException {
    String jobName = "testJob";
    String teamName = "testTeam";

    when(jobSecretsService.readJobSecrets(teamName, jobName)).thenThrow(JsonProcessingException.class);

    ResponseEntity<Map<String, Object>> expectedResponse =
        ResponseEntity.status(HttpStatus.BAD_REQUEST).body(null);

    DataJobSecretsException thrownException =
        assertThrows(
            DataJobSecretsException.class,
            () -> controller.dataJobSecretsRead(teamName, jobName, null));

    verify(jobSecretsService, times(1)).readJobSecrets(teamName, jobName);

    assertEquals(expectedResponse.getStatusCode(), thrownException.getHttpStatus());
  }

  @Test
  void testDataJobSecrets_NotConfigured() throws JsonProcessingException {
    String jobName = "testJob";
    String teamName = "testTeam";

    ResponseEntity<Map<String, Object>> expectedResponse =
        ResponseEntity.status(HttpStatus.NOT_IMPLEMENTED).body(null);

    SecretStorageNotConfiguredException thrownException =
        assertThrows(
            SecretStorageNotConfiguredException.class,
            () -> noOpsController.dataJobSecretsRead(teamName, jobName, null));

    assertEquals(expectedResponse.getStatusCode(), thrownException.getHttpStatus());

    thrownException =
        assertThrows(
            SecretStorageNotConfiguredException.class,
            () -> noOpsController.dataJobSecretsUpdate(teamName, jobName, null, null));

    assertEquals(expectedResponse.getStatusCode(), thrownException.getHttpStatus());
  }
}
