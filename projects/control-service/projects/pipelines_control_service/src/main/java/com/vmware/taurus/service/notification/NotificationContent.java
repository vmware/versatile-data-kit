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
import lombok.Getter;

import javax.mail.internet.AddressException;
import javax.mail.internet.InternetAddress;
import java.util.ArrayList;
import java.util.List;

@Getter
/**
 * The NotificationContent class is used to build the notifications which will be sent to the users.
 *
 * @see DataJobNotification
 * @see EmailNotification
 */
public class NotificationContent {

  private static final String NOTIFICATION_MSG_TEMPLATE =
      "<p>Dear Data Pipelines user,<br/>\n"
          + "Last %s of your data job <strong>%s</strong> has status: %s.</p>\n"
          + "%s\n"
          + // exec_type, job_name, result, error details
          "<p>The sender mailbox is not monitored, please do not reply to this email.</p>\n"
          + "<p>Best,<br/>%s</p>\n";

  private static final String NOTIFICATION_MSG_SUBJECT_TEMPLATE = "[%s][data job %s] %s";

  private static final String USER_ERROR_TEMPLATE =
      "<p style=\"padding-left: 30px; color:red;\">"
          + "<br/>WHAT HAPPENED: %s"
          + "<br/>WHY IT HAPPENED: %s"
          + "<br/>CONSEQUENCES: %s"
          + "<br/>COUNTERMEASURES: %s"
          + "</p>";

  // TODO: Find usage once infra error is defined in the context of the service
  private static final String INFRA_ERROR_TEMPLATE =
      "<p>Details:</p>\n"
          + "<p style=\"padding-left: 30px; color:red;\">%s</p>"; // error_msg - Exception

  // TODO: Move user guide to the Taurus one once it is out
  // TODO: allow IT Ops/Admin team to customize the template
  private static final String GENERAL_ERROR_TEMPLATE =
      "<p>Data job: %s error.</p>\n"
          + "<p>Details:</p>\n"
          + "<p style=\"padding-left: 30px; color:red;\">%s</p>\n"
          + "<p>%s</p>\n"
          + "<p>For more information please visit&nbsp;\n"
          + "<a href=\"https://confluence.eng.vmware.com/display/SUPCR/Data+Pipelines+User+Guide#DataPipelinesUserGuide-Monitoring&amp;Troubleshooting\">Data"
          + " Pipelines User Guide - Monitoring&amp;Troubleshooting</a>.</p>";
  // TODO Make "Data Pipelines" name configurable

  private InternetAddress sender;
  private InternetAddress[] recipients;
  private String subject;
  private String content;
  private List<String> ccEmails;

  public NotificationContent(
      JobConfig jobConfig,
      String stage,
      String status,
      String ownerName,
      String ownerEmail,
      List<String> ccEmails)
      throws AddressException {
    this.sender = new InternetAddress(ownerEmail);
    this.ccEmails = ccEmails;
    // TODO: all recipients are defined in notified_on_job_deploy in the job's ini file for now
    this.recipients = createInternetAddresses(jobConfig.getNotifiedOnJobDeploy());
    this.subject = formatNotificationSubject(stage, status, jobConfig.getJobName());
    this.content = formatNotificationContent(stage, jobConfig.getJobName(), status, "", ownerName);
  }

  public NotificationContent(
      JobConfig jobConfig,
      String stage,
      String status,
      String errName,
      String errBody,
      String ownerName,
      String ownerEmail,
      List<String> ccEmails)
      throws AddressException {
    this.sender = new InternetAddress(ownerEmail);
    this.ccEmails = ccEmails;
    this.recipients = createInternetAddresses(jobConfig.getNotifiedOnJobDeploy());
    this.subject = formatNotificationSubject(stage, status, jobConfig.getJobName());
    String errorContent = formatErrNotificationContent(jobConfig.getJobName(), errName, errBody);
    this.content =
        formatNotificationContent(stage, jobConfig.getJobName(), status, errorContent, ownerName);
  }

  public static String getErrorBody(
      String what, String why, String consequences, String countermeasures) {
    // TODO: might be good idea to convert new lines to html new lines (<br>)
    return String.format(USER_ERROR_TEMPLATE, what, why, consequences, countermeasures);
  }

  public static String getPlatformErrorBody() {
    return getErrorBody(
        "Tried to deploy a data job",
        "There has been a platform error.",
        "Your new/updated job was not deployed. Your job will run its latest successfully deployed"
            + " version (if any) as scheduled.",
        "Try the operation again in a few minutes and open a ticket to the SRE team if the problem"
            + " persists.");
  }

  private InternetAddress[] createInternetAddresses(List<String> recipients)
      throws AddressException {
    List<InternetAddress> ccAddresses = new ArrayList();
    for (String cc : this.ccEmails) {
      ccAddresses.add(new InternetAddress(cc));
    }
    for (String receiver : recipients) {
      ccAddresses.add(new InternetAddress(receiver));
    }
    return ccAddresses.stream().toArray(InternetAddress[]::new);
  }

  String formatNotificationSubject(String stage, String status, String jobName) {
    return String.format(NOTIFICATION_MSG_SUBJECT_TEMPLATE, stage, status, jobName);
  }

  String formatNotificationContent(
      String stage, String status, String jobName, String content, String notificationOwner) {
    return String.format(
        NOTIFICATION_MSG_TEMPLATE, stage, status, jobName, content, notificationOwner);
  }

  String formatErrNotificationContent(String jobName, String errorName, String errorBody) {
    return String.format(GENERAL_ERROR_TEMPLATE, jobName, errorName, errorBody);
  }
}
