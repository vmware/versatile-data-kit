/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { CollectionsUtil } from '../../utils';

const TASK_IDENTIFIER_SEPARATOR = ' __ ';
const TASK_IDENTIFIER_TEMPLATE = `%s${TASK_IDENTIFIER_SEPARATOR}%s`;

/**
 * ** Factory for Tasks identifiers.
 */
export const createTaskIdentifier = (task: string) => {
    if (CollectionsUtil.isString(task)) {
        return CollectionsUtil.interpolateString(TASK_IDENTIFIER_TEMPLATE, task, CollectionsUtil.dateISO());
    }

    return undefined;
};

/**
 * ** Extract Task from Tasks identifiers.
 */
export const extractTaskFromIdentifier = <T extends string = string>(taskIdentifier: string) => {
    if (CollectionsUtil.isString(taskIdentifier)) {
        return taskIdentifier.split(TASK_IDENTIFIER_SEPARATOR)[0] as T;
    }

    return null;
};
