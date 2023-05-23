/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.properties;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.vmware.taurus.properties.controller.DataJobsPropertiesController;
import com.vmware.taurus.properties.service.PropertiesService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.server.ResponseStatusException;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.*;

class DataJobsPropertiesControllerTest {

    @Mock
    private PropertiesService propertiesService;

    @InjectMocks
    private DataJobsPropertiesController controller;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    void testDataJobPropertiesUpdate() {
        String jobName = "testJob";
        Map<String, Object> requestBody = new HashMap<>();

        ResponseEntity<Void> expectedResponse = ResponseEntity.noContent().build();

        doNothing().when(propertiesService).updateJobProperties(jobName, requestBody);

        ResponseEntity<Void> actualResponse =
                controller.dataJobPropertiesUpdate(null, jobName, null, requestBody);

        verify(propertiesService, times(1)).updateJobProperties(jobName, requestBody);

        assertEquals(expectedResponse.getStatusCode(), actualResponse.getStatusCode());
    }

    @Test
    void testDataJobPropertiesRead() throws JsonProcessingException {
        String jobName = "testJob";
        Map<String, Object> expectedProperties = new HashMap<>();

        when(propertiesService.readJobProperties(jobName)).thenReturn(expectedProperties);

        ResponseEntity<Map<String, Object>> expectedResponse = ResponseEntity.ok(expectedProperties);

        ResponseEntity<Map<String, Object>> actualResponse =
                controller.dataJobPropertiesRead(null, jobName, null);

        verify(propertiesService, times(1)).readJobProperties(jobName);

        assertEquals(expectedResponse.getStatusCode(), actualResponse.getStatusCode());
        assertEquals(expectedResponse.getBody(), actualResponse.getBody());
    }

    @Test
    void testDataJobPropertiesRead_JsonProcessingException() throws JsonProcessingException {
        String jobName = "testJob";

        when(propertiesService.readJobProperties(jobName)).thenThrow(JsonProcessingException.class);

        ResponseEntity<Map<String, Object>> expectedResponse =
                ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                        .body(null);

        ResponseStatusException thrownException =
                org.junit.jupiter.api.Assertions.assertThrows(
                        ResponseStatusException.class,
                        () -> controller.dataJobPropertiesRead(null, jobName, null));

        verify(propertiesService, times(1)).readJobProperties(jobName);

        assertEquals(expectedResponse.getStatusCode(), thrownException.getStatus());
    }
}
