/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.vmware.taurus.controlplane.model.api.DataJobsSourcesApi;
import com.vmware.taurus.controlplane.model.data.DataJobVersion;
import com.vmware.taurus.exception.ExternalSystemError;
import com.vmware.taurus.service.JobsService;
import com.vmware.taurus.service.upload.JobUpload;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.Resource;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;

import java.util.Optional;

/**
 * REST controller for operations on data jobs source folders
 *
 * <p>REST behaviour and response codes should follow guidelines at
 *
 * <p>The controller may throw exception which will be handled by {@link
 * com.vmware.taurus.exception.ExceptionControllerAdvice}. The advice class logs error so no need to
 * log them here.
 *
 * <p>Wrap {@link org.springframework.dao.DataAccessException} from JobsService in {@link
 * ExternalSystemError} either here or in the service itself.
 */
@RestController
@AllArgsConstructor
@NoArgsConstructor
@Tag(name = "Data Jobs Sources")
public class DataJobsSourcesController implements DataJobsSourcesApi {
  @Autowired private JobsService jobsService;

  @Autowired private JobUpload jobUpload;

  @Override
  public ResponseEntity<Void> sourcesDelete(String teamName, String jobName, String reason) {
    if (jobsService.jobWithTeamExists(jobName, teamName)) {
      jobUpload.deleteDataJob(jobName, reason);
      return ResponseEntity.ok().build();
    }
    return ResponseEntity.notFound().build();
  }

  @Override
  public ResponseEntity<DataJobVersion> sourcesUpload(
      String teamName, String jobName, Resource resource, String reason) {
    if (jobsService.jobWithTeamExists(jobName, teamName)) {
      DataJobVersion jobVersion = new DataJobVersion();
      jobVersion.setVersionSha(jobUpload.publishDataJob(jobName, resource, reason));
      return ResponseEntity.ok(jobVersion);
    }
    return ResponseEntity.notFound().build();
  }

  public ResponseEntity<Resource> dataJobSourcesDownload(String teamName, String jobName) {
    if (jobsService.jobWithTeamExists(jobName, teamName)) {
      Optional<Resource> jobSource = jobUpload.getDataJob(jobName);
      if (jobSource.isPresent()) {
        return ResponseEntity.ok(jobSource.get());
      }
    }
    return ResponseEntity.notFound().build();
  }
}
