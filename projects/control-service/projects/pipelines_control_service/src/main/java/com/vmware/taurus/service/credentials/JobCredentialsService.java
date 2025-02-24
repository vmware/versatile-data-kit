/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.credentials;

import com.vmware.taurus.exception.ExternalSystemError;
import com.vmware.taurus.exception.ExternalSystemError.MainExternalSystem;
import com.vmware.taurus.exception.KubernetesException;
import com.vmware.taurus.secrets.service.JobSecretsService;
import com.vmware.taurus.secrets.service.vault.VaultTeamCredentials;
import com.vmware.taurus.service.credentials.webhook.CreateOAuthAppBody;
import com.vmware.taurus.service.credentials.webhook.CreateOAuthAppWebHookProvider;
import com.vmware.taurus.service.credentials.webhook.CreateOAuthAppWebHookResult;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.webhook.WebHookResult;
import io.fabric8.kubernetes.client.utils.KubernetesResourceUtil;
import io.kubernetes.client.openapi.ApiException;
import java.io.Closeable;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.Validate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.lang.Nullable;
import org.springframework.stereotype.Service;

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
@Slf4j
public class JobCredentialsService {
  public static final String K8S_KEYTAB_KEY_IN_SECRET = "keytab";
  public static final String K8S_TEAM_CLIENT_ID = "VDK_TEAM_CLIENT_ID";
  public static final String K8S_TEAM_CLIENT_SECRET = "VDK_TEAM_CLIENT_SECRET";
  public static final String OAUTH_CREDENTIALS = "team-oauth-";

  // pattern for the name of the principal to be created - "%(data_job)" will be replaced with the
  // job name
  @Value("${credentials.principal.pattern:pa__view_%(data_job)}")
  private String credentialsPrincipalPattern = "pa__view_%(data_job)";

  private final DataJobsKubernetesService dataJobsKubernetesService;
  private final CredentialsRepository credentialsRepository;

  @Nullable private final JobSecretsService secretsService;

  private final CreateOAuthAppWebHookProvider createOAuthAppWebHookProvider;

  /**
   * Create a new job credentials and saves it as kubernetes secret possibly overwriting the older
   * credentials (if they existed)
   */
  public void createJobCredentials(String jobName, String teamName) {
    Validate.notBlank(jobName, "jobName must not be blank");

    String principal = getJobPrincipalName(jobName);
    File keytabFile;
    try {
      keytabFile = File.createTempFile(principal, ".keytab");
    } catch (IOException e) {
      throw new ExternalSystemError(MainExternalSystem.HOST_CONTAINER, e);
    }

    // Create a secret with the oAuth token for the team
    if (secretsService != null) {
      VaultTeamCredentials teamCredentials = secretsService.readTeamOauthCredentials(teamName);
      // if this is the first data job for the team or the credentials do not exist for some reason,
      // we should create them
      if (teamCredentials == null) {
        // call the webhook to create Oauth app permissions
        CreateOAuthAppBody request = new CreateOAuthAppBody();
        request.setOauthAppId(teamName);
        Optional<WebHookResult> resultHolder = createOAuthAppWebHookProvider.invokeWebHook(request);
        if (resultHolder.isPresent()
            && resultHolder.get().isSuccess()
            && resultHolder.get()
                instanceof CreateOAuthAppWebHookResult createOAuthAppWebHookResult) {
          // store the permissions in the secretService
          secretsService.updateTeamOauthCredentials(
              teamName,
              createOAuthAppWebHookResult.getClientId(),
              createOAuthAppWebHookResult.getClientSecret());
          teamCredentials = new VaultTeamCredentials();
          teamCredentials.setTeamName(teamName);
          teamCredentials.setClientId(createOAuthAppWebHookResult.getClientId());
          teamCredentials.setClientSecret(createOAuthAppWebHookResult.getClientSecret());
        } else {
          log.warn(
              "Unable to process the result from the CreateOAuth webhook and cannot create team"
                  + " credentials for team: "
                  + teamName);
        }
      }

      Map<String, byte[]> secretData = new HashMap<>();
      secretData.put(K8S_TEAM_CLIENT_ID, teamCredentials.getClientId().getBytes());
      secretData.put(K8S_TEAM_CLIENT_SECRET, teamCredentials.getClientSecret().getBytes());

      String secretName = getTeamOAuthSecretName(teamName);
      try {
        dataJobsKubernetesService.saveSecretData(secretName, secretData);
      } catch (ApiException e) {
        throw new KubernetesException("Cannot update team credentials for team:" + teamName, e);
      }
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

  public static String getTeamOAuthSecretName(String teamName) {
    return KubernetesResourceUtil.sanitizeName(OAUTH_CREDENTIALS + teamName);
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
