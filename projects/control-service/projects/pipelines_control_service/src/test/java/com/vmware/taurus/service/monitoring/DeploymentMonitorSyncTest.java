/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DeploymentStatus;
import com.vmware.taurus.service.model.JobConfig;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.ArrayList;
import java.util.List;

@ExtendWith(MockitoExtension.class)
public class DeploymentMonitorSyncTest {

  @Mock private JobsRepository jobsRepository;

  @Mock private DeploymentMonitor deploymentMonitor;

  @InjectMocks private DeploymentMonitorSync deploymentMonitorSync;

  @Test
  public void testEmptyRepository() throws InterruptedException {
    Iterable<DataJob> mockJobs = new ArrayList<DataJob>();
    Mockito.when(jobsRepository.findAll()).thenReturn(mockJobs);

    deploymentMonitorSync.updateJobDeploymentStatuses();

    Mockito.verify(deploymentMonitor, Mockito.times(0))
        .updateDataJobStatus(Mockito.any(), Mockito.any());
  }

  @Test
  public void testOneJobInRepository() throws InterruptedException {
    List<DataJob> mockJobs = new ArrayList<DataJob>();
    mockJobs.add(new DataJob("test-job", new JobConfig(), DeploymentStatus.SUCCESS));
    Mockito.when(jobsRepository.findAll()).thenReturn(mockJobs);

    deploymentMonitorSync.updateJobDeploymentStatuses();

    Mockito.verify(deploymentMonitor, Mockito.times(1))
        .updateDataJobStatus("test-job", DeploymentStatus.SUCCESS);
  }

  @Test
  public void testTwoJobsInRepository() throws InterruptedException {
    List<DataJob> mockJobs = new ArrayList<DataJob>();
    mockJobs.add(new DataJob("test-job", new JobConfig()));
    mockJobs.add(new DataJob("test-job-2", new JobConfig(), DeploymentStatus.PLATFORM_ERROR));
    Mockito.when(jobsRepository.findAll()).thenReturn(mockJobs);

    deploymentMonitorSync.updateJobDeploymentStatuses();

    Mockito.verify(deploymentMonitor, Mockito.times(0))
        .updateDataJobStatus("test-job", DeploymentStatus.NONE);

    Mockito.verify(deploymentMonitor, Mockito.times(1))
        .updateDataJobStatus("test-job-2", DeploymentStatus.PLATFORM_ERROR);
  }

  @Test
  public void testJobWithNoneStatusSkipped() throws InterruptedException {
    List<DataJob> mockJobs = new ArrayList<DataJob>();
    mockJobs.add(new DataJob("test-job", new JobConfig()));
    Mockito.when(jobsRepository.findAll()).thenReturn(mockJobs);

    deploymentMonitorSync.updateJobDeploymentStatuses();

    Mockito.verify(deploymentMonitor, Mockito.times(0))
        .updateDataJobStatus(Mockito.any(), Mockito.any());
  }

  @Test
  public void testJobWithNullStatusHandled() throws InterruptedException {
    List<DataJob> mockJobs = new ArrayList<DataJob>();
    mockJobs.add(new DataJob("test-job", new JobConfig(), null));
    Mockito.when(jobsRepository.findAll()).thenReturn(mockJobs);

    deploymentMonitorSync.updateJobDeploymentStatuses();

    Mockito.verify(deploymentMonitor, Mockito.times(0))
        .updateDataJobStatus(Mockito.any(), Mockito.any());
  }
}
