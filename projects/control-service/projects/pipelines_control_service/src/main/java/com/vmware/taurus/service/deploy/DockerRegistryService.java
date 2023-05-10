/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.service.credentials.AWSCredentialsService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
@Slf4j
public class DockerRegistryService {

  @Value("${datajobs.proxy.repositoryUrl}")
  private String proxyRepositoryURL;

  @Value("${datajobs.builder.image}")
  private String builderImage;

  @Value("${datajobs.builder.registrySecret:}")
  private String registrySecret;

  @Value("${datajobs.docker.registryType:}")
  private String registryType;

  private EcrRegistryInterface ecrRegistryInterface;

  public DockerRegistryService(EcrRegistryInterface ecrRegistryInterface) {
    this.ecrRegistryInterface = ecrRegistryInterface;
  }

  public String dataJobImage(String dataJobName, String gitCommitSha) {
    return String.format("%s/%s:%s", proxyRepositoryURL, dataJobName, gitCommitSha);
  }

  public String registrySecret() {
    return registrySecret;
  }

  public String builderImage() {
    return builderImage;
  }

  // TODO: Implement
  public boolean dataJobImageExists(
      String imageName, AWSCredentialsService.AWSCredentialsDTO awsCredentialsDTO) {

    if (registryType.equalsIgnoreCase("ecr")) {
      return checkImageExistsInEcr(imageName, awsCredentialsDTO);
    }

    return false;
  }

  private boolean checkImageExistsInEcr(
      String imageName, AWSCredentialsService.AWSCredentialsDTO awsCredentialsDTO) {
    return ecrRegistryInterface.checkEcrImageExists(imageName, awsCredentialsDTO);
  }
}
