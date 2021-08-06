/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.notification;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.mail.*;
import javax.mail.internet.MimeMessage;
import java.util.Arrays;
import java.util.Properties;
import java.util.stream.Collectors;

/**
 * The EmailNotification class is responsible for implementing the email notifications functionality.
 * The single exposed send method accepts pre-build notification object.
 *
 * @see DataJobNotification
 * @see NotificationContent
 */
public class EmailNotification {

    static Logger log = LoggerFactory.getLogger(EmailNotification.class);

    private static final String CONTENT_TYPE = "text/html; charset=utf-8";

    private static final String SMTP_SERVER_VALUE = "smtp.vmware.com";

    private static final String SMTP_SERVER_KEY = "mail.smtp.host";

    private final Session session;

    public EmailNotification() {
        Properties properties = System.getProperties();
        properties.setProperty(SMTP_SERVER_KEY, SMTP_SERVER_VALUE);
        session = Session.getDefaultInstance(properties);
    }

    public void send(NotificationContent notificationContent)
            throws MessagingException {
        if (recipientsExist(notificationContent.getRecipients())) {
            MimeMessage mimeMessage = new MimeMessage(session);
            mimeMessage.setFrom(notificationContent.getSender());
            mimeMessage.setRecipients(MimeMessage.RecipientType.TO, notificationContent.getRecipients());
            mimeMessage.setSubject(notificationContent.getSubject());
            mimeMessage.setContent(notificationContent.getContent(), CONTENT_TYPE);
            try {
                Transport.send(mimeMessage);
            } catch (SendFailedException firstException) {
                log.info("Following addresses are invalid: {}", concatAddresses(firstException.getInvalidAddresses()));
                var validUnsentAddresses = firstException.getValidUnsentAddresses();
                if (recipientsExist(validUnsentAddresses)) {
                    log.info("Retrying unsent valid addresses: {}", concatAddresses(validUnsentAddresses));
                    mimeMessage.setRecipients(MimeMessage.RecipientType.TO, validUnsentAddresses);
                    try {
                        Transport.send(mimeMessage);
                    } catch (SendFailedException retriedException) {
                        log.warn("\nwhat: {}\nwhy: {}\nconsequence: {}\ncountermeasure: {}",
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
        if (recipients.length == 0) {
            return false;
        }
        return true;
    }

    private String concatAddresses(Address[] addresses) {
        return Arrays.asList(addresses)
                .stream()
                .map(addr -> addr.toString())
                .collect(Collectors.joining(" "));
    }
}
