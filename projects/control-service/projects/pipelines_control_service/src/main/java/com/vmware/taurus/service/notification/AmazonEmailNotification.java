/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.notification;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.DefaultAWSCredentialsProviderChain;
import com.amazonaws.auth.STSAssumeRoleSessionCredentialsProvider;
import com.amazonaws.services.securitytoken.AWSSecurityTokenServiceClientBuilder;
import com.amazonaws.services.simpleemail.AmazonSimpleEmailService;
import com.amazonaws.services.simpleemail.AmazonSimpleEmailServiceClientBuilder;
import com.amazonaws.services.simpleemail.model.*;
import com.google.common.collect.Lists;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Primary;
import org.springframework.stereotype.Component;

import javax.mail.MessagingException;

/**
 * The AmazonEmailNotification class is responsible for implementing the email notifications
 * functionality in AWS using SES. The single exposed send method accepts pre-build notification
 * object.
 *
 * @see DataJobNotification
 * @see NotificationContent
 */
@Primary
@Component
public class AmazonEmailNotification extends EmailNotification {

  static Logger log = LoggerFactory.getLogger(AmazonEmailNotification.class);
  private final String roleArn;

  private final String region;

  public AmazonEmailNotification(EmailConfiguration emailConfiguration, @Value("datajobs.aws.roleArn") String roleArn) {
    super(emailConfiguration);
    log.info("Constructing AmazonEmailNotification class");
    this.region = "us-east-1";
    this.roleArn = roleArn;
  }

  @Override
  public void send(NotificationContent notificationContent) throws MessagingException {
    String roleSessionName = "email-session";

    STSAssumeRoleSessionCredentialsProvider credentialsProvider = new STSAssumeRoleSessionCredentialsProvider
            .Builder(this.roleArn, roleSessionName)
            .withStsClient(AWSSecurityTokenServiceClientBuilder.standard()
                    .withCredentials(new DefaultAWSCredentialsProviderChain())
                    .withRegion(this.region)
                    .build())
            .build();

    AmazonSimpleEmailService sesClient = AmazonSimpleEmailServiceClientBuilder.standard()
            .withCredentials(new AWSStaticCredentialsProvider(credentialsProvider.getCredentials()))
            .withRegion(this.region)
            .build();

    log.info("Send AmazonEmailNotification");
    SendEmailResult sendEmailResult =
        sesClient.sendEmail(
            new SendEmailRequest()
                .withSource("paulm2@vmware.com")
                .withDestination(
                    new Destination(Lists.newArrayList("yoan.salambashev@broadcom.com")))
                .withMessage(
                    new Message(
                        new Content("this is a test"), new Body(new Content("this is a test")))));
    log.info("Email sent using Amazon SES. Message ID: {}", sendEmailResult.getMessageId());
  }
}
