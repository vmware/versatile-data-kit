/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.properties;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.properties.service.JobProperties;
import com.vmware.taurus.properties.service.PropertiesRepository;
import com.vmware.taurus.properties.service.PropertiesService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;

@ExtendWith(SpringExtension.class)
@SpringBootTest(classes = ControlplaneApplication.class)
class PropertiesServiceTest {

    @Autowired
    private PropertiesRepository propertiesRepository;

    @Autowired
    private PropertiesService propertiesService;

    @BeforeEach
    void setUp() {
        propertiesRepository.deleteAll();
        String jobName = "testJob";
        var intialProperties = new JobProperties(jobName, "{\"key2\":\"value2\",\"key1\":123}");
        propertiesRepository.save(intialProperties);
        this.propertiesService = new PropertiesService(propertiesRepository);
    }

    @Test
    void testUpdateJobProperties() throws JsonProcessingException {
        String jobName = "testJob";
        Map<String, Object> properties = new HashMap<>();
        properties.put("key1", "value1");
        properties.put("key2", 123);
        properties.put("key3", true);
        properties.put("key4", null);

        Map<String, Object> initial = propertiesService.readJobProperties(jobName);
        assertNotEquals(properties, initial);

        propertiesService.updateJobProperties(jobName, properties);
        Map<String, Object> result = propertiesService.readJobProperties(jobName);

        assertEquals(properties, result);
    }

    @Test
    void testReadJobProperties() throws JsonProcessingException {
        String jobName = "testJob";
        Map<String, Object> expectedProperties = new HashMap<>();
        expectedProperties.put("key2", "value2");
        expectedProperties.put("key1", 123);

        Map<String, Object> actualProperties = propertiesService.readJobProperties(jobName);

        assertEquals(expectedProperties, actualProperties);
    }

    @Test
    void testReadEmptyJobProperties() throws JsonProcessingException {
        String jobName = "testJob1";
        Map<String, Object> actualProperties = propertiesService.readJobProperties(jobName);
        assertEquals(actualProperties, Collections.emptyMap());
    }
}
