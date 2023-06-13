/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.properties.controller;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.vmware.taurus.controlplane.model.api.DataJobsPropertiesApi;
import com.vmware.taurus.exception.DataJobPropertiesException;
import com.vmware.taurus.properties.service.PropertiesService;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

import java.util.Map;

@RestController
@ComponentScan(basePackages = "com.vmware.taurus.properties")
@Tag(name = "Data Jobs Properties")
public class DataJobsPropertiesController implements DataJobsPropertiesApi {
  static Logger log = LoggerFactory.getLogger(DataJobsPropertiesController.class);

  private final PropertiesService propertiesService;

  public DataJobsPropertiesController(PropertiesService propertiesService) {
    this.propertiesService = propertiesService;
  }

  @Override
  public ResponseEntity<Void> dataJobPropertiesUpdate(
      String teamName, String jobName, String deploymentId, Map<String, Object> requestBody) {
    log.debug("Updating properties for job: {}", jobName);

    propertiesService.updateJobProperties(jobName, requestBody);
    return ResponseEntity.noContent().build();
  }

  @Override
  public ResponseEntity<Map<String, Object>> dataJobPropertiesRead(
      String teamName, String jobName, String deploymentId) {
    log.debug("Reading properties for job: {}", jobName);

    try {
      return ResponseEntity.ok(propertiesService.readJobProperties(jobName));
    } catch (JsonProcessingException e) {
      log.error("Error while parsing properties for job: " + jobName, e);

      throw new DataJobPropertiesException(jobName, "Error while parsing properties.");
    }
  }
}
