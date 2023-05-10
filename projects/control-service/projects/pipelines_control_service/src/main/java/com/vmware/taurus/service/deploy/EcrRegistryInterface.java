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

  private AmazonECR buildAmazonEcrClient(
      AWSCredentialsDTO awsCredentialsDTO) {
    AWSStaticCredentialsProvider awsStaticCredentialsProvider;
    if (!awsCredentialsDTO.awsSessionToken().isBlank()) {
      // need to include session token
      var sessionCredentials =
          new BasicSessionCredentials(
              awsCredentialsDTO.awsAccessKeyId(),
              awsCredentialsDTO.awsSecretAccessKey(),
              awsCredentialsDTO.awsSessionToken());
      awsStaticCredentialsProvider = new AWSStaticCredentialsProvider(sessionCredentials);
    } else {
      // otherwise, we auth without session token
      var credentials =
          new BasicAWSCredentials(awsCredentialsDTO.awsAccessKeyId(),
              awsCredentialsDTO.awsSecretAccessKey());
      awsStaticCredentialsProvider = new AWSStaticCredentialsProvider(credentials);
    }

    AmazonECR ecrClient =
        AmazonECRClientBuilder.standard()
            .withCredentials(awsStaticCredentialsProvider)
            .withRegion(awsCredentialsDTO.region())
            .build();

    return ecrClient;
  }

  private DescribeImagesRequest buildDescribeImagesRequest(String imageName,
      AWSCredentialsService.AWSCredentialsDTO awsCredentialsDTO) {
    // imageName is a string of the sort:
    // 850879199482.dkr.ecr.us-west-2.amazonaws.com/sc/dp/job-name:hash
    String imageRepoTag = imageName.split("amazonaws.com/")[1];
    ImageIdentifier imageIdentifier =
        new ImageIdentifier().withImageTag(imageRepoTag.split(":")[1]);
    String imageRepository = imageRepoTag.split(":")[0];

    return new DescribeImagesRequest()
        .withRepositoryName(imageRepository)
        .withImageIds(imageIdentifier);
  }

  public boolean checkEcrImageExists(String imageName,
      AWSCredentialsService.AWSCredentialsDTO awsCredentialsDTO) {

    AmazonECR ecrClient = buildAmazonEcrClient(awsCredentialsDTO);
    DescribeImagesRequest describeImagesRequest = buildDescribeImagesRequest(imageName,
        awsCredentialsDTO);
    boolean imageExists = false;
    try {
      DescribeImagesResult describeImagesResult = ecrClient.describeImages(describeImagesRequest);
      if (describeImagesResult.getImageDetails().size() == 1) {
        imageExists = true;
      }
    } catch (ImageNotFoundException
        | RepositoryNotFoundException e) {
      log.info("Could not find image due to: {}", e);
    } catch (Exception e) {
      log.error("Failed to check if image exists due to: ", e);
    }
    return imageExists;
  }

}
