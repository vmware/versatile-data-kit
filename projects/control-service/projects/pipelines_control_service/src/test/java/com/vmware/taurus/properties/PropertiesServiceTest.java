/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.properties;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.vmware.taurus.properties.service.JobProperties;
import com.vmware.taurus.properties.service.PropertiesRepository;
import com.vmware.taurus.properties.service.PropertiesService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.*;


@ExtendWith(MockitoExtension.class)
class PropertiesServiceTest {

    @Mock
    private PropertiesRepository propertiesRepository;

    private PropertiesService propertiesService;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        this.propertiesService = new PropertiesService(propertiesRepository);
    }


    @Test
    void testUpdateJobProperties() {
        String jobName = "testJob";
        Map<String, Object> properties = new HashMap<>();
        properties.put("key1", "value1");
        properties.put("key2", 123);
        properties.put("key3", true);
        properties.put("key4", null);

        var existingProperties = new JobProperties(jobName, "{\"key2\":\"value2\",\"key1\":123}");

        JobProperties expectedjobProperties = new JobProperties(jobName, "{\"key1\":\"value1\",\"key2\":123,\"key3\":true,\"key4\":null}");


        when(propertiesRepository.findByJobName(jobName)).thenReturn(Optional.of(existingProperties));
        when(propertiesRepository.save(expectedjobProperties)).thenReturn(expectedjobProperties);

        propertiesService.updateJobProperties(jobName, properties);

        verify(propertiesRepository, times(1)).findByJobName(jobName);
        verify(propertiesRepository, times(1)).save(existingProperties);

        assertEquals("{\"key1\":\"value1\",\"key2\":123,\"key3\":true,\"key4\":null}", existingProperties.getPropertiesJson());
    }

    @Test
    void testReadJobProperties() throws JsonProcessingException {
        String jobName = "testJob";
        String propertiesJson = "{\"key1\":\"value1\",\"key2\":123}";

        JobProperties jobProperties = new JobProperties(jobName, propertiesJson);

        when(propertiesRepository.findByJobName(jobName)).thenReturn(Optional.of(jobProperties));

        Map<String, Object> expectedProperties = new HashMap<>();
        expectedProperties.put("key1", "value1");
        expectedProperties.put("key2", 123);

        Map<String, Object> actualProperties = propertiesService.readJobProperties(jobName);

        verify(propertiesRepository, times(1)).findByJobName(jobName);

        assertEquals(expectedProperties, actualProperties);
    }

    @Test
    void testReadEmptyJobProperties() throws JsonProcessingException {
        String jobName = "testJob";

        when(propertiesRepository.findByJobName(jobName)).thenReturn(Optional.empty());

        Map<String, Object> actualProperties = propertiesService.readJobProperties(jobName);

        verify(propertiesRepository, times(1)).findByJobName(jobName);

        assertEquals(actualProperties, Collections.emptyMap());
    }
}
