/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.gpu;

import com.vmware.taurus.gpu.jpa.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

import com.google.ortools.linearsolver.MPConstraint;
import com.google.ortools.linearsolver.MPObjective;
import com.google.ortools.linearsolver.MPSolver;
import com.google.ortools.linearsolver.MPVariable;


public interface GpuResourceManager {

    void jobEnded(String jobName, String teamName);

    public List<JobAction> tryProvisionResources(String teamName,String jobName,float amount);

}
