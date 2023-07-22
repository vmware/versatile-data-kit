/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.amazonaws.AmazonClientException;
import com.amazonaws.services.ecr.AmazonECR;
import com.amazonaws.services.ecr.model.*;
import com.vmware.taurus.exception.ExternalSystemError;
import com.vmware.taurus.service.credentials.AWSCredentialsService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

class EcrRegistryInterfaceTest {
  private EcrRegistryInterface ecrRegistryInterface;

  @Mock private AWSCredentialsService.AWSCredentialsDTO awsCredentialsDTO;

  @Mock private AmazonECR amazonECR;

  @Mock private CreateRepositoryResult createRepositoryResult;

  @Mock private Repository repository;

  @BeforeEach
  public void setUp() {
    MockitoAnnotations.initMocks(this);
    ecrRegistryInterface = new EcrRegistryInterface();
  }

  @Test
  public void testExtractImageRepositoryTag() {
    String imageName = "850879199482.dkr.ecr.us-west-2.amazonaws.com/sc/dp/job-name:hash";
    String expected = "sc/dp/job-name:hash";
    assertEquals(expected, ecrRegistryInterface.extractImageRepositoryTag(imageName));
  }

  @Test
  public void testCreateRepositoryFailure() {
    String repositoryName = "repo";
    when(awsCredentialsDTO.region()).thenReturn("us-west-2");
    when(awsCredentialsDTO.awsAccessKeyId()).thenReturn("");
    when(awsCredentialsDTO.awsSecretAccessKey()).thenReturn("");
    when(amazonECR.createRepository(any(CreateRepositoryRequest.class)))
        .thenThrow(new RuntimeException());
    assertThrows(
        Exception.class,
        () -> ecrRegistryInterface.createRepository(repositoryName, awsCredentialsDTO));
  }

  @Test
  public void testCreateRepositoryFailureEcrException() {
    String repositoryName = "repo";
    when(awsCredentialsDTO.region()).thenReturn("us-west-2");
    when(awsCredentialsDTO.awsAccessKeyId()).thenReturn("");
    when(awsCredentialsDTO.awsSecretAccessKey()).thenReturn("");
    when(amazonECR.createRepository(any(CreateRepositoryRequest.class)))
        .thenThrow(new AmazonClientException(""));
    assertThrows(
        ExternalSystemError.class,
        () -> ecrRegistryInterface.createRepository(repositoryName, awsCredentialsDTO));
  }
}
