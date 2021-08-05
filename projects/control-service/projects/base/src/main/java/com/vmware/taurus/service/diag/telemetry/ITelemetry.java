package com.vmware.taurus.service.diag.telemetry;

public interface ITelemetry {
    /**
     * @param payload json to be sent as payload.
     */
    public void sendAsync(String payload);
}
