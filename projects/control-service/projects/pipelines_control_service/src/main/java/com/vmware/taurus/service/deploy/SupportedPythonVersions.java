/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import java.security.InvalidParameterException;
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

  record DeploymentDetails(String baseImage, String vdkImage) {}

  @Value("#{${datajobs.deployment.supportedPythonVersions:{}}}")
  private Map<String, DeploymentDetails> supportedPythonVersions;

  @Value("${datajobs.deployment.defaultPythonVersion}")
  private String defaultPythonVersion;

  /**
   * Check if the pythonVersion passed by the user is supported by the Control Service.
   *
   * @param pythonVersion python version passed by the user.
   * @return true if the version is supported, and false otherwise.
   */
  public boolean isPythonVersionSupported(String pythonVersion) {
    return supportedPythonVersions.containsKey(pythonVersion);
  }

  /**
   * Returns a set of the python versions supported by the Control Service, in the format: [3.7,
   * 3.8, ...]. If the supportedPythonVersions configuration is not set, the method returns an empty
   * set.
   *
   * @return A set of all python versions supported by the Control Service.
   */
  public Set<String> getSupportedPythonVersions() {
    return supportedPythonVersions.keySet();
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
      return supportedPythonVersions.get(pythonVersion).baseImage;
    } else {
      log.warn(
          "An issue with the passed pythonVersion or supportedPythonVersions configuration has"
              + " occurred. Returning default job base image");
      return getDefaultJobBaseImage();
    }
  }

  public String getDefaultJobBaseImage() {
    return supportedPythonVersions.get(defaultPythonVersion).baseImage;
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
      return supportedPythonVersions.get(pythonVersion).vdkImage;
    } else {
      log.warn(
          "An issue with the passed pythonVersion or supportedPythonVersions configuration has"
              + " occurred. Returning default vdk image");
      return getDefaultVdkImage();
    }
  }

  public String getDefaultVdkImage() {
    return supportedPythonVersions.get(defaultPythonVersion).vdkImage;
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
}
