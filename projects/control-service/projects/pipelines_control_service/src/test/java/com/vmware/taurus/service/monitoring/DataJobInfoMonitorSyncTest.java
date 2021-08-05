/*
 * Copyright (c) 2021 VMware, Inc.
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
import java.util.function.Supplier;

@ExtendWith(MockitoExtension.class)
public class DataJobInfoMonitorSyncTest {

   @Mock
   private JobsRepository jobsRepository;

   @Mock
   private DataJobInfoMonitor dataJobInfoMonitor;

   @InjectMocks
   private DataJobInfoMonitorSync dataJobInfoMonitorSync;

   @Test
   public void testUpdateDataJobInfo() {
      List<DataJob> mockJobs = new ArrayList<>();
      Mockito.when(jobsRepository.findAll()).thenReturn(mockJobs);

      dataJobInfoMonitorSync.updateDataJobInfo();

      var dataJobsCaptor = ArgumentCaptor.forClass(Supplier.class);
      Mockito.verify(dataJobInfoMonitor, Mockito.times(1)).updateDataJobsInfo(dataJobsCaptor.capture());

      Assertions.assertEquals(dataJobsCaptor.getValue().get(), mockJobs);
   }
}
