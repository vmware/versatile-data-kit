/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/no-explicit-any */

import { Expression } from '../../../../common';

import { SystemEvent } from '../../event';

export type SystemEventMetadataRecord = {
    handler: SystemEventHandlerRef;
    events: SystemEvent | SystemEvent[];
    filterExpression: Expression;
};

/**
 * ** Type for one Handler interface.
 */
export type SystemEventHandlerRef = (payload: any, eventId?: SystemEvent) => Promise<any>;

/**
 * ** Event Handler record in registry.
 */
export type SystemEventHandlerRecord = {
    /**
     * ** Reference to Handler instance.
     */
    handlerRef: SystemEventHandlerRef;

    /**
     * ** Reference to the object where Handler belongs, for context purpose.
     */
    handlerClassInstance?: Record<any, any>;

    /**
     * ** Expression that filters if some Event should be dispatch to the Handler reference or not.
     */
    handlerFilterExpression?: Expression;
};
export type SystemEventHandlerFindByRef = { active: boolean; handlerRecord: SystemEventHandlerRecord; handlerRef: SystemEventHandlerRef };
export type SystemEventMetadataRecords = SystemEventMetadataRecord[];
