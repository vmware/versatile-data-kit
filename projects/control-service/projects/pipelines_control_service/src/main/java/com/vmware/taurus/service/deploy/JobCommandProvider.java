/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;

/**
 * This class provides the command list for the K8S' data job container. The command list executes
 * the data job, by calling vdk run ...
 */
@Component
public class JobCommandProvider {
  private List<String> command;

  public JobCommandProvider() {

    this.command =
        List.of(
            "/bin/bash",
            "-c",
            "export PYTHONPATH=$(python -c \"from distutils.sysconfig import get_python_lib;"
                + " print(get_python_lib())\"):/vdk/site-packages/ && /vdk/vdk run");
  }

  private String getJobNameArgument(String jobName) {
    return String.format(" ./%s", jobName);
  }

  private String getExtraArguments(String arguments) {
    return String.format(" --arguments '%s'", arguments);
  }

  public List<String> getJobCommand(String jobName) {

    return List.of(command.get(0), command.get(1), command.get(2) + getJobNameArgument(jobName));
  }

  public List<String> getJobCommand(String jobName, Map<String, Object> extraArguments)
      throws JsonProcessingException {
    var arguments = new ObjectMapper().writeValueAsString(extraArguments);
    return List.of(
        command.get(0),
        command.get(1),
        command.get(2) + getJobNameArgument(jobName) + getExtraArguments(arguments));
  }
}
