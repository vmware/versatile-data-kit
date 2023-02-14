/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.notification;

import com.vmware.taurus.service.model.JobConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.mail.MessagingException;
import javax.mail.internet.AddressException;
import java.util.List;

/**
 * The DataJobNotification class is the interface used by the Versatile Data Kit service in order to
 * notify the customers about the status of their Job. The class's methods build notification
 * content object and send it to the user through email.
 *
 * @see NotificationContent
 * @see EmailNotification
 */
@Component
public class DataJobNotification {

  static Logger log = LoggerFactory.getLogger(DataJobNotification.class);

  private static final String DEPLOY_STAGE = "deploy";

  private static final String RUN_STAGE = "run";

  private static final String FAILURE_STATUS = "failure";

  private static final String SUCCESS_STATUS = "success";

  private String ownerName;

  private String ownerEmail;

  private List<String> ccEmails;

  private EmailNotification notification;

  public DataJobNotification(
      EmailNotification notification,
      @Value("${datajobs.notification.owner.name}") String ownerName,
      @Value("${datajobs.notification.owner.email}") String ownerEmail,
      @Value("${datajobs.notification.cc.emails:}") List<String> ccEmails) {
    this.notification = notification;
    this.ownerName = ownerName;
    this.ownerEmail = ownerEmail;
    this.ccEmails = ccEmails;
  }

  public void notifyJobDeploySuccess(JobConfig jobConfig) {
    try {
      NotificationContent notificationContent =
          new NotificationContent(
              jobConfig, DEPLOY_STAGE, SUCCESS_STATUS, ownerName, ownerEmail, ccEmails);
      notification.send(notificationContent);
    } catch (AddressException e) {
      log.warn("Could not send notification due to bad email format", e);
    } catch (MessagingException e) {
      log.warn("Could not send notification due to message error", e);
    }
  }

  // TODO: Potentially split to infrastructure and user error if possible
  public void notifyJobDeployError(JobConfig jobConfig, String errorName, String errorBody) {
    try {
      NotificationContent notificationContent =
          new NotificationContent(
              jobConfig,
              DEPLOY_STAGE,
              FAILURE_STATUS,
              errorName,
              errorBody,
              ownerName,
              ownerEmail,
              ccEmails);
      notification.send(notificationContent);
    } catch (AddressException e) {
      log.warn("Could not send notification due to bad email format", e);
    } catch (MessagingException e) {
      log.warn("Could not send notification due to message error", e);
    }
  }
}
