/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.model.DataJob;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.ArrayList;
import java.util.List;

@ExtendWith(MockitoExtension.class)
public class DataJobMonitorSyncTest {

  @Mock private JobsRepository jobsRepository;

  @Mock private DataJobMonitor dataJobMonitor;

  @InjectMocks private DataJobMonitorSync dataJobMonitorSync;

  @Test
  public void testUpdateDataJobStatus() {
    List<DataJob> mockJobs = new ArrayList<>();
    Mockito.when(jobsRepository.findAll()).thenReturn(mockJobs);

    dataJobMonitorSync.updateDataJobStatus();

    var dataJobsCaptor = ArgumentCaptor.forClass(Iterable.class);
    Mockito.verify(dataJobMonitor, Mockito.times(1)).updateDataJobsGauges(dataJobsCaptor.capture());

    Assertions.assertEquals(dataJobsCaptor.getValue(), mockJobs);
  }
}
