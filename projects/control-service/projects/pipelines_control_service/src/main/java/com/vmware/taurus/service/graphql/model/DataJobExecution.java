package com.vmware.taurus.service.graphql.model;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonValue;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.media.Schema.RequiredMode;
import java.time.OffsetDateTime;
import java.util.Objects;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.format.annotation.DateTimeFormat.ISO;

@Schema(name = "DataJobExecution", description = "Executions of a Data Job")
public class DataJobExecution {
  private String id;
  private String jobName;
  private DataJobExecution.StatusEnum status;
  private DataJobExecution.TypeEnum type;

  @DateTimeFormat(iso = ISO.DATE_TIME)
  private OffsetDateTime startTime;

  @DateTimeFormat(iso = ISO.DATE_TIME)
  private OffsetDateTime endTime;

  private String startedBy;
  private String logsUrl;
  private String message;
  private String opId;
  private DataJobDeployment deployment;

  public DataJobExecution() {}

  public DataJobExecution id(String id) {
    this.id = id;
    return this;
  }

  @Schema(
      name = "id",
      example = "starshot-processing-vmc-fact-daily-2018623174356",
      description = "Data Job Execution ID",
      requiredMode = RequiredMode.NOT_REQUIRED)
  @JsonProperty("id")
  public String getId() {
    return this.id;
  }

  public void setId(String id) {
    this.id = id;
  }

  public DataJobExecution jobName(String jobName) {
    this.jobName = jobName;
    return this;
  }

  @Schema(
      name = "job_name",
      example = "starshot-processing-vmc-fact-daily",
      description = "Data Job name",
      requiredMode = RequiredMode.NOT_REQUIRED)
  @JsonProperty("job_name")
  public String getJobName() {
    return this.jobName;
  }

  public void setJobName(String jobName) {
    this.jobName = jobName;
  }

  public DataJobExecution status(DataJobExecution.StatusEnum status) {
    this.status = status;
    return this;
  }

  @Schema(
      name = "status",
      example = "submitted",
      description = "The current status",
      requiredMode = RequiredMode.NOT_REQUIRED)
  @JsonProperty("status")
  public DataJobExecution.StatusEnum getStatus() {
    return this.status;
  }

  public void setStatus(DataJobExecution.StatusEnum status) {
    this.status = status;
  }

  public DataJobExecution type(DataJobExecution.TypeEnum type) {
    this.type = type;
    return this;
  }

  @Schema(
      name = "type",
      example = "scheduled",
      description = "Execution type - manual or scheduled",
      requiredMode = RequiredMode.NOT_REQUIRED)
  @JsonProperty("type")
  public DataJobExecution.TypeEnum getType() {
    return this.type;
  }

  public void setType(DataJobExecution.TypeEnum type) {
    this.type = type;
  }

  public DataJobExecution startTime(OffsetDateTime startTime) {
    this.startTime = startTime;
    return this;
  }

  @Schema(
      name = "start_time",
      description = "Start of execution",
      requiredMode = RequiredMode.NOT_REQUIRED)
  @JsonProperty("start_time")
  public OffsetDateTime getStartTime() {
    return this.startTime;
  }

  public void setStartTime(OffsetDateTime startTime) {
    this.startTime = startTime;
  }

  public DataJobExecution endTime(OffsetDateTime endTime) {
    this.endTime = endTime;
    return this;
  }

  @Schema(
      name = "end_time",
      description = "Start of execution",
      requiredMode = RequiredMode.NOT_REQUIRED)
  @JsonProperty("end_time")
  public OffsetDateTime getEndTime() {
    return this.endTime;
  }

  public void setEndTime(OffsetDateTime endTime) {
    this.endTime = endTime;
  }

  public DataJobExecution startedBy(String startedBy) {
    this.startedBy = startedBy;
    return this;
  }

  @Schema(
      name = "started_by",
      example = "schedule/runtime",
      description =
          "User or service that started the execution (e.g manual/auserov@example.mail.com or"
              + " scheduled/runtime)",
      requiredMode = RequiredMode.NOT_REQUIRED)
  @JsonProperty("started_by")
  public String getStartedBy() {
    return this.startedBy;
  }

  public void setStartedBy(String startedBy) {
    this.startedBy = startedBy;
  }

  public DataJobExecution logsUrl(String logsUrl) {
    this.logsUrl = logsUrl;
    return this;
  }

  @Schema(
      name = "logs_url",
      example = "http://logs/jobs?filter=job-name",
      description =
          "URL link to persisted logs in central location. Logs generally should be available for"
              + " longer time. The link is available only if operators have configured it during"
              + " installation of Control Service. During install operators can configure logs to"
              + " be persisted to log aggregator service whose link can be exposed here. ",
      requiredMode = RequiredMode.NOT_REQUIRED)
  @JsonProperty("logs_url")
  public String getLogsUrl() {
    return this.logsUrl;
  }

  public void setLogsUrl(String logsUrl) {
    this.logsUrl = logsUrl;
  }

  public DataJobExecution message(String message) {
    this.message = message;
    return this;
  }

  @Schema(
      name = "message",
      description = "Message (usually error) during execution",
      requiredMode = RequiredMode.NOT_REQUIRED)
  @JsonProperty("message")
  public String getMessage() {
    return this.message;
  }

  public void setMessage(String message) {
    this.message = message;
  }

  public DataJobExecution opId(String opId) {
    this.opId = opId;
    return this;
  }

  @Schema(
      name = "op_id",
      description = "Operation id used for tracing calls between different services",
      requiredMode = RequiredMode.NOT_REQUIRED)
  @JsonProperty("op_id")
  public String getOpId() {
    return this.opId;
  }

  public void setOpId(String opId) {
    this.opId = opId;
  }

  public DataJobExecution deployment(DataJobDeployment deployment) {
    this.deployment = deployment;
    return this;
  }

  @Schema(name = "deployment", requiredMode = RequiredMode.NOT_REQUIRED)
  @JsonProperty("deployment")
  public DataJobDeployment getDeployment() {
    return this.deployment;
  }

  public void setDeployment(DataJobDeployment deployment) {
    this.deployment = deployment;
  }

  public boolean equals(Object o) {
    if (this == o) {
      return true;
    } else if (o != null && this.getClass() == o.getClass()) {
      DataJobExecution dataJobExecution = (DataJobExecution) o;
      return Objects.equals(this.id, dataJobExecution.id)
          && Objects.equals(this.jobName, dataJobExecution.jobName)
          && Objects.equals(this.status, dataJobExecution.status)
          && Objects.equals(this.type, dataJobExecution.type)
          && Objects.equals(this.startTime, dataJobExecution.startTime)
          && Objects.equals(this.endTime, dataJobExecution.endTime)
          && Objects.equals(this.startedBy, dataJobExecution.startedBy)
          && Objects.equals(this.logsUrl, dataJobExecution.logsUrl)
          && Objects.equals(this.message, dataJobExecution.message)
          && Objects.equals(this.opId, dataJobExecution.opId)
          && Objects.equals(this.deployment, dataJobExecution.deployment);
    } else {
      return false;
    }
  }

  public int hashCode() {
    return Objects.hash(
        new Object[] {
          this.id,
          this.jobName,
          this.status,
          this.type,
          this.startTime,
          this.endTime,
          this.startedBy,
          this.logsUrl,
          this.message,
          this.opId,
          this.deployment
        });
  }

  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class DataJobExecution {\n");
    sb.append("    id: ").append(this.toIndentedString(this.id)).append("\n");
    sb.append("    jobName: ").append(this.toIndentedString(this.jobName)).append("\n");
    sb.append("    status: ").append(this.toIndentedString(this.status)).append("\n");
    sb.append("    type: ").append(this.toIndentedString(this.type)).append("\n");
    sb.append("    startTime: ").append(this.toIndentedString(this.startTime)).append("\n");
    sb.append("    endTime: ").append(this.toIndentedString(this.endTime)).append("\n");
    sb.append("    startedBy: ").append(this.toIndentedString(this.startedBy)).append("\n");
    sb.append("    logsUrl: ").append(this.toIndentedString(this.logsUrl)).append("\n");
    sb.append("    message: ").append(this.toIndentedString(this.message)).append("\n");
    sb.append("    opId: ").append(this.toIndentedString(this.opId)).append("\n");
    sb.append("    deployment: ").append(this.toIndentedString(this.deployment)).append("\n");
    sb.append("}");
    return sb.toString();
  }

  private String toIndentedString(Object o) {
    return o == null ? "null" : o.toString().replace("\n", "\n    ");
  }

  public static enum StatusEnum {
    SUBMITTED("submitted"),
    RUNNING("running"),
    SUCCEEDED("succeeded"),
    CANCELLED("cancelled"),
    SKIPPED("skipped"),
    USER_ERROR("user_error"),
    PLATFORM_ERROR("platform_error");

    private String value;

    private StatusEnum(String value) {
      this.value = value;
    }

    @JsonValue
    public String getValue() {
      return this.value;
    }

    public String toString() {
      return String.valueOf(this.value);
    }

    @JsonCreator
    public static DataJobExecution.StatusEnum fromValue(String value) {
      DataJobExecution.StatusEnum[] var1 = values();
      int var2 = var1.length;

      for (int var3 = 0; var3 < var2; ++var3) {
        DataJobExecution.StatusEnum b = var1[var3];
        if (b.value.equals(value)) {
          return b;
        }
      }

      throw new IllegalArgumentException("Unexpected value '" + value + "'");
    }
  }

  public static enum TypeEnum {
    MANUAL("manual"),
    SCHEDULED("scheduled");

    private String value;

    private TypeEnum(String value) {
      this.value = value;
    }

    @JsonValue
    public String getValue() {
      return this.value;
    }

    public String toString() {
      return String.valueOf(this.value);
    }

    @JsonCreator
    public static DataJobExecution.TypeEnum fromValue(String value) {
      DataJobExecution.TypeEnum[] var1 = values();
      int var2 = var1.length;

      for (int var3 = 0; var3 < var2; ++var3) {
        DataJobExecution.TypeEnum b = var1[var3];
        if (b.value.equals(value)) {
          return b;
        }
      }

      throw new IllegalArgumentException("Unexpected value '" + value + "'");
    }
  }
}
