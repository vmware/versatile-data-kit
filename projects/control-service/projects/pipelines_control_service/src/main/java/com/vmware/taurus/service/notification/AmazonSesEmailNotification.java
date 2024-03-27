/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.notification;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.DefaultAWSCredentialsProviderChain;
import com.amazonaws.auth.STSAssumeRoleSessionCredentialsProvider;
import com.amazonaws.services.securitytoken.AWSSecurityTokenServiceClientBuilder;
import com.amazonaws.services.simpleemail.AmazonSimpleEmailServiceClientBuilder;
import com.amazonaws.services.simpleemail.model.*;
import com.google.common.collect.Lists;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Primary;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

import javax.mail.MessagingException;
import javax.mail.internet.InternetAddress;
import java.util.Arrays;

/**
 * The AmazonEmailNotification class is responsible for implementing the email notifications
 * functionality in AWS using SES. The single exposed send method accepts pre-build notification
 * object.
 *
 * @see DataJobNotification
 * @see NotificationContent
 */
@Profile("amazon_ses")
@Primary
@Component
public class AmazonSesEmailNotification implements EmailNotification {

  static Logger log = LoggerFactory.getLogger(AmazonSesEmailNotification.class);
  private final String roleArn;
  private String region;

  public AmazonSesEmailNotification(EmailConfiguration emailConfiguration) {
    log.info("Constructing AmazonEmailNotification class");
    this.region = emailConfiguration.mail().get("mail.smtp.host");
    this.roleArn = emailConfiguration.getUsername();
  }

  @Override
  public void send(NotificationContent notificationContent) throws MessagingException {
    String roleSessionName = "email-session";

    STSAssumeRoleSessionCredentialsProvider credentialsProvider =
        new STSAssumeRoleSessionCredentialsProvider.Builder(roleArn, roleSessionName)
            .withStsClient(
                AWSSecurityTokenServiceClientBuilder.standard()
                    .withCredentials(new DefaultAWSCredentialsProviderChain())
                    .withRegion(this.region)
                    .build())
            .build();

    var sesClient =
        AmazonSimpleEmailServiceClientBuilder.standard()
            .withCredentials(new AWSStaticCredentialsProvider(credentialsProvider.getCredentials()))
            .withRegion(this.region)
            .build();
    log.info("Send AmazonEmailNotification");
    SendEmailResult sendEmailResult =
        sesClient.sendEmail(
            new SendEmailRequest()
                .withSource(notificationContent.getSender().toString())
                .withDestination(
                    new Destination(
                        Lists.newArrayList(
                            Arrays.stream(notificationContent.getRecipients())
                                .map(InternetAddress::toString)
                                .toList())))
                .withMessage(
                    new Message(
                        new Content(notificationContent.getSubject()),
                        new Body(new Content(notificationContent.getContent())))));
    log.info("Email sent using Amazon SES. Message ID: {}", sendEmailResult.getMessageId());
  }
}
