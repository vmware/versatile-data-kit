/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.amazonaws.AmazonClientException;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.auth.BasicSessionCredentials;
import com.amazonaws.services.ecr.AmazonECR;
import com.amazonaws.services.ecr.AmazonECRClientBuilder;
import com.amazonaws.services.ecr.model.*;
import com.vmware.taurus.exception.ExternalSystemError;
import com.vmware.taurus.service.credentials.AWSCredentialsService;
import com.vmware.taurus.service.credentials.AWSCredentialsService.AWSCredentialsDTO;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;

/**
 * This class is used to provide interface methods between an Amazon Elastic Container Registry and
 * the control service.
 */
@Service
@Slf4j
public class EcrRegistryInterface {

  public AWSStaticCredentialsProvider createStaticCredentialsProvider(
      AWSCredentialsDTO awsCredentialsDTO) {
    if (!StringUtils.isBlank(awsCredentialsDTO.awsSessionToken())) {
      // need to include session token
      return new AWSStaticCredentialsProvider(
          new BasicSessionCredentials(
              awsCredentialsDTO.awsAccessKeyId(),
              awsCredentialsDTO.awsSecretAccessKey(),
              awsCredentialsDTO.awsSessionToken()));
    } else {
      // otherwise, we auth without session token
      return new AWSStaticCredentialsProvider(
          new BasicAWSCredentials(
              awsCredentialsDTO.awsAccessKeyId(), awsCredentialsDTO.awsSecretAccessKey()));
    }
  }

  public String extractImageRepositoryTag(String imageName) {
    // imageName is a string of the sort:
    // 850879199482.dkr.ecr.us-west-2.amazonaws.com/sc/dp/job-name:hash'
    return imageName.split("amazonaws.com/")[1];
  }

  private AmazonECR buildAmazonEcrClient(AWSCredentialsDTO awsCredentialsDTO) {
    AWSStaticCredentialsProvider awsStaticCredentialsProvider =
        createStaticCredentialsProvider(awsCredentialsDTO);

    return AmazonECRClientBuilder.standard()
        .withCredentials(awsStaticCredentialsProvider)
        .withRegion(awsCredentialsDTO.region())
        .build();
  }

  private DescribeImagesRequest buildDescribeImagesRequest(String imageName) {
    // imageName is a string of the sort:
    // 850879199482.dkr.ecr.us-west-2.amazonaws.com/sc/dp/job-name:hash
    String imageRepoTag = extractImageRepositoryTag(imageName);
    ImageIdentifier imageIdentifier =
        new ImageIdentifier().withImageTag(imageRepoTag.split(":")[1]);
    String imageRepository = imageRepoTag.split(":")[0];

    return new DescribeImagesRequest()
        .withRepositoryName(imageRepository)
        .withImageIds(imageIdentifier);
  }

  private static boolean existsRepository(AmazonECR ecrClient, String repositoryName) {
    try {
      ecrClient.describeRepositories(
          new DescribeRepositoriesRequest().withRepositoryNames(repositoryName));
      return true;
    } catch (RepositoryNotFoundException e) {
      log.debug("Repository does not exist: {}", repositoryName);
      return false;
    } catch (Exception e) {
      log.warn("Failed to check if image exists and will assume it doesn't exist. Exception: " + e);
      return false;
    }
  }

  /**
   * Checks if a specific image exists in the Amazon ECR.
   *
   * @param imageName the name of the image whose existence is to be checked
   * @param awsCredentialsDTO the DTO containing AWS credentials information
   * @return true if the specified image exists, false otherwise
   */
  public boolean checkEcrImageExists(
      String imageName, AWSCredentialsService.AWSCredentialsDTO awsCredentialsDTO) {

    AmazonECR ecrClient = buildAmazonEcrClient(awsCredentialsDTO);
    DescribeImagesRequest describeImagesRequest = buildDescribeImagesRequest(imageName);
    boolean imageExists = false;
    try {
      DescribeImagesResult describeImagesResult = ecrClient.describeImages(describeImagesRequest);
      if (describeImagesResult.getImageDetails().size() == 1) {
        imageExists = true;
      }
    } catch (ImageNotFoundException | RepositoryNotFoundException e) {
      log.info("Could not find image due to " + e);
    } catch (Exception e) {
      log.warn("Failed to check if image exists and will assume it doesn't exist. Exception: " + e);
    }
    return imageExists;
  }

  /**
   * Creates a repository in Amazon ECR with the provided repository name. If a repository with the
   * same name already exists, then nothing happens and operation succeeds.
   *
   * @param repositoryName the name of the repository to be created. This is without the registry part of URI:
   *                       e.g. if full URL is aws_account_id.dkr.ecr.us-west-2.amazonaws.com/my-ns/my-repository:tag ,
   *                       the repository name is "my-ns/my-repository"
   * @param awsCredentialsDTO the DTO containing AWS credentials information
   * @throws ExternalSystemError if other exception occurs during repository creation with container
   *     registry
   */
  public void createRepository(
      String repositoryName, AWSCredentialsService.AWSCredentialsDTO awsCredentialsDTO) {
    AmazonECR ecrClient = buildAmazonEcrClient(awsCredentialsDTO);

    try {

      if (!existsRepository(ecrClient, repositoryName)) {
        log.debug("Create ECR repository {}", repositoryName);
        CreateRepositoryRequest createRepositoryRequest =
            new CreateRepositoryRequest().withRepositoryName(repositoryName);

        CreateRepositoryResult createRepositoryResult =
            ecrClient.createRepository(createRepositoryRequest);

        String repositoryUri = createRepositoryResult.getRepository().getRepositoryUri();
        log.debug("ECR repository created: {}", repositoryUri);
      }

    } catch (AmazonClientException e) {
      throw new ExternalSystemError(
          ExternalSystemError.MainExternalSystem.CONTAINER_REGISTRY,
          "Creating container repository " + repositoryName + " failed.",
          e);
    }
  }
}
