package com.vmware.taurus.service.graphql.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.media.Schema.RequiredMode;
import java.util.Objects;

@Schema(
        name = "DataJobResources",
        description = "Resource cofiguration of a data Data Job Deployment."
)
public class DataJobResources {
    private Float cpuRequest;
    private Float cpuLimit;
    private Integer memoryRequest;
    private Integer memoryLimit;

    public DataJobResources cpuRequest(Float cpuRequest) {
        this.cpuRequest = cpuRequest;
        return this;
    }

    @Schema(
            name = "cpu_request",
            example = "10",
            description = "Initial CPU shares in deciCores (1 dCore = 0.1 Core = 100 mCores)",
            requiredMode = RequiredMode.NOT_REQUIRED
    )
    @JsonProperty("cpu_request")
    public Float getCpuRequest() {
        return this.cpuRequest;
    }

    public void setCpuRequest(Float cpuRequest) {
        this.cpuRequest = cpuRequest;
    }

    public DataJobResources cpuLimit(Float cpuLimit) {
        this.cpuLimit = cpuLimit;
        return this;
    }

    @Schema(
            name = "cpu_limit",
            example = "20",
            description = "Max CPU shares in deciCores (1 dCore = 0.1 Core = 100 mCores)",
            requiredMode = RequiredMode.NOT_REQUIRED
    )
    @JsonProperty("cpu_limit")
    public Float getCpuLimit() {
        return this.cpuLimit;
    }

    public void setCpuLimit(Float cpuLimit) {
        this.cpuLimit = cpuLimit;
    }

    public DataJobResources memoryRequest(Integer memoryRequest) {
        this.memoryRequest = memoryRequest;
        return this;
    }

    @Schema(
            name = "memory_request",
            example = "1024",
            description = "Initial Memory in MiB.",
            requiredMode = RequiredMode.NOT_REQUIRED
    )
    @JsonProperty("memory_request")
    public Integer getMemoryRequest() {
        return this.memoryRequest;
    }

    public void setMemoryRequest(Integer memoryRequest) {
        this.memoryRequest = memoryRequest;
    }

    public DataJobResources memoryLimit(Integer memoryLimit) {
        this.memoryLimit = memoryLimit;
        return this;
    }

    @Schema(
            name = "memory_limit",
            example = "2048",
            description = "Max Memory in MiB.",
            requiredMode = RequiredMode.NOT_REQUIRED
    )
    @JsonProperty("memory_limit")
    public Integer getMemoryLimit() {
        return this.memoryLimit;
    }

    public void setMemoryLimit(Integer memoryLimit) {
        this.memoryLimit = memoryLimit;
    }

    public boolean equals(Object o) {
        if (this == o) {
            return true;
        } else if (o != null && this.getClass() == o.getClass()) {
            DataJobResources dataJobResources = (DataJobResources)o;
            return Objects.equals(this.cpuRequest, dataJobResources.cpuRequest) && Objects.equals(this.cpuLimit, dataJobResources.cpuLimit) && Objects.equals(this.memoryRequest, dataJobResources.memoryRequest) && Objects.equals(this.memoryLimit, dataJobResources.memoryLimit);
        } else {
            return false;
        }
    }

    public int hashCode() {
        return Objects.hash(new Object[]{this.cpuRequest, this.cpuLimit, this.memoryRequest, this.memoryLimit});
    }

    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("class DataJobResources {\n");
        sb.append("    cpuRequest: ").append(this.toIndentedString(this.cpuRequest)).append("\n");
        sb.append("    cpuLimit: ").append(this.toIndentedString(this.cpuLimit)).append("\n");
        sb.append("    memoryRequest: ").append(this.toIndentedString(this.memoryRequest)).append("\n");
        sb.append("    memoryLimit: ").append(this.toIndentedString(this.memoryLimit)).append("\n");
        sb.append("}");
        return sb.toString();
    }

    private String toIndentedString(Object o) {
        return o == null ? "null" : o.toString().replace("\n", "\n    ");
    }
}

