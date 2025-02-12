/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.notification;

import javax.mail.MessagingException;

/**
 * The EmailNotification class is responsible for implementing the email notifications
 * functionality. The single exposed send method accepts pre-build notification object.
 *
 * @see DataJobNotification
 * @see NotificationContent
 */
public interface EmailNotification {

  public void send(NotificationContent notificationContent) throws MessagingException;
}
