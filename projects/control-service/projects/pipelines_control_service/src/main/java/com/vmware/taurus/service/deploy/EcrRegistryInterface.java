/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.auth.BasicSessionCredentials;
import com.amazonaws.services.ecr.AmazonECR;
import com.amazonaws.services.ecr.AmazonECRClientBuilder;
import com.amazonaws.services.ecr.model.DescribeImagesRequest;
import com.amazonaws.services.ecr.model.DescribeImagesResult;
import com.amazonaws.services.ecr.model.ImageIdentifier;
import com.amazonaws.services.ecr.model.ImageNotFoundException;
import com.amazonaws.services.ecr.model.RepositoryNotFoundException;
import com.vmware.taurus.service.credentials.AWSCredentialsService;
import com.vmware.taurus.service.credentials.AWSCredentialsService.AWSCredentialsDTO;
import lombok.extern.slf4j.Slf4j;
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
    if (!awsCredentialsDTO.awsSessionToken().isBlank()) {
      // need to include session token
      return new AWSStaticCredentialsProvider(new BasicSessionCredentials(
          awsCredentialsDTO.awsAccessKeyId(),
          awsCredentialsDTO.awsSecretAccessKey(),
          awsCredentialsDTO.awsSessionToken()));
    } else {
      // otherwise, we auth without session token
      return new AWSStaticCredentialsProvider(new BasicAWSCredentials(
          awsCredentialsDTO.awsAccessKeyId(), awsCredentialsDTO.awsSecretAccessKey()));
    }
  }

  public String extractImageRepositoryTag(String imageName){
    // imageName is a string of the sort:
    // 850879199482.dkr.ecr.us-west-2.amazonaws.com/sc/dp/job-name:hash
    return imageName.split("amazonaws.com/")[1];
  }

  private AmazonECR buildAmazonEcrClient(AWSCredentialsDTO awsCredentialsDTO) {
    AWSStaticCredentialsProvider awsStaticCredentialsProvider = createStaticCredentialsProvider(
        awsCredentialsDTO);

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
      log.info("Could not find image due to: {}", e);
    } catch (Exception e) {
      log.error("Failed to check if image exists due to: ", e);
    }
    return imageExists;
  }
}
