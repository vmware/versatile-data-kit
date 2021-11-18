/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.graphql.it;

import com.vmware.taurus.ServiceApp;
import com.vmware.taurus.datajobs.it.common.BaseDataJobDeploymentIT;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.deploy.DeploymentService;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobExecution;
import com.vmware.taurus.service.model.DeploymentStatus;
import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.ExecutionType;
import com.vmware.taurus.service.model.JobConfig;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;

import java.time.OffsetDateTime;
import java.util.List;

import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(classes = ServiceApp.class)
@AutoConfigureMockMvc
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class GraphQLJobExecutionsStatusCountIT extends BaseDataJobDeploymentIT {

    @MockBean
    DeploymentService deploymentService;

    @Autowired
    MockMvc mockMvc;

    @Autowired
    JobExecutionRepository jobExecutionRepository;

    @Autowired
    JobsRepository jobsRepository;

    private DataJob jobA;
    private final String uri = "/data-jobs/for-team/supercollider/jobs";

    @BeforeEach
    private void setUpJobsAndDeployments() {
        var depl = new JobDeploymentStatus();
        depl.setDataJobName("jobA");
        depl.setEnabled(true);
        depl.setLastDeployedBy("Me");
        depl.setLastDeployedDate("today");
        depl.setMode("testing");
        depl.setGitCommitSha("1234asdasd");
        depl.setImageName("imgname");
        depl.setCronJobName("jobA-cron");
        Mockito.when(deploymentService.readDeployments()).thenReturn(List.of(depl));
        JobConfig config = new JobConfig();
        config.setSchedule("schedule");
        jobA = new DataJob("jobA", config);
        jobA.setLatestJobDeploymentStatus(DeploymentStatus.SUCCESS);
        jobsRepository.save(jobA);
    }

    @AfterEach
    public void cleanup() {
        jobsRepository.deleteAll();
        jobExecutionRepository.deleteAll();
    }

    private void addJobExecution(OffsetDateTime endTime, String executionId, ExecutionStatus executionStatus) {
        var execution = createDataJobExecution(executionId, jobA, executionStatus,
                "message", OffsetDateTime.now());
        execution.setEndTime(endTime);
        jobExecutionRepository.save(execution);
    }

    private String getQuery(String sortOrder) {
        return "{\n" +
                "  jobs(pageNumber: 1, pageSize: 100, filter: [{property: \"jobName\", sort: ASC}]) {\n" +
                "    content {\n" +
                "      jobName\n" +
                "      deployments {\n" +
                "successfulExecutions\n " +
                "failedExecutions\n " +
                "      }\n" +
                "    }\n" +
                "  }\n" +
                "}";
    }

    @Test
    public void testExecutionStatusCount_expectTwoSuccessful() throws Exception {
        var expectedEndTimeLarger = OffsetDateTime.now();
        var expectedEndTimeSmaller = OffsetDateTime.now().minusDays(1);

        addJobExecution(expectedEndTimeLarger, "testId", ExecutionStatus.FINISHED);
        addJobExecution(expectedEndTimeSmaller, "testId2", ExecutionStatus.FINISHED);

        mockMvc.perform(MockMvcRequestBuilders.get(uri).queryParam("query", getQuery("ASC")))
                .andExpect(status().is(200))
                .andExpect(content().contentType("application/json"))
                .andExpect(jsonPath("$.data.content[0].deployments[0].successfulExecutions").value(2))
                .andExpect(jsonPath("$.data.content[0].deployments[0].failedExecutions").value(0));

    }

    @Test
    public void testExecutionStatusCount_expectNoCounts() throws Exception {
        mockMvc.perform(MockMvcRequestBuilders.get(uri).queryParam("query", getQuery("ASC")))
                .andExpect(status().is(200))
                .andExpect(content().contentType("application/json"))
                .andExpect(jsonPath("$.data.content[0].deployments[0].successfulExecutions").value(0))
                .andExpect(jsonPath("$.data.content[0].deployments[0].failedExecutions").value(0));
    }

    @Test
    public void testExecutionStatusCount_expectTwoSuccessfulTwoFailed() throws Exception {
        var expectedEndTimeLarger = OffsetDateTime.now();
        var expectedEndTimeSmaller = OffsetDateTime.now().minusDays(1);

        addJobExecution(expectedEndTimeLarger, "testId", ExecutionStatus.FINISHED);
        addJobExecution(expectedEndTimeSmaller, "testId2", ExecutionStatus.FINISHED);
        addJobExecution(expectedEndTimeLarger, "testI3", ExecutionStatus.FAILED);
        addJobExecution(expectedEndTimeSmaller, "testId4", ExecutionStatus.FAILED);

        mockMvc.perform(MockMvcRequestBuilders.get(uri).queryParam("query", getQuery("ASC")))
                .andExpect(status().is(200))
                .andExpect(content().contentType("application/json"))
                .andExpect(jsonPath("$.data.content[0].deployments[0].successfulExecutions").value(2))
                .andExpect(jsonPath("$.data.content[0].deployments[0].failedExecutions").value(2));

    }

    @Test
    public void testExecutionStatusCount_expectOneSuccessfulOneFailed() throws Exception {
        var expectedEndTimeLarger = OffsetDateTime.now();
        var expectedEndTimeSmaller = OffsetDateTime.now().minusDays(1);

        addJobExecution(expectedEndTimeLarger, "testId", ExecutionStatus.FINISHED);
        addJobExecution(expectedEndTimeLarger, "testI3", ExecutionStatus.FAILED);

        mockMvc.perform(MockMvcRequestBuilders.get(uri).queryParam("query", getQuery("ASC")))
                .andExpect(status().is(200))
                .andExpect(content().contentType("application/json"))
                .andExpect(jsonPath("$.data.content[0].deployments[0].successfulExecutions").value(1))
                .andExpect(jsonPath("$.data.content[0].deployments[0].failedExecutions").value(1));

    }

    private DataJobExecution createDataJobExecution(
            String executionId,
            DataJob dataJob,
            ExecutionStatus executionStatus,
            String message,
            OffsetDateTime startTime) {

        var jobExecution = DataJobExecution.builder()
                .id(executionId)
                .dataJob(dataJob)
                .startTime(startTime)
                .type(ExecutionType.MANUAL)
                .status(executionStatus)
                .resourcesCpuRequest(1F)
                .resourcesCpuLimit(2F)
                .resourcesMemoryRequest(500)
                .resourcesMemoryLimit(1000)
                .message(message)
                .lastDeployedBy("test_user")
                .lastDeployedDate(OffsetDateTime.now())
                .jobVersion("test_version")
                .jobSchedule("*/5 * * * *")
                .opId("test_op_id")
                .vdkVersion("test_vdk_version")
                .build();

        return jobExecution;
    }
}
