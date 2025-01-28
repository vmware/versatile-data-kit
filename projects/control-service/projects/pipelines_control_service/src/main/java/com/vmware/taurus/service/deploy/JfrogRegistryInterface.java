/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

import org.jfrog.artifactory.client.Artifactory;
import org.jfrog.artifactory.client.ArtifactoryClientBuilder;
import org.jfrog.artifactory.client.model.AqlItem;
import org.jfrog.filespecs.FileSpec;

import java.util.List;

/**
 * This class is used to provide interface methods between a Jfrog Artifactory Container Registry
 * and the VDK control service.
 */
@Service
@Slf4j
@ConditionalOnProperty(name = "datajobs.docker.registryType", havingValue = "jfrog")
public class JfrogRegistryInterface {

  //    String artifactoryUrl = "https://build-artifactory.eng.vmware.com/artifactory";
  @Value("${datajobs.jfrog.artifactory.url}")
  private String artifactoryUrl;

  @Value("${datajobs.jfrog.artifactory.username}")
  private String artifactoryUsername;

  @Value("${datajobs.jfrog.artifactory.password}")
  private String artifactoryPassword;

  @Value("${datajobs.jfrog.artifactory.repo}")
  private String artifactoryDockerRepoName;

  public boolean checkJfrogImageExists(String imageName) {
    boolean imageExists = false;

    ArtifactoryClientBuilder artifactoryClientBuilder =
        ArtifactoryClientBuilder.create()
            .setUrl(artifactoryUrl)
            .setUsername(artifactoryUsername)
            .setPassword(artifactoryPassword);

    // Create Artifactory client
    List<AqlItem> repoPaths;
    try (Artifactory artifactory = artifactoryClientBuilder.build()) {

      // Docker image path
      String fileSpecJson =
          String.format(
              "{\"files\": [{\"pattern\": \"%s/%s/manifest.json\"}]}",
              artifactoryDockerRepoName, imageName);
      FileSpec fileSpec = FileSpec.fromString(fileSpecJson);
      repoPaths =
          artifactory
              .searches()
              .repositories(artifactoryDockerRepoName)
              .artifactsByFileSpec(fileSpec);
      if (!repoPaths.isEmpty()) {
        imageExists = true;
      }
    } catch (Exception e) {
      log.error(
          "Failed to check if image exists and will assume it doesn't exist. Exception: " + e, e);
    }
    return imageExists;
  }
}
