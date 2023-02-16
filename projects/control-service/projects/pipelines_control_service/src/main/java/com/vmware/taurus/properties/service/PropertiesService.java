/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.properties.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.json.JSONObject;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@Service
public class PropertiesService {

  private final PropertiesRepository propertiesRepository;
  private final ObjectMapper objectMapper = new ObjectMapper();

  @Autowired
  public PropertiesService(PropertiesRepository propertiesRepository) {
    this.propertiesRepository = propertiesRepository;
  }

  public void updateJobProperties(String jobName, Map<String, Object> properties) {
    var jobProperties =
        propertiesRepository.findByJobName(jobName).orElse(new JobProperties(jobName, null));

    properties =
        properties.entrySet().stream()
            .collect(
                Collectors.toMap(
                    Map.Entry::getKey,
                    entry -> {
                      if (entry.getValue() == null) {
                        entry.setValue(JSONObject.NULL);
                      }
                      return entry.getValue();
                    }));

    jobProperties.setPropertiesJson(new JSONObject(properties).toString());

    propertiesRepository.save(jobProperties);
  }

  public Map<String, Object> readJobProperties(String jobName) throws JsonProcessingException {
    var jobPropertiesJson =
        propertiesRepository
            .findByJobName(jobName)
            .map(JobProperties::getPropertiesJson)
            .orElse(null);

    return jobPropertiesJson == null
        ? Collections.emptyMap()
        : objectMapper.readValue(jobPropertiesJson, Map.class);
  }
}
