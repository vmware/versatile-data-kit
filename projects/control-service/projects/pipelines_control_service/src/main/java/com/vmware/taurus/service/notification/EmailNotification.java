/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.notification;

import java.util.Arrays;
import java.util.Properties;
import java.util.stream.Collectors;
import javax.mail.Address;
import javax.mail.MessagingException;
import javax.mail.SendFailedException;
import javax.mail.Session;
import javax.mail.Transport;
import javax.mail.internet.MimeMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
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
    if (recipientsExist(notificationContent.getRecipients())) {
      try {
        sendEmail(notificationContent, notificationContent.getRecipients());
      } catch (SendFailedException firstException) {
        log.info(
            "Following addresses are invalid: {}",
            concatAddresses(firstException.getInvalidAddresses()));
        var validUnsentAddresses = firstException.getValidUnsentAddresses();
        if (recipientsExist(validUnsentAddresses)) {
          log.info("Retrying unsent valid addresses: {}", concatAddresses(validUnsentAddresses));
          try {
            sendEmail(notificationContent, validUnsentAddresses);
          } catch (SendFailedException retriedException) {
            log.warn(
                "\nwhat: {}\nwhy: {}\nconsequence: {}\ncountermeasure: {}",
                "Unable to send notification to the recipients",
                retriedException.getMessage(),
                "Listed recipients won't receive notifications for the job's status",
                "There might be misconfiguration or outage. Check error message for more details");
          }
        }
      }
    }
  }

  private void sendEmail(NotificationContent notificationContent, Address[] recipients)
      throws MessagingException {
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
      transport.connect(emailConfiguration.getUsername(), emailConfiguration.getPassword());
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
