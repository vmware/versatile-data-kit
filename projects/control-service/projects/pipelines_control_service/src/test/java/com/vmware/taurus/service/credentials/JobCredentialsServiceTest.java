/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.credentials;

import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import io.kubernetes.client.openapi.ApiException;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.io.File;
import java.nio.file.Files;
import java.util.Map;
import java.util.Optional;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class JobCredentialsServiceTest {

  @Mock private KerberosCredentialsRepository credentialsRepository;

  @Mock private DataJobsKubernetesService kubernetesService;

  @InjectMocks private JobCredentialsService credentialsService;

  @BeforeEach
  public void setup() throws Exception {}

  @Test
  public void test_createJobCredentials() throws ApiException {
    doAnswer(
            a -> {
              Optional<File> f = (Optional<File>) a.getArgument(1);
              Files.writeString(f.get().toPath(), "keytab-data");
              return null;
            })
        .when(credentialsRepository)
        .createPrincipal(anyString(), any());

    credentialsService.createJobCredentials("test");

    String secretName = JobCredentialsService.getJobKeytabKubernetesSecretName("test");
    ArgumentCaptor<Map<String, byte[]>> argCaptor = ArgumentCaptor.forClass(Map.class);

    verify(kubernetesService, only()).saveSecretData(eq(secretName), argCaptor.capture());
    Assertions.assertTrue(argCaptor.getValue().containsKey("keytab"));
    Assertions.assertArrayEquals("keytab-data".getBytes(), argCaptor.getValue().get("keytab"));
  }

  @Test
  public void test_deleteJobCredentials() throws ApiException {
    credentialsService.deleteJobCredentials("job");
    verify(kubernetesService).removeSecretData(contains("job"));
    verify(credentialsRepository).deletePrincipal(contains("job"));
  }
}
