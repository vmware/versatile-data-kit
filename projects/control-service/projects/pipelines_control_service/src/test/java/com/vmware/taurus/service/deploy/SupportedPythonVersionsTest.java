/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.Map;
import java.util.Set;

import static com.vmware.taurus.service.deploy.SupportedPythonVersions.*;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
public class SupportedPythonVersionsTest {
  private static final String SUPPORTED_PYTHON_VERSIONS = "supportedPythonVersions";

  private static final String DEFAULT_PYTHON_VERSION = "defaultPythonVersion";

  @InjectMocks private SupportedPythonVersions supportedPythonVersions;

  @Mock private DockerRegistryService dockerRegistryService;

  @Test
  public void isPythonVersionSupported_noSupportedVersions() {
    ReflectionTestUtils.setField(supportedPythonVersions, SUPPORTED_PYTHON_VERSIONS, Map.of());

    Assertions.assertFalse(supportedPythonVersions.isPythonVersionSupported("3.7"));
  }

  @Test
  public void isPythonVersionSupported_versionSupported() {
    Map<String, Map<String, String>> supportedVersions =
        Map.of("3.7", Map.of(BASE_IMAGE, "python:3.7-slim", VDK_IMAGE, "test_vdk_image"));

    ReflectionTestUtils.setField(
        supportedPythonVersions, SUPPORTED_PYTHON_VERSIONS, supportedVersions);

    Assertions.assertTrue(supportedPythonVersions.isPythonVersionSupported("3.7"));
  }

  @Test
  public void isPythonVersionSupported_versionNotInSupported() {
    Map<String, Map<String, String>> supportedVersions =
        Map.of("3.8", Map.of(BASE_IMAGE, "python:3.8-slim", VDK_IMAGE, "test_vdk_image"));

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
  public void
      getBuilderImage_notSupportedPythonVersionAndProvidedBuilderImage_shouldReturnBuilderImageForDefaultPythonVersion() {
    var supportedVersions =
        Map.of(
            "3.7",
            Map.of(
                BASE_IMAGE,
                "python:3.7-slim",
                VDK_IMAGE,
                "test_vdk_image_3.7",
                BUILDER_IMAGE,
                "test_builder_image_3.7"),
            "3.8",
            Map.of(
                BASE_IMAGE,
                "python:3.8-slim",
                VDK_IMAGE,
                "test_vdk_image_3.8",
                BUILDER_IMAGE,
                "test_builder_image_3.8"),
            "3.9",
            Map.of(BASE_IMAGE, "python:3.9-slim", VDK_IMAGE, "test_vdk_image_3.9"),
            BUILDER_IMAGE,
            "test_builder_image_3.9");
    ReflectionTestUtils.setField(
        supportedPythonVersions, SUPPORTED_PYTHON_VERSIONS, supportedVersions);
    ReflectionTestUtils.setField(supportedPythonVersions, DEFAULT_PYTHON_VERSION, "3.7");
    when(dockerRegistryService.builderImage()).thenReturn("default_builder_image");

    Assertions.assertEquals(
        "test_builder_image_3.7", supportedPythonVersions.getBuilderImage("3.11"));
  }

  @Test
  public void
      getBuilderImage_notSupportedPythonVersionAndNotProvidedBuilderImage_shouldReturnDefaultBuilderImage() {
    var supportedVersions =
        Map.of(
            "3.7",
            Map.of(BASE_IMAGE, "python:3.7-slim", VDK_IMAGE, "test_vdk_image_3.7"),
            "3.8",
            Map.of(
                BASE_IMAGE,
                "python:3.8-slim",
                VDK_IMAGE,
                "test_vdk_image_3.8",
                BUILDER_IMAGE,
                "test_builder_image_3.8"),
            "3.9",
            Map.of(BASE_IMAGE, "python:3.9-slim", VDK_IMAGE, "test_vdk_image_3.9"),
            BUILDER_IMAGE,
            "test_builder_image_3.9");
    ReflectionTestUtils.setField(
        supportedPythonVersions, SUPPORTED_PYTHON_VERSIONS, supportedVersions);
    ReflectionTestUtils.setField(supportedPythonVersions, DEFAULT_PYTHON_VERSION, "3.7");
    when(dockerRegistryService.builderImage()).thenReturn("default_builder_image");

    Assertions.assertEquals(
        "default_builder_image", supportedPythonVersions.getBuilderImage("3.11"));
  }

  @Test
  public void
      getBuilderImage_supportedPythonVersionAndNotProvidedBuilderImage_shouldReturnDefaultBuilderImage() {
    var supportedVersions =
        Map.of(
            "3.7",
            Map.of(BASE_IMAGE, "python:3.7-slim", VDK_IMAGE, "test_vdk_image_3.7"),
            "3.8",
            Map.of(
                BASE_IMAGE,
                "python:3.8-slim",
                VDK_IMAGE,
                "test_vdk_image_3.8",
                BUILDER_IMAGE,
                "test_builder_image_3.8"),
            "3.9",
            Map.of(BASE_IMAGE, "python:3.9-slim", VDK_IMAGE, "test_vdk_image_3.9"),
            BUILDER_IMAGE,
            "test_builder_image_3.9");
    ReflectionTestUtils.setField(
        supportedPythonVersions, SUPPORTED_PYTHON_VERSIONS, supportedVersions);
    ReflectionTestUtils.setField(supportedPythonVersions, DEFAULT_PYTHON_VERSION, "3.7");
    when(dockerRegistryService.builderImage()).thenReturn("default_builder_image");

    Assertions.assertEquals(
        "default_builder_image", supportedPythonVersions.getBuilderImage("3.7"));
  }

  @Test
  public void
      getBuilderImage_supportedPythonVersionAndProvidedBuilderImage_shouldReturnBuilderImageForProvidedPythonVersion() {
    var supportedVersions =
        Map.of(
            "3.7",
            Map.of(
                BASE_IMAGE,
                "python:3.7-slim",
                VDK_IMAGE,
                "test_vdk_image_3.7",
                BUILDER_IMAGE,
                "test_builder_image_3.7"),
            "3.8",
            Map.of(
                BASE_IMAGE,
                "python:3.8-slim",
                VDK_IMAGE,
                "test_vdk_image_3.8",
                BUILDER_IMAGE,
                "test_builder_image_3.8"),
            "3.9",
            Map.of(BASE_IMAGE, "python:3.9-slim", VDK_IMAGE, "test_vdk_image_3.9"),
            BUILDER_IMAGE,
            "test_builder_image_3.9");
    ReflectionTestUtils.setField(
        supportedPythonVersions, SUPPORTED_PYTHON_VERSIONS, supportedVersions);
    ReflectionTestUtils.setField(supportedPythonVersions, DEFAULT_PYTHON_VERSION, "3.7");
    when(dockerRegistryService.builderImage()).thenReturn("default_builder_image");

    Assertions.assertEquals(
        "test_builder_image_3.8", supportedPythonVersions.getBuilderImage("3.8"));
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

    final String defaultVdkImage = "domain:5000/name:test_vdk_image_3.7";

    Assertions.assertEquals(defaultVdkImage, supportedPythonVersions.getVdkImage("3.11"));
  }

  @Test
  public void getVdkImage_multipleSupportedVersions() {
    var supportedVersions = generateSupportedPythonVersionsConf();

    final String resultVdkImg = "domain:5000/name:test_vdk_image_3.8";
    ReflectionTestUtils.setField(
        supportedPythonVersions, SUPPORTED_PYTHON_VERSIONS, supportedVersions);

    Assertions.assertEquals(resultVdkImg, supportedPythonVersions.getVdkImage("3.8"));
  }

  @Test
  public void replaceVdkVersionInImage_replaceTheImage() {
    var supportedVersions = generateSupportedPythonVersionsConf();
    ReflectionTestUtils.setField(
        supportedPythonVersions, SUPPORTED_PYTHON_VERSIONS, supportedVersions);
    ReflectionTestUtils.setField(supportedPythonVersions, DEFAULT_PYTHON_VERSION, "3.8");
    String resImage = "domain:5000/name:replaced_vdk_image";

    Assertions.assertEquals(
        resImage, supportedPythonVersions.replaceVdkVersionInImage("replaced_vdk_image"));
  }

  private static Map<String, Map<String, String>> generateSupportedPythonVersionsConf() {
    return Map.of(
        "3.7",
            Map.of(BASE_IMAGE, "python:3.7-slim", VDK_IMAGE, "domain:5000/name:test_vdk_image_3.7"),
        "3.8",
            Map.of(BASE_IMAGE, "python:3.8-slim", VDK_IMAGE, "domain:5000/name:test_vdk_image_3.8"),
        "3.9", Map.of(BASE_IMAGE, "python:3.9-slim", VDK_IMAGE, "test_vdk_image_3.9"));
  }
}
