/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.notification;

import org.junit.Test;

public class DataJobNotificationTest {

    @Test
    public void SendEmailsManualTest() {
        /** Integration test with which you can send yourself some emails
         *
         * Uncomment and fill with your @vmware email
         *
         *

         JobConfig jobConfig = new JobConfig();
         List receivers = new ArrayList();
         receivers.add("your_username@vmware.com");
         jobConfig.setNotifiedOnJobDeploy(receivers);
         jobConfig.setJobName("test_job");

         DataJobNotification dataJobNotification =
                 new DataJobNotification(new EmailNotification(),"Example Name","your_username@vmware.com");
         dataJobNotification.notifyJobDeployFailure(jobConfig);
         dataJobNotification.notifyJobDeploySuccess(jobConfig);
         dataJobNotification.notifyJobDeployError(jobConfig, "Some error", "Some error body");

         */
    }
}
