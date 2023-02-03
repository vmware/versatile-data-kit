/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class DockerRegistryService {

  // @Value("${datajobs.proxy.repositoryUrl}")
  private String proxyRepositoryURL = "registry.gitlab.com/dev.dp.taurus/data-jobs";

  // @Value("${datajobs.builder.image}")
  private String builderImage = "registry.hub.docker.com/versatiledatakit/job-builder:1.2.3";

  @Value("${datajobs.builder.registrySecret:}")
  private String registrySecret;

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
  public boolean dataJobImageExists(String imageName) {
    return false;
  }
}
