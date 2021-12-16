/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.graphql.it;

import com.vmware.taurus.datajobs.it.common.BaseDataJobDeploymentIT;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.model.ExecutionStatus;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;

import java.time.OffsetDateTime;
import java.time.ZoneOffset;

import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.is;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

public class GraphQLDataJobsFieldsIT extends BaseDataJobDeploymentIT {

    private static final String DEFAULT_QUERY_WITH_DEPLOYMENTS =
            "query($filter: [Predicate], $executionOrder: DataJobExecutionOrder, $search: String, $pageNumber: Int, $pageSize: Int) {" +
                    "  jobs(pageNumber: $pageNumber, pageSize: $pageSize, filter: $filter, search: $search) {" +
                    "    content {" +
                    "      jobName" +
                    "      deployments {" +
                    "        id" +
                    "        enabled" +
                    "        lastExecutionStatus" +
                    "        lastExecutionTime" +
                    "        lastExecutionDuration" +
                    "        executions(pageNumber: 1, pageSize: 5, order: $executionOrder) {" +
                    "          id" +
                    "          status" +
                    "        }" +
                    "      }" +
                    "      config {" +
                    "        team" +
                    "        description" +
                    "        schedule {" +
                    "          scheduleCron" +
                    "          nextRunEpochSeconds" +
                    "        }" +
                    "      }" +
                    "    }" +
                    "    totalPages" +
                    "    totalItems" +
                    "  }" +
                    "}";

    @Autowired
    private JobsRepository jobsRepository;

    @Test
    void testFields(String jobName, String teamName, String username) throws Exception {
        var dataJob = jobsRepository.findById(jobName).get();
        dataJob.setLastExecutionStatus(ExecutionStatus.SUCCEEDED);
        dataJob.setLastExecutionEndTime(OffsetDateTime.of(2000, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC));
        dataJob.setLastExecutionDuration(1000);
        dataJob = jobsRepository.save(dataJob);

        // Test requesting of fields that are computed
        mockMvc.perform(get(JOBS_URI)
                        .with(user(username))
                        .param("query", DEFAULT_QUERY_WITH_DEPLOYMENTS)
                        .param("variables", "{" +
                                "\"search\": \"" + jobName + "\"," +
                                "\"pageNumber\": 1," +
                                "\"pageSize\": 10," +
                                "\"executionOrder\": {" +
                                "    \"direction\": \"DESC\"," +
                                "    \"property\": \"status\"" +
                                "  }" +
                                "}")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.content[0].config.team", is(teamName)))
                .andExpect(jsonPath("$.data.content[0].config.schedule.scheduleCron", is(dataJob.getJobConfig().getSchedule())))
                .andExpect(jsonPath("$.data.content[0].config.schedule.nextRunEpochSeconds", greaterThan(1)))
                .andExpect(jsonPath("$.data.content[0].deployments[0].lastExecutionStatus", is(dataJob.getLastExecutionStatus().name())))
                .andExpect(jsonPath("$.data.content[0].deployments[0].lastExecutionTime", isDate(dataJob.getLastExecutionEndTime())))
                .andExpect(jsonPath("$.data.content[0].deployments[0].lastExecutionDuration", is(dataJob.getLastExecutionDuration())))
                .andReturn().getResponse().getContentAsString();
    }
}
