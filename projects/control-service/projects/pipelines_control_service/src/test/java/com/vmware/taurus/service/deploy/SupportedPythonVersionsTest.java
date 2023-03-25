/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;
import com.vmware.taurus.service.deploy.SupportedPythonVersions.DeploymentDetails;

import java.util.Map;
import java.util.Set;

@ExtendWith(MockitoExtension.class)
public class SupportedPythonVersionsTest {
  private static final String SUPPORTED_PYTHON_VERSIONS = "supportedPythonVersions";
  private static final String DEFAULT_PYTHON_VERSION = "defaultPythonVersion";

  @InjectMocks private SupportedPythonVersions supportedPythonVersions;

  @Test
  public void isPythonVersionSupported_noSupportedVersions() {
    ReflectionTestUtils.setField(
        supportedPythonVersions, SUPPORTED_PYTHON_VERSIONS, Map.of());

    Assertions.assertFalse(supportedPythonVersions.isPythonVersionSupported("3.7"));
  }

  @Test
  public void isPythonVersionSupported_versionSupported() {
    Map<String, DeploymentDetails> supportedVersions = Map.of("3.7", new DeploymentDetails("python:3.7-slim", "test_vdk_image"));

    ReflectionTestUtils.setField(
        supportedPythonVersions, SUPPORTED_PYTHON_VERSIONS, supportedVersions);

    Assertions.assertTrue(supportedPythonVersions.isPythonVersionSupported("3.7"));
  }

  @Test
  public void isPythonVersionSupported_versionNotInSupported() {
    Map<String, DeploymentDetails> supportedVersions = Map.of("3.8", new DeploymentDetails("python:3.8-slim", "test_vdk_image"));

    ReflectionTestUtils.setField(
        supportedPythonVersions, SUPPORTED_PYTHON_VERSIONS, supportedVersions);

    Assertions.assertFalse(supportedPythonVersions.isPythonVersionSupported("3.7"));
  }

  @Test
  public void getSupportedPythonVersions_multipleSupportedVersions() {
    var supportedVersions = generateSupportedPythonVersionsConf();

    var res = Set.of("3.7", "3.8", "3.9");

    ReflectionTestUtils.setField(
        supportedPythonVersions, SUPPORTED_PYTHON_VERSIONS, supportedVersions);

    Assertions.assertEquals(res, supportedPythonVersions.getSupportedPythonVersions());
  }

  @Test
  public void getDefaultPythonVersion() {
    ReflectionTestUtils.setField(supportedPythonVersions, DEFAULT_PYTHON_VERSION, "3.7");
    var res = "3.7";

    Assertions.assertEquals(res, supportedPythonVersions.getDefaultPythonVersion());
  }

  @Test
  public void getJobBaseImage_defaultImage() {
    var supportedVersions = generateSupportedPythonVersionsConf();
    ReflectionTestUtils.setField(
        supportedPythonVersions, SUPPORTED_PYTHON_VERSIONS, supportedVersions);
    ReflectionTestUtils.setField(supportedPythonVersions, DEFAULT_PYTHON_VERSION, "3.7");
    final String defaultBaseImage = "python:3.7-slim";

    Assertions.assertEquals(defaultBaseImage, supportedPythonVersions.getJobBaseImage("3.11"));
  }

  @Test
  public void getJobBaseImage_multipleSupportedVersions() {
    var supportedVersions = generateSupportedPythonVersionsConf();

    final String resultBaseImg = "python:3.8-slim";
    ReflectionTestUtils.setField(
        supportedPythonVersions, SUPPORTED_PYTHON_VERSIONS, supportedVersions);

    Assertions.assertEquals(resultBaseImg, supportedPythonVersions.getJobBaseImage("3.8"));
  }

  @Test
  public void getVdkImage_defaultImage() {
    var supportedVersions = generateSupportedPythonVersionsConf();
    ReflectionTestUtils.setField(
        supportedPythonVersions, SUPPORTED_PYTHON_VERSIONS, supportedVersions);
    ReflectionTestUtils.setField(supportedPythonVersions, DEFAULT_PYTHON_VERSION, "3.7");

    final String defaultVdkImage = "test_vdk_image_3.7";

    Assertions.assertEquals(defaultVdkImage, supportedPythonVersions.getVdkImage("3.11"));
  }

  @Test
  public void getVdkImage_multipleSupportedVersions() {
    var supportedVersions = generateSupportedPythonVersionsConf();

    final String resultVdkImg = "test_vdk_image_3.8";
    ReflectionTestUtils.setField(
        supportedPythonVersions, SUPPORTED_PYTHON_VERSIONS, supportedVersions);

    Assertions.assertEquals(resultVdkImg, supportedPythonVersions.getVdkImage("3.8"));
  }

  private static Map<String, DeploymentDetails> generateSupportedPythonVersionsConf() {
    return Map.of(
            "3.7", new DeploymentDetails("python:3.7-slim", "test_vdk_image_3.7"),
            "3.8", new DeploymentDetails("python:3.8-slim", "test_vdk_image_3.8"),
            "3.9", new DeploymentDetails("python:3.9-slim", "test_vdk_image_3.9")
    );
  }
}
