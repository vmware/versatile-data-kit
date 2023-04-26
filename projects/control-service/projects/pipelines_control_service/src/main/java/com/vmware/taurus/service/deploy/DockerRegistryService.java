/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.auth.BasicSessionCredentials;
import com.amazonaws.services.ecr.model.ImageNotFoundException;
import com.amazonaws.services.ecr.model.InvalidParameterException;
import com.amazonaws.services.ecr.model.RepositoryNotFoundException;
import com.amazonaws.services.ecr.model.ServerException;
import com.vmware.taurus.service.credentials.AWSCredentialsService;
import com.vmware.taurus.service.credentials.AWSCredentialsService.AWSCredentialsDTO;
import com.vmware.taurus.service.credentials.AWSCredentialsServiceConfig;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import com.amazonaws.services.ecr.AmazonECR;
import com.amazonaws.services.ecr.AmazonECRClientBuilder;
import com.amazonaws.services.ecr.model.DescribeImagesRequest;
import com.amazonaws.services.ecr.model.DescribeImagesResult;
import com.amazonaws.services.ecr.model.ImageIdentifier;

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

  private AWSCredentialsService awsCredentialsService;

  public DockerRegistryService(AWSCredentialsServiceConfig awsCredentialsServiceConfig,
      AWSCredentialsService awsCredentialsService) {
    this.awsCredentialsService = awsCredentialsService;
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
  public boolean dataJobImageExists(String imageName
  ) {

    if (registryType.toLowerCase().equals("ecr")) {
      return checkImageExistsInEcr(imageName);
    }

    return false;
  }

  private boolean checkImageExistsInEcr(String imageName) {
    // imageName is a string of the sort:
    // 850879199482.dkr.ecr.us-west-2.amazonaws.com/sc/dp/integration-test-6ebd50b6:b722432f9f0aaa43fcec6cb68993651145815990
    String imageRepoTag = imageName.split("amazonaws.com/")[1];
    ImageIdentifier imageIdentifier = new ImageIdentifier().withImageTag(
        imageRepoTag.split(":")[1]);
    String imageRepository = imageRepoTag.split(":")[0];

    var credentials = awsCredentialsService.createTemporaryCredentials();

    AmazonECR ecrClient;
    AWSStaticCredentialsProvider awsStaticCredentialsProvider;
    if (!credentials.awsSessionToken().isBlank()) {
      // need to include session token
      var sessCreds = new BasicSessionCredentials(credentials.awsAccessKeyId(),
          credentials.awsSecretAccessKey(), credentials.awsSessionToken());
      awsStaticCredentialsProvider = new AWSStaticCredentialsProvider(sessCreds);

    } else {
      // otherwise, we auth without session token
      var creds = new BasicAWSCredentials(credentials.awsAccessKeyId(),
          credentials.awsSecretAccessKey());
      awsStaticCredentialsProvider = new AWSStaticCredentialsProvider(creds);
    }

    ecrClient = AmazonECRClientBuilder.standard()
        .withCredentials(awsStaticCredentialsProvider).withRegion(credentials.region()).build();

    DescribeImagesRequest describeImagesRequest = new DescribeImagesRequest()
        .withRepositoryName(imageRepository)
        .withImageIds(imageIdentifier);

    try {
      DescribeImagesResult describeImagesResult = ecrClient.describeImages(describeImagesRequest);
      if (describeImagesResult.getImageDetails().size() == 1) {
        return true;
      }
    } catch (ImageNotFoundException | RepositoryNotFoundException | ServerException | InvalidParameterException e) {
      log.info("Could not find image due to: {}", e);
      return false;
    } catch (Exception e) {
      log.error("Failed to check if image exists due to: ", e);
      return false;
    }
    return false;
  }

}
