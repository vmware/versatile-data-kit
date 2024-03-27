/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.notification;

import com.amazonaws.auth.DefaultAWSCredentialsProviderChain;
import com.amazonaws.services.simpleemail.AmazonSimpleEmailService;
import com.amazonaws.services.simpleemail.AmazonSimpleEmailServiceClientBuilder;
import com.amazonaws.services.simpleemail.model.*;
import com.google.common.collect.Lists;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
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

  private String region;
  private final AmazonSimpleEmailService sesClient;

  public AmazonEmailNotification(EmailConfiguration emailConfiguration) {
    super(emailConfiguration);
    log.info("Constructing AmazonEmailNotification class");
    this.region = "us-east-1";
    this.sesClient =
        AmazonSimpleEmailServiceClientBuilder.standard()
            .withCredentials(new DefaultAWSCredentialsProviderChain())
            .withRegion(this.region)
            .build();
  }

  @Override
  public void send(NotificationContent notificationContent) throws MessagingException {
    log.info("Send AmazonEmailNotification");
    SendEmailResult sendEmailResult =
        sesClient.sendEmail(
            new SendEmailRequest()
                .withSource("paulm2@vmware.com")
                .withDestination(new Destination(Lists.newArrayList("paulm2@vmware.com")))
                .withMessage(
                    new Message(
                        new Content("this is a test"), new Body(new Content("this is a test")))));
    log.info("Email sent using Amazon SES. Message ID: {}", sendEmailResult.getMessageId());
  }
}
