/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.notification;

import java.util.Arrays;
import java.util.Properties;
import java.util.stream.Collectors;
import javax.mail.Address;
import javax.mail.MessagingException;
import javax.mail.Session;
import javax.mail.Transport;
import javax.mail.internet.MimeMessage;

import com.amazonaws.auth.DefaultAWSCredentialsProviderChain;
import com.amazonaws.services.simpleemail.AmazonSimpleEmailService;
import com.amazonaws.services.simpleemail.AmazonSimpleEmailServiceClientBuilder;
import com.amazonaws.services.simpleemail.model.*;
import com.google.common.collect.Lists;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Bean;
import org.springframework.stereotype.Component;

/**
 * The EmailNotification class is responsible for implementing the email notifications
 * functionality. The single exposed send method accepts pre-build notification object.
 *
 * @see DataJobNotification
 * @see NotificationContent
 */
@Component
public class EmailNotification {

  static Logger log = LoggerFactory.getLogger(EmailNotification.class);

  private static final String CONTENT_TYPE = "text/html; charset=utf-8";

  private final Session session;
  private final EmailConfiguration emailConfiguration;

  public EmailNotification(EmailConfiguration emailConfiguration) {
    this.emailConfiguration = emailConfiguration;
    Properties properties = System.getProperties();
    properties.putAll(emailConfiguration.smtpWithPrefix());
    properties.setProperty("mail.transport.protocol", emailConfiguration.getTransportProtocol());
    session = Session.getInstance(properties);
  }


  public void send(NotificationContent notificationContent) throws MessagingException {
    AmazonSimpleEmailService build = AmazonSimpleEmailServiceClientBuilder.standard()
            .withCredentials(new DefaultAWSCredentialsProviderChain())
            .withRegion("us-east-1")
            .build();
    SendEmailResult sendEmailResult = build.sendEmail(new SendEmailRequest().withSource("paulm2@vmware.com")
            .withDestination(new Destination(Lists.newArrayList("paulm2@vmware.com")))
            .withMessage(new Message(new Content("this is a test"),
                    new Body(new Content("this is a test")))));
  }

  private void sendEmail(NotificationContent notificationContent, Address[] recipients)
      throws MessagingException {
    log.info("is email auth enabled " + emailConfiguration.isAuthEnabled());
    log.info("notification context " + emailConfiguration.isAuthEnabled());
    if (emailConfiguration.isAuthEnabled()) {
      sendAuthenticatedEmail(notificationContent, recipients);
    } else {
      sendUnauthenticatedEmail(notificationContent, recipients);
    }
  }

  private void sendUnauthenticatedEmail(
      NotificationContent notificationContent, Address[] recipients) throws MessagingException {
    var mimeMessage = prepareMessage(notificationContent);
    Transport.send(mimeMessage, recipients);
  }

  private void sendAuthenticatedEmail(NotificationContent notificationContent, Address[] recipients)
      throws MessagingException {
    Transport transport = session.getTransport();
    var mimeMessage = prepareMessage(notificationContent);
    try {
      transport.connect(emailConfiguration.getUsername(), "BFr6/lykIex01+2ESOGRSL0mxXo+zq0MtnS3UAG8SFiF");
      transport.sendMessage(mimeMessage, recipients);
    } finally {
      transport.close();
    }
  }

  private MimeMessage prepareMessage(NotificationContent notificationContent)
      throws MessagingException {
    MimeMessage mimeMessage = new MimeMessage(session);
    mimeMessage.setFrom(notificationContent.getSender());
    mimeMessage.setRecipients(MimeMessage.RecipientType.TO, notificationContent.getRecipients());
    mimeMessage.setSubject(notificationContent.getSubject());
    mimeMessage.setContent(notificationContent.getContent(), CONTENT_TYPE);
    return mimeMessage;
  }

  private boolean recipientsExist(Address[] recipients) {
    return recipients.length > 0;
  }

  String concatAddresses(Address[] addresses) {
    return addresses == null
        ? null
        : Arrays.stream(addresses).map(Address::toString).collect(Collectors.joining(" "));
  }
}
