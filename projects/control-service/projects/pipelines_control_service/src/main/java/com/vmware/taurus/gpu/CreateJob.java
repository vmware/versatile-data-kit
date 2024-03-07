package com.vmware.taurus.gpu;

public final class CreateJob extends JobAction {
    private final String nodeName;
    private final String jobName;

    public CreateJob(String nodeName, String jobName) {
        this.nodeName = nodeName;
        this.jobName = jobName;
    }
}
