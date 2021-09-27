/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import java.util.List;

/**
 * This class provides the command list for the K8S' data job
 * container. The command list executes the data job, by calling
 * vdk run ...
 */
public class JobCommandProvider {
    private List<String> command;

    public JobCommandProvider(String jobName) {
        this.command = List.of(
                "/bin/bash",
                "-c",
                String.format("export PYTHONPATH=/usr/local/lib/python3.7/site-packages:/vdk/site-packages/ && /vdk/vdk run ./%s", jobName)
        );
    }

    public List<String> getJobCommand() {
        return command;
    }

    public List<String> getJobCommand(String extraArguments) {
        return List.of(
                command.get(0),
                command.get(1),
                command.get(2) + String.format(" --arguments '%s'", extraArguments)
        );
    }
}
