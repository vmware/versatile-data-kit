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

  public EmailNotification(EmailPropertiesConfiguration emailPropertiesConfiguration) {
    Properties properties = System.getProperties();
    properties.putAll(emailPropertiesConfiguration.smtpWithPrefix());
    session = Session.getDefaultInstance(properties);
  }

  public void send(NotificationContent notificationContent) throws MessagingException {
    if (recipientsExist(notificationContent.getRecipients())) {
      MimeMessage mimeMessage = new MimeMessage(session);
      mimeMessage.setFrom(notificationContent.getSender());
      mimeMessage.setRecipients(MimeMessage.RecipientType.TO, notificationContent.getRecipients());
      mimeMessage.setSubject(notificationContent.getSubject());
      mimeMessage.setContent(notificationContent.getContent(), CONTENT_TYPE);
      try {
        Transport.send(mimeMessage);
      } catch (SendFailedException firstException) {
        log.info(
            "Following addresses are invalid: {}",
            concatAddresses(firstException.getInvalidAddresses()));
        var validUnsentAddresses = firstException.getValidUnsentAddresses();
        if (recipientsExist(validUnsentAddresses)) {
          log.info("Retrying unsent valid addresses: {}", concatAddresses(validUnsentAddresses));
          mimeMessage.setRecipients(MimeMessage.RecipientType.TO, validUnsentAddresses);
          try {
            Transport.send(mimeMessage);
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

  private boolean recipientsExist(Address[] recipients) {
    return recipients.length > 0;
  }

  String concatAddresses(Address[] addresses) {
    return addresses == null
        ? null
        : Arrays.asList(addresses).stream()
            .map(addr -> addr.toString())
            .collect(Collectors.joining(" "));
  }
}
