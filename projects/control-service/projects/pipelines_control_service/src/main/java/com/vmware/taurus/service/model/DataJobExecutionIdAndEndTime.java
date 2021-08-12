package com.vmware.taurus.service.model;

import java.time.OffsetDateTime;

public interface DataJobExecutionIdAndEndTime {
    String getId();
    OffsetDateTime getEndTime();
}
