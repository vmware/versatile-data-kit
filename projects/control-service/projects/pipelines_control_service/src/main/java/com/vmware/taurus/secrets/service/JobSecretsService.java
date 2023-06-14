/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.secrets.service;

import com.fasterxml.jackson.core.JsonProcessingException;

import java.util.Map;

public interface JobSecretsService {
    void updateJobSecrets(String jobName, Map<String, Object> secrets);

    Map<String, Object> readJobSecrets(String jobName) throws JsonProcessingException;
}
