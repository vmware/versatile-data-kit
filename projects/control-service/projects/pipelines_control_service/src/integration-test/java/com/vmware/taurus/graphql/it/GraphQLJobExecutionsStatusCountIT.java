/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.graphql.it;

import com.vmware.taurus.ServiceApp;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.deploy.DeploymentService;
import com.vmware.taurus.service.model.*;
import org.hamcrest.core.IsNull;
import org.junit.jupiter.api.*;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;

import java.time.OffsetDateTime;
import java.util.List;

import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;

@SpringBootTest(classes = ServiceApp.class)
@AutoConfigureMockMvc
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class GraphQLJobExecutionsStatusCountIT {

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

    private void addJobExecution(OffsetDateTime endTime, String executionId) {
        var execution = createDataJobExecution(executionId, jobA, ExecutionStatus.FINISHED,
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
    public void testExecutionStatusCountFieldsPresent() throws Exception {
        var expectedEndTimeLarger = OffsetDateTime.now();
        var expectedEndTimeSmaller = OffsetDateTime.now().minusDays(1);

        addJobExecution(expectedEndTimeLarger, "testId");
        addJobExecution(expectedEndTimeSmaller, "testId2");

        mockMvc.perform(MockMvcRequestBuilders.get(uri).queryParam("query", getQuery("ASC")))
                .andExpect(status().is(200))
                .andExpect(content().contentType("application/json"))
                .andExpect(jsonPath("$.data.content[0].deployments[0].successfulExecutions").value(IsNull.nullValue()))
                .andExpect(jsonPath("$.data.content[0].deployments[0].failedExecutions").value(IsNull.nullValue()));

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
