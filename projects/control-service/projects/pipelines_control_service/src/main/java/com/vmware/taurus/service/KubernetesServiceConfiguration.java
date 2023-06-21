/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import io.kubernetes.client.openapi.ApiClient;
import io.kubernetes.client.openapi.apis.BatchV1Api;
import io.kubernetes.client.openapi.apis.BatchV1beta1Api;
import io.kubernetes.client.util.ClientBuilder;
import io.kubernetes.client.util.KubeConfig;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.jetbrains.annotations.NotNull;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.TimeUnit;

import static java.util.function.Predicate.not;

@Configuration
@Slf4j
public class KubernetesServiceConfiguration {

  private final UserAgentService userAgentService;

  @Autowired
  public KubernetesServiceConfiguration(UserAgentService userAgentService) {
    this.userAgentService = userAgentService;
  }

  @Bean
  public BatchV1Api deploymentBatchV1Api(
      @Qualifier("deploymentApiClient") ApiClient deploymentApiClient) {
    return new BatchV1Api(deploymentApiClient);
  }

  @Bean
  public BatchV1beta1Api deploymentBatchV1beta1Api(
      @Qualifier("deploymentApiClient") ApiClient deploymentApiClient) {
    return new BatchV1beta1Api(deploymentApiClient);
  }

  @Bean
  public ApiClient deploymentApiClient(
      @Value("${datajobs.deployment.k8s.kubeconfig:}") String kubeconfig) throws Exception {
    return getClient(kubeconfig);
  }

  @Bean
  public ApiClient controlApiClient(@Value("${datajobs.control.k8s.kubeconfig:}") String kubeconfig)
      throws Exception {
    return getClient(kubeconfig);
  }

  @Bean
  public BatchV1Api controlBatchV1Api(@Qualifier("controlApiClient") ApiClient apiClient) {
    return new BatchV1Api(apiClient);
  }

  @Bean
  public String controlNamespace(
      @Value("${datajobs.control.k8s.kubeconfig:}") String kubeconfig,
      @Value("${datajobs.control.k8s.namespace:}") String namespace)
      throws FileNotFoundException {
    return getNamespace(kubeconfig, namespace);
  }

  @Bean
  public String dataJobsNamespace(
      @Value("${datajobs.deployment.k8s.kubeconfig:}") String kubeconfig,
      @Value("${datajobs.deployment.k8s.namespace:}") String namespace)
      throws FileNotFoundException {
    return getNamespace(kubeconfig, namespace);
  }

  @NotNull
  private static String getNamespace(String kubeconfig, String namespace)
      throws FileNotFoundException {
    if (!StringUtils.isBlank(namespace)) {
      return namespace;
    } else if (!StringUtils.isBlank(kubeconfig) && new File(kubeconfig).isFile()) {
      KubeConfig kubeConfig = KubeConfig.loadKubeConfig(new FileReader(kubeconfig));
      return kubeConfig.getNamespace();
    } else {
      return getCurrentNamespace();
    }
  }

  private static String getCurrentNamespace() {
    return getNamespaceFileContents().stream()
        .filter(not(String::isBlank))
        .findFirst()
        .map(String::strip)
        .orElse(null);
  }

  private static List<String> getNamespaceFileContents() {
    try {
      String namespaceFile = "/var/run/secrets/kubernetes.io/serviceaccount/namespace";
      return Files.readAllLines(Paths.get(namespaceFile));
    } catch (IOException e) {
      return Collections.emptyList();
    }
  }

  @NotNull
  private ApiClient getClient(String kubeconfig) throws IOException {
    final ApiClient client;
    log.info("Configuration used: kubeconfig: {}", kubeconfig);
    if (!StringUtils.isBlank(kubeconfig) && new File(kubeconfig).isFile()) {
      log.info("Will use provided kubeconfig file from configuration: {}", kubeconfig);
      KubeConfig kubeConfig = KubeConfig.loadKubeConfig(new FileReader(kubeconfig));
      client = ClientBuilder.kubeconfig(kubeConfig).build();
    } else {
      log.info("Will use default client");
      client = ClientBuilder.defaultClient();
    }
    if (userAgentService != null) {
      client.setUserAgent(userAgentService.getUserAgent());
    }

    // Annoying error: Watch is incompatible with debugging mode active
    // client.setDebugging(true);
    client.setHttpClient(
        client.getHttpClient().newBuilder().readTimeout(0, TimeUnit.SECONDS).build());
    // client.getHttpClient().setReadTimeout(0, TimeUnit.SECONDS);
    return client;
  }
}
