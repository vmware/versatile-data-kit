/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import java.util.*;

import org.springframework.beans.factory.annotation.Value;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import lombok.extern.slf4j.Slf4j;

/**
 * Handles operations related to supported python versions for data job deployments. The class
 * contains utility methods which provide functionality to read the configuration related to the
 * python versions supported by the Control Service. These utility methods are meant to be used in
 * other components, as needed.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class SupportedPythonVersions {

  protected static String BASE_IMAGE = "baseImage";

  protected static String VDK_IMAGE = "vdkImage";

  protected static String BUILDER_IMAGE = "builderImage";

  @Value("#{${datajobs.deployment.supportedPythonVersions:{}}}")
  private Map<String, Map<String, String>> supportedPythonVersions;

  @Value("${datajobs.deployment.defaultPythonVersion}")
  private String defaultPythonVersion;

  private final DockerRegistryService dockerRegistryService;

  /**
   * Check if the pythonVersion passed by the user is supported by the Control Service.
   *
   * @param pythonVersion python version passed by the user.
   * @return true if the version is supported, and false otherwise.
   */
  public boolean isPythonVersionSupported(String pythonVersion) {
    return supportedPythonVersions != null
        && !supportedPythonVersions.isEmpty()
        && supportedPythonVersions.containsKey(pythonVersion);
  }

  /**
   * Returns a set of the python versions supported by the Control Service, in the format: [3.7,
   * 3.8, ...]. If the supportedPythonVersions configuration is not set, the method returns an empty
   * set.
   *
   * @return A set of all python versions supported by the Control Service.
   */
  public Set<String> getSupportedPythonVersions() {
    return Optional.ofNullable(supportedPythonVersions)
        .map(Map::keySet)
        .orElse(Collections.emptySet());
  }

  /**
   * Returns the name of the data job base image as stored in the docker registry. If
   * supportedPythonVersions is set, and the pythonVersion passed by the user is supported according
   * to the configuration, the base image corresponding to the pythonVersion is returned. Otherwise,
   * the default base image is returned.
   *
   * @param pythonVersion a string indicating the python version passed by the user
   * @return a string of the data job base image.
   */
  public String getJobBaseImage(String pythonVersion) {
    if (isPythonVersionSupported(pythonVersion)) {
      return supportedPythonVersions.get(pythonVersion).get(BASE_IMAGE);
    } else {
      log.warn(
          "An issue with the passed pythonVersion or supportedPythonVersions configuration has"
              + " occurred. Returning default job base image");
      return getDefaultJobBaseImage();
    }
  }

  public String getDefaultJobBaseImage() {
    return supportedPythonVersions.get(defaultPythonVersion).get(BASE_IMAGE);
  }

  /**
   * Returns the name of the vdk image as stored in the docker registry. If supportedPythonVersions
   * is set, and the pythonVersion, passed by the user, is supported according to the configuration,
   * the vdk image corresponding to the pythonVersion is returned. Otherwise, the default vdk image
   * is returned.
   *
   * @param pythonVersion a string indicating the python version passed by the user
   * @return a string of the vdk image.
   */
  public String getVdkImage(String pythonVersion) {
    if (isPythonVersionSupported(pythonVersion)) {
      return supportedPythonVersions.get(pythonVersion).get(VDK_IMAGE);
    } else {
      log.warn(
          "An issue with the passed pythonVersion or supportedPythonVersions configuration has"
              + " occurred. Returning default vdk image");
      return getDefaultVdkImage();
    }
  }

  public String getBuilderImage(String pythonVersion) {
    if (isPythonVersionSupported(pythonVersion)) {
      return getBuilderImage(supportedPythonVersions.get(pythonVersion));
    } else {
      log.warn(
          "An issue with the passed pythonVersion or supportedPythonVersions configuration has"
              + " occurred. Returning default builder image");
      return getBuilderImage(supportedPythonVersions.get(defaultPythonVersion));
    }
  }

  public String getDefaultVdkImage() {
    return supportedPythonVersions.get(defaultPythonVersion).get(VDK_IMAGE);
  }

  /**
   * Returns the default python version supported by the Control Service. The version number is read
   * from the datajobs.deployment.defaultPythonVersion application property.
   *
   * @return a string indicating the default python version supported by the Control Service.
   */
  public String getDefaultPythonVersion() {
    return defaultPythonVersion;
  }

  private String getBuilderImage(Map<String, String> supportedPythonVersion) {
    return supportedPythonVersion.getOrDefault(BUILDER_IMAGE, dockerRegistryService.builderImage());
  }
}
