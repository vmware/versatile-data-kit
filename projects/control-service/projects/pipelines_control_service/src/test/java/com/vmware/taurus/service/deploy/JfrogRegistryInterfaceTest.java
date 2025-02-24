/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import org.jfrog.artifactory.client.Searches;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockedStatic;
import org.mockito.MockitoAnnotations;
import org.jfrog.artifactory.client.Artifactory;
import org.jfrog.artifactory.client.ArtifactoryClientBuilder;
import org.jfrog.artifactory.client.model.AqlItem;
import org.jfrog.filespecs.FileSpec;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class JfrogRegistryInterfaceTest {

  @Mock private ArtifactoryClientBuilder artifactoryClientBuilder;

  @Mock private Artifactory artifactory;

  @Mock private Searches searches;

  @InjectMocks private JfrogRegistryInterface jfrogRegistryInterface;

  private final String imageName = "test-image:latest";

  @BeforeEach
  void setUp() {
    MockitoAnnotations.openMocks(this);
    ReflectionTestUtils.setField(jfrogRegistryInterface, "artifactoryUrl", "url");
    ReflectionTestUtils.setField(jfrogRegistryInterface, "artifactoryUsername", "username");
    ReflectionTestUtils.setField(jfrogRegistryInterface, "artifactoryPassword", "password");
    ReflectionTestUtils.setField(jfrogRegistryInterface, "artifactoryDockerRepoName", "repo");

    when(artifactoryClientBuilder.setUsername(anyString())).thenReturn(artifactoryClientBuilder);
    when(artifactoryClientBuilder.setUrl(anyString())).thenReturn(artifactoryClientBuilder);
    when(artifactoryClientBuilder.setPassword(anyString())).thenReturn(artifactoryClientBuilder);
    when(artifactoryClientBuilder.build()).thenReturn(artifactory);
    when(artifactory.searches()).thenReturn(searches);
    when(searches.repositories(any())).thenReturn(searches);
  }

  @Test
  void testCheckJfrogImageExists_ImageExists() {
    try (MockedStatic<ArtifactoryClientBuilder> artifactoryClientBuilderMockedStatic =
        mockStatic(ArtifactoryClientBuilder.class)) {
      artifactoryClientBuilderMockedStatic
          .when(ArtifactoryClientBuilder::create)
          .thenReturn(artifactoryClientBuilder);
      List<AqlItem> repoPaths = Collections.singletonList(mock(AqlItem.class));
      when(artifactory
              .searches()
              .repositories(anyString())
              .artifactsByFileSpec(any(FileSpec.class)))
          .thenReturn(repoPaths);

      // Execution
      boolean imageExists = jfrogRegistryInterface.checkJfrogImageExists(imageName);

      // Verification
      assertTrue(imageExists);
    }
  }

  @Test
  void testCheckJfrogImageExists_ImageDoesNotExist() {
    try (MockedStatic<ArtifactoryClientBuilder> artifactoryClientBuilderMockedStatic =
        mockStatic(ArtifactoryClientBuilder.class)) {
      artifactoryClientBuilderMockedStatic
          .when(ArtifactoryClientBuilder::create)
          .thenReturn(artifactoryClientBuilder);
      // Mocking behavior
      when(searches.repositories(anyString()).artifactsByFileSpec(any(FileSpec.class)))
          .thenReturn(Collections.emptyList());

      // Execution
      boolean imageExists = jfrogRegistryInterface.checkJfrogImageExists(imageName);

      // Verification
      assertFalse(imageExists);
    }
  }

  @Test
  void testCheckJfrogImageExists_Exception() {
    try (MockedStatic<ArtifactoryClientBuilder> artifactoryClientBuilderMockedStatic =
        mockStatic(ArtifactoryClientBuilder.class)) {
      artifactoryClientBuilderMockedStatic
          .when(ArtifactoryClientBuilder::create)
          .thenReturn(artifactoryClientBuilder);
      // Mocking behavior
      when(artifactory
              .searches()
              .repositories(anyString())
              .artifactsByFileSpec(any(FileSpec.class)))
          .thenThrow(new RuntimeException("Simulated exception"));

      // Execution
      boolean imageExists = jfrogRegistryInterface.checkJfrogImageExists(imageName);

      // Verification
      assertFalse(imageExists);
    }
  }
}
