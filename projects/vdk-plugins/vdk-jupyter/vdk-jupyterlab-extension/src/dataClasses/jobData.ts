/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import data from "./jobDataModel.json";

export var jobData = JSON.parse(JSON.stringify(data));

export function revertJobDataToDefault(){
    jobData = JSON.parse(JSON.stringify(data));
}
