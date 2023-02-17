/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.vmware.taurus.controlplane.model.api.DataJobsApi;
import com.vmware.taurus.controlplane.model.data.DataJob;
import com.vmware.taurus.controlplane.model.data.DataJobQueryResponse;
import com.vmware.taurus.exception.ApiConstraintError;
import com.vmware.taurus.exception.ExternalSystemError;
import com.vmware.taurus.exception.WebHookRequestError;
import com.vmware.taurus.service.GraphQLJobsQueryService;
import com.vmware.taurus.service.JobOperationResult;
import com.vmware.taurus.service.JobsService;
import com.vmware.taurus.service.credentials.JobCredentialsService;
import com.vmware.taurus.service.upload.JobUpload;
import graphql.GraphQLError;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;
import org.springframework.web.util.UriBuilder;

import java.net.URI;
import java.util.List;
import java.util.function.Supplier;

/**
 * REST controller for operations on data jobs
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
@Tag(name = "Data Jobs")
public class DataJobsController implements DataJobsApi {
  static Logger log = LoggerFactory.getLogger(DataJobsController.class);

  @Autowired private JobsService jobsService;

  @Autowired private JobCredentialsService jobCredentialsService;

  @Autowired private JobUpload jobUpload;

  @Autowired private GraphQLJobsQueryService graphQLService;

  // modified in unit tests
  private Supplier<UriBuilder> currentContextPathBuilderSupplier =
      ServletUriComponentsBuilder::fromCurrentContextPath;

  @Override
  public ResponseEntity<Void> dataJobCreate(String teamName, DataJob dataJob, String jobName) {
    if (dataJob.getJobName() == null) {
      throw new ApiConstraintError(
          "dataJob.jobName", "missing or malformed data job name", dataJob.getJobName());
    } else if (!dataJob.getJobName().matches("^[a-z][a-z0-9-]{5,49}$")) {
      throw new ApiConstraintError(
          "dataJob.jobName",
          "starting with lowercase letter, only lowercase alphanumeric characters or dash and"
              + " between 6 and 50 characters",
          dataJob.getJobName());
    }

    if (StringUtils.isNotBlank(jobName) && !jobName.equals(dataJob.getJobName())) {
      throw new ApiConstraintError(
          "dataJob.jobName",
          "the same as the name in the request URL query parameter",
          dataJob.getJobName());
    }

    if (StringUtils.isBlank(teamName)) {
      throw new ApiConstraintError("team", "in path should not be blank", dataJob.getTeam());
    } else if (StringUtils.isNotBlank(teamName) && dataJob.getTeam() == null) {
      dataJob.setTeam(teamName);
    } else if (StringUtils.isNotBlank(teamName) && !teamName.equals(dataJob.getTeam())) {
      throw new ApiConstraintError(
          "dataJob.team",
          "the same as the team name in the request URL query parameter",
          dataJob.getTeam());
    }

    var apiJob = ToModelApiConverter.toDataJob(dataJob);
    var operationResult = jobsService.createJob(apiJob);
    if (webHookResultExists(operationResult)) {
      propagateWebHookResult("Create", operationResult);
    }
    if (operationResult.isCompleted()) {
      String contextPath =
          String.format("/data-jobs/for-team/%s/jobs/%s", dataJob.getTeam(), dataJob.getJobName());
      URI location = currentContextPathBuilderSupplier.get().path(contextPath).build();
      return ResponseEntity.created(location).build();
    } else {
      // Mob consensus is for responding 409 Conflict when creating with existing ID:
      // https://stackoverflow.com/questions/3825990/http-response-code-for-post-when-resource-already-exists
      return ResponseEntity.status(HttpStatus.CONFLICT).build();
    }
  }

  @Override
  public ResponseEntity<Void> dataJobDelete(String teamName, String jobName) {
    if (jobsService.jobWithTeamExists(jobName, teamName)) {
      var operationResult = jobsService.deleteJob(jobName);
      jobUpload.deleteDataJob(
          jobName,
          String.format("Source deleted automatically upon a data job: %s deletion", jobName));
      if (webHookResultExists(operationResult)) {
        return propagateWebHookResult("Delete", operationResult);
      }
      if (operationResult.isCompleted()) {
        return ResponseEntity.ok().build();
      }
      return ResponseEntity.notFound().build();
    }
    return ResponseEntity.notFound().build();
  }

  @Override
  public ResponseEntity<Resource> dataJobKeytabDownload(String teamName, String jobName) {
    if (jobsService.jobWithTeamExists(jobName, teamName)) {
      byte[] keytab = jobCredentialsService.readJobCredential(jobName);
      if (keytab != null) {
        return ResponseEntity.ok(new ByteArrayResource(keytab));
      }
    }
    return ResponseEntity.notFound().build();
  }

  @Override
  public ResponseEntity<DataJob> dataJobRead(String teamName, String jobName) {
    if (jobsService.jobWithTeamExists(jobName, teamName)) {
      var job = jobsService.getByName(jobName.toLowerCase());
      if (job.isPresent()) {
        return ResponseEntity.ok(ToApiModelConverter.toDataJob(job.get()));
      }
    }
    return ResponseEntity.notFound().build();
  }

  @Override
  public ResponseEntity<Void> dataJobTeamUpdate(
      String teamName, String newTeamName, String jobName) {
    if (jobsService.jobWithTeamExists(jobName, teamName)) {
      if (StringUtils.isNotBlank(newTeamName)) {
        var job = jobsService.getByName(jobName.toLowerCase());
        if (job.isPresent()) {
          job.get().getJobConfig().setTeam(newTeamName);
          jobsService.updateJob(job.get());
          return ResponseEntity.ok().build();
        } else {
          return ResponseEntity.notFound().build();
        }
      }
    }
    return ResponseEntity.notFound().build();
  }

  @Override
  public ResponseEntity<Void> dataJobUpdate(String teamName, String jobName, DataJob dataJob) {
    if (jobsService.jobWithTeamExists(jobName, teamName)) {
      // TODO: maybe we can remove job name form PUT request body (thus eliminating the chance of an
      // error).
      if (!jobName.equals(dataJob.getJobName())) {
        throw new ApiConstraintError(
            "dataJob.jobName", "the same as the name in the PUT request URL", dataJob.getJobName());
      }
      var existingJob = jobsService.getByName(jobName.toLowerCase());
      if (existingJob.isPresent()) {
        if (dataJob.getTeam() != null) {
          if (!existingJob.get().getJobConfig().getTeam().equals(dataJob.getTeam())) {
            throw new ApiConstraintError(
                "dataJob.team",
                " '"
                    + existingJob.get().getJobConfig().getTeam()
                    + "' as the team of an existing job cannot be changed through this API",
                dataJob.getTeam(),
                "set the team to the correct value, "
                    + "or if you want to change the job's team, use the UpdateJobTeam API.");
          }
        }
        dataJob.setTeam(teamName);
        jobsService.updateJob(ToModelApiConverter.toDataJob(dataJob));
        return ResponseEntity.ok().build();
      } else {
        return ResponseEntity.notFound().build();
      }
    }
    return ResponseEntity.notFound().build();
  }

  @Override
  public ResponseEntity<DataJobQueryResponse> jobsQuery(
      String teamName, String query, String operationName, String variables) {
    if (query == null) {
      query = GraphQLJobsQueryService.DEFAULT_QUERY;
    }

    var executionResult =
        graphQLService.executeRequest(
            query, operationName, graphQLService.convertVariablesJson(variables));
    var dataJobQueryResponse = ToApiModelConverter.toDataJobPage(executionResult);

    return buildGraphQLResponseEntity(dataJobQueryResponse);
  }

  private boolean webHookResultExists(JobOperationResult operationResult) {
    return operationResult.getWebHookResult() != null;
  }

  private ResponseEntity<Void> propagateWebHookResult(
      String operationName, JobOperationResult operationResult) {
    throw new WebHookRequestError(
        operationName,
        operationResult.getWebHookResult().getMessage(),
        operationResult.getWebHookResult().getStatus());
  }

  private static ResponseEntity<DataJobQueryResponse> buildGraphQLResponseEntity(
      DataJobQueryResponse dataJobQueryResponse) {
    if (dataJobQueryResponse == null) {
      return ResponseEntity.badRequest().body(new DataJobQueryResponse());
    }
    List<Object> errors = dataJobQueryResponse.getErrors();
    return (errors != null && errors.stream().anyMatch(GraphQLError.class::isInstance))
        ? ResponseEntity.badRequest().body(dataJobQueryResponse)
        : ResponseEntity.ok(dataJobQueryResponse);
  }
}
