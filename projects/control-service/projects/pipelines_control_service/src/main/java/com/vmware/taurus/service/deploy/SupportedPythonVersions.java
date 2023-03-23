/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

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

  @Value("#{${datajobs.deployment.supportedPythonVersions}}")
  private Map<String, Map<String, String>> supportedPythonVersions;

  @Value("${datajobs.vdk.image}")
  private String vdkImage;

  @Value("${datajobs.deployment.dataJobBaseImage:python:3.9-slim}")
  private String deploymentDataJobBaseImage;

  private static final String VDK_IMAGE = "vdkImage";

  private static final String BASE_IMAGE = "baseImage";

  /**
   * Check if the python_version passed by the user is supported by the Control Service.
   *
   * @param pythonVersion python version passed by the user.
   * @return true if the version is supported, and false otherwise.
   */
  public boolean isPythonVersionSupported(String pythonVersion) {
    if (!supportedPythonVersions.isEmpty()) {
      return supportedPythonVersions.containsKey(pythonVersion);
    } else {
      return false;
    }
  }

  /**
   * Returns a string of the python versions supported by the Control Service, in the format: [3.7,
   * 3.8, ...]. If the supportedPythonVersions configuration is not set, the method returns the
   * default python version set in the deploymentDataJobBaseImage configuration property.
   *
   * @return A string of all python versions supported by the Control Service
   */
  public List<String> getSupportedPythonVersions() {
    if (!supportedPythonVersions.isEmpty()) {
      return supportedPythonVersions.keySet().stream()
          .map((obj) -> Objects.toString(obj, null))
          .collect(Collectors.toList());
    } else {
      try {
        return Arrays.asList(getDefaultPythonVersion());
      } catch (IllegalArgumentException e) {
        throw new IllegalArgumentException(e);
      }
    }
  }

  /**
   * Returns the name of the data job base image as stored in the docker registry. If
   * supportedPythonVersions is set, and the python_version passed by the user is supported
   * according to the configuration, the base image corresponding to the python_version is returned.
   * Otherwise, the default base image name as set in deploymentDataJobBaseImage is returned.
   *
   * @param pythonVersion a string indicating the python version passed by the user
   * @return a string of the data job base image.
   */
  public String getJobBaseImage(String pythonVersion) {
    if (!supportedPythonVersions.isEmpty() && isPythonVersionSupported(pythonVersion)) {
      return supportedPythonVersions.get(pythonVersion).get(BASE_IMAGE);
    } else {
      return deploymentDataJobBaseImage;
    }
  }

  public String getDefaultJobBaseImage() {
    return deploymentDataJobBaseImage;
  }

  /**
   * Returns the name of the vdk image as stored in the docker registry. If supportedPythonVersions
   * is set, and the python_version, passed by the user, is supported according to the
   * configuration, the vdk image corresponding to the python_version is returned. Otherwise, the
   * default vdk image name as set in vdkImage is returned.
   *
   * @param pythonVersion a string indicating the python version passed by the user
   * @return a string of the data job base image.
   */
  public String getVdkImage(String pythonVersion) {
    if (!supportedPythonVersions.isEmpty() && isPythonVersionSupported(pythonVersion)) {
      return supportedPythonVersions.get(pythonVersion).get(VDK_IMAGE);
    } else {
      return vdkImage;
    }
  }

  public String getDefaultVdkImage() {
    return vdkImage;
  }

  /**
   * Returns the default python version supported by the Control Service. The version number is
   * extracted from the datajobs.deployment.dataJobBaseImage application property. The property is
   * set as for example, `python:3.9-slim`, and we use a regex to match `3.9` and return it to the
   * caller.
   *
   * @return a string indicating the default python version supported by the Control Service.
   * @throws IllegalArgumentException
   */
  public String getDefaultPythonVersion() throws IllegalArgumentException {
    Pattern pattern = Pattern.compile("(\\d+\\.\\d+)");
    Matcher matcher = pattern.matcher(deploymentDataJobBaseImage);
    if (matcher.find()) {
      return matcher.group(1);
    } else {
      throw new IllegalArgumentException(
          "Could not extract python version number from datajobs.deployment.dataJobBaseImage.");
    }
  }
}
