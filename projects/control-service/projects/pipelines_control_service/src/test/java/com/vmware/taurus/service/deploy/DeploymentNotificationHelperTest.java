/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.model.DeploymentStatus;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.JobConfig;
import com.vmware.taurus.service.model.JobDeployment;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;
import com.vmware.taurus.service.notification.NotificationContent;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import java.io.IOException;

import static org.mockito.Mockito.*;

@ExtendWith(SpringExtension.class)
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class DeploymentNotificationHelperTest {
  private static final String TEST_JOB_NAME = "test-job-name";
  private static final String TEST_JOB_SCHEDULE = "*/5 * * * *";
  private static final String TEST_DB_DEFAULT_TYPE = "IMPALA";
  private static final String TEST_BUILDER_JOB_NAME = "builder-test-job-name";

  @Autowired private DeploymentNotificationHelper deploymentNotificationHelper;

  @MockBean private DeploymentProgress deploymentProgress;

  @Test
  public void deploymentNotificationHelper_fail_userError() throws IOException {
    JobConfig jobConfig = new JobConfig();
    jobConfig.setDbDefaultType(TEST_DB_DEFAULT_TYPE);
    jobConfig.setSchedule(TEST_JOB_SCHEDULE);
    jobConfig.setTeam("test-team");

    DataJob testDataJob = new DataJob();
    testDataJob.setName(TEST_JOB_NAME);
    testDataJob.setJobConfig(jobConfig);

    JobDeployment testJobDeployment = new JobDeployment();
    testJobDeployment.setDataJobName(TEST_JOB_NAME);
    testJobDeployment.setGitCommitSha("test-git-commit-sha");

    KubernetesService.JobStatusCondition testCondition =
        new KubernetesService.JobStatusCondition(false, "type", "user-error", "some-message", 0);

    final String BUILDER_JOB_LOGS =
        "INFO[0007] ARG requirements_file=requirements.txt       \n"
            + "INFO[0007] RUN if [ -f \"$job_name/$requirements_file\" ]; then pip3 install"
            + " --disable-pip-version-check -q -r \"$job_name/$requirements_file\" || ( echo"
            + " \">requirements_failed<\" && exit 1 ) ; fi \n"
            + "INFO[0007] cmd: /bin/sh                                 \n"
            + "INFO[0007] args: [-c if [ -f \"$job_name/$requirements_file\" ]; then pip3 install"
            + " --disable-pip-version-check -q -r \"$job_name/$requirements_file\" || ( echo"
            + " \">requirements_failed<\" && exit 1 ) ; fi] \n"
            + "INFO[0007] Running: [/bin/sh -c if [ -f \"$job_name/$requirements_file\" ]; then"
            + " pip3 install --disable-pip-version-check -q -r \"$job_name/$requirements_file\" ||"
            + " ( echo \">requirements_failed<\" && exit 1 ) ; fi] \n"
            + "ERROR: Invalid requirement: 'sqlite=\"broken\"' (from line 4 of"
            + " aa-test-job/requirements.txt)\n"
            + "Hint: = is not a valid operator. Did you mean == ?\n"
            + ">requirements_failed<\n"
            + "error building image: error building stage: failed to execute command: waiting for"
            + " process to exit: exit status 1";

    final String requirementsError =
        "\" && exit 1 ) ; fi] \n"
            + "ERROR: Invalid requirement: 'sqlite=\"broken\"' (from line 4 of"
            + " aa-test-job/requirements.txt)\n"
            + "Hint: = is not a valid operator. Did you mean == ?\n";

    String errorMessage =
        NotificationContent.getErrorBody(
            "Tried to deploy a data job",
            "There has been an error while processing your requirements file: " + requirementsError,
            "Your new/updated job was not deployed. Your job will run its latest successfully"
                + " deployed version (if any) as scheduled.",
            "Please fix the requirements file");

    deploymentNotificationHelper.verifyBuilderResult(
        TEST_BUILDER_JOB_NAME,
        testDataJob,
        testJobDeployment,
        testCondition,
        BUILDER_JOB_LOGS,
        true);

    verify(deploymentProgress)
        .failed(
            testDataJob.getJobConfig(),
            testJobDeployment,
            DeploymentStatus.USER_ERROR,
            errorMessage,
            true);
  }
}
