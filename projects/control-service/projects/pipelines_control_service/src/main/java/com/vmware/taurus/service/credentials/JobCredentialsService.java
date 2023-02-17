/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.credentials;

import com.vmware.taurus.exception.ExternalSystemError;
import com.vmware.taurus.exception.ExternalSystemError.MainExternalSystem;
import com.vmware.taurus.exception.KubernetesException;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import io.kubernetes.client.openapi.ApiException;
import lombok.RequiredArgsConstructor;
import org.apache.commons.lang3.Validate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.Closeable;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.Collections;
import java.util.Optional;

/**
 * Manages credentials of a job.
 *
 * <p>Credentials (kerberos principal and keytab) are generated and then are stored as kubernetes
 * secret.
 *
 * <p>Methods throw {@link ExternalSystemError} in case of unexpected, and likely intermittent,
 * errors from Kubernetes.
 */
@Service
@RequiredArgsConstructor
public class JobCredentialsService {
  public static final String K8S_KEYTAB_KEY_IN_SECRET = "keytab";

  // pattern for the name of the principal to be created - "%(data_job)" will be replaced with the
  // job name
  @Value("${credentials.principal.pattern:pa__view_%(data_job)}")
  private String credentialsPrincipalPattern = "pa__view_%(data_job)";

  private final DataJobsKubernetesService dataJobsKubernetesService;
  private final CredentialsRepository credentialsRepository;

  /**
   * Create a new job credentials and saves it as kubernetes secret possibly overwriting the older
   * credentials (if they existed)
   */
  public void createJobCredentials(String jobName) {
    Validate.notBlank(jobName, "jobName must not be blank");

    String principal = getJobPrincipalName(jobName);
    File keytabFile;
    try {
      keytabFile = File.createTempFile(principal, ".keytab");
    } catch (IOException e) {
      throw new ExternalSystemError(MainExternalSystem.HOST_CONTAINER, e);
    }
    try (Closeable ignored = keytabFile::delete) {
      credentialsRepository.createPrincipal(principal, Optional.of(keytabFile));

      String secretName = getJobKeytabKubernetesSecretName(jobName);
      var keytabData =
          Collections.singletonMap(
              K8S_KEYTAB_KEY_IN_SECRET, Files.readAllBytes(keytabFile.toPath()));
      dataJobsKubernetesService.saveSecretData(secretName, keytabData);
    } catch (ApiException e) {
      throw new KubernetesException("Cannot update job credentials", e);
    } catch (IOException e) {
      throw new ExternalSystemError(MainExternalSystem.HOST_CONTAINER, e);
    }
  }

  /** Delete job's credentials. */
  public void deleteJobCredentials(String jobName) {
    Validate.notBlank(jobName, "jobName must not be blank");

    String secretName = getJobKeytabKubernetesSecretName(jobName);
    try {
      dataJobsKubernetesService.removeSecretData(secretName);
    } catch (ApiException e) {
      throw new KubernetesException("Cannot delete job credentials", e);
    }
    String principal = getJobPrincipalName(jobName);
    credentialsRepository.deletePrincipal(principal);
  }

  public byte[] readJobCredential(String jobName) {
    String secretName = getJobKeytabKubernetesSecretName(jobName);
    try {
      return dataJobsKubernetesService
          .getSecretData(secretName)
          .getOrDefault(K8S_KEYTAB_KEY_IN_SECRET, null);
    } catch (ApiException e) {
      throw new KubernetesException("Cannot read job credentials", e);
    }
  }

  public String getJobPrincipalName(String jobName) {
    return credentialsPrincipalPattern.replace("%(data_job)", jobName);
  }

  public static String getJobKeytabKubernetesSecretName(String jobName) {
    return "data-job-keytab-" + jobName;
  }
}
