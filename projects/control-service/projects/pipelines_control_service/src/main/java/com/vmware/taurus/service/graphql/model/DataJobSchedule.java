package com.vmware.taurus.service.graphql.model;


import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.media.Schema.RequiredMode;
import java.util.Objects;

@Schema(
        name = "DataJobSchedule",
        description = "Schedule configuration"
)
public class DataJobSchedule {
    private String scheduleCron;
    

    public DataJobSchedule scheduleCron(String scheduleCron) {
        this.scheduleCron = scheduleCron;
        return this;
    }

    @Schema(
            name = "schedule_cron",
            example = "0 0 13 * 5",
            description = "For format see https://en.wikipedia.org/wiki/Cron<br> The cron expression is evaluated in UTC time. If it is time for a new job run and the previous job run hasn't finished yet, the cron job kills and replaces the currently running job run with a new job run. Jobs configured to run more often than once per hour are not supported and their schedule may be overridden by the platform. To distribute load evenly, Administrators may override the minute you specified. Use https://crontab.guru for help. ",
            requiredMode = RequiredMode.NOT_REQUIRED
    )
    @JsonProperty("schedule_cron")
    public String getScheduleCron() {
        return this.scheduleCron;
    }

    public void setScheduleCron(String scheduleCron) {
        this.scheduleCron = scheduleCron;
    }

    public boolean equals(Object o) {
        if (this == o) {
            return true;
        } else if (o != null && this.getClass() == o.getClass()) {
            DataJobSchedule dataJobSchedule = (DataJobSchedule)o;
            return Objects.equals(this.scheduleCron, dataJobSchedule.scheduleCron);
        } else {
            return false;
        }
    }

    public int hashCode() {
        return Objects.hash(new Object[]{this.scheduleCron});
    }

    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("class DataJobSchedule {\n");
        sb.append("    scheduleCron: ").append(this.toIndentedString(this.scheduleCron)).append("\n");
        sb.append("}");
        return sb.toString();
    }

    private String toIndentedString(Object o) {
        return o == null ? "null" : o.toString().replace("\n", "\n    ");
    }
}

