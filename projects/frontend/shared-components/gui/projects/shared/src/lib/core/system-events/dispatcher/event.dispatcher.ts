

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/no-explicit-any */

import { CollectionsUtil } from '../../../utils';

import { SE_ALL_EVENTS, SystemEvent, SystemEventComparable } from '../event';
import { SystemEventHandlerRegistry } from './registry';
import { SystemEventHandlerRecord } from './models';

/**
 * ** System Event Dispatcher.
 *
 *   - This Class is start point to trigger SystemEvent.
 *   - SystemEvent identifier is in string format, and would be nice those string to be assigned to constant for easier usage.
 *   - Payload could be any format but preferable is Literal Object.
 *   - SystemEvents could be dispatched in two ways using implemented behavior:
 *
 *   1) POST - this is NON-BLOCKING execution that leverages `setTimeout(handler, 0)` to avoid blocking main JavaScript thread.
 *
 *   2) SEND - this is BLOCKING execution that leverages `Promise` mechanism to chain Handlers execution. At the end returns
 *               flow of execution to Invoker.
 *
 *   - Handlers and their usage read at Decorators JSDoc {@link SystemEventHandlerClass} {@link SystemEventHandler}.
 *
 * @see SystemEventDispatcher.post
 * @see SystemEventDispatcher.send
 *
 * @example
 *    // void
 *    SystemEventDispatcher
 *        .post('SE_Send_Email', { email: 'join-versatiledatakit@groups.vmware.com });
 *
 *    // returns Promise
 *    SystemEventDispatcher
 *        .send('SE_Create_Job', { jobName: 'Test', jobCreator: 'System' })
 *        .then((v) => {
 *          // Do something
 *        });
 *
 *
 */
export class SystemEventDispatcher {
    /**
     * ** Method to post System Event.
     *
     *   - NON-BLOCKING execution.
     *   - Execution is non-blocking, e.g. it is executed in queue using setTimeout of 0.
     *   - If third parameters is provided it will execute as many handlers as it is request.
     *      - e.g. 1 or 2 or N and will skip the others.
     */
    static post(eventId: SystemEvent, payload: any, handlersToExecute: number = null) {
        const preparedHandlers = SystemEventHandlerRegistry.getPreparedArrayOfHandlers(eventId);

        let executedHandlers = 0;

        for (const handlerRecord of preparedHandlers) {
            if (!SystemEventDispatcher.executeExpressionFilter(handlerRecord, eventId, payload)) {
                return;
            }

            executedHandlers++;

            const isHandlerActive = (e: SystemEvent) => SystemEventHandlerRegistry.findHandlerByReference(
                e,
                handlerRecord.handlerRef,
                handlerRecord.handlerClassInstance
            ).active;

            setTimeout(() => {
                if (!isHandlerActive(eventId) && !isHandlerActive(SE_ALL_EVENTS)) {
                    return;
                }

                handlerRecord.handlerRef.call(handlerRecord.handlerClassInstance, payload, eventId);
            }, 0);

            if (CollectionsUtil.isNumber(handlersToExecute) && executedHandlers >= handlersToExecute) {
                break;
            }
        }
    }

    /**
     * ** Method to send System Event.
     *
     *   - BLOCKING execution.
     *   - Execution is blocking, e.g. it is achieved using Promises, and every handler must return Promise.
     *   - If third parameters is provided it will execute as many handlers as it is request.
     *      - e.g. 1 or 2 or N and will return the flow to the invoker.
     */
    static send(eventId: SystemEvent, payload: any, handlersToExecute: number = null): Promise<boolean> {
        const preparedHandlers = SystemEventHandlerRegistry.getPreparedArrayOfHandlers(eventId, true);

        return SystemEventDispatcher.executeSendCommand(
            preparedHandlers,
            eventId,
            payload,
            handlersToExecute
        );
    }

    /**
     * ** Execute send command and handle Promises from handlers.
     */
    private static executeSendCommand(handlers: SystemEventHandlerRecord[],
                                      eventId: SystemEvent,
                                      payload: any,
                                      handlersToExecute: number = null,
                                      executedHandlers = 0): Promise<boolean> {

        if (!handlers.length) {
            return Promise.resolve(true);
        }

        if (CollectionsUtil.isNumber(handlersToExecute) && handlersToExecute === executedHandlers) {
            return Promise.resolve(true);
        }

        const handlerForExecution = handlers.pop();

        if (!SystemEventDispatcher.executeExpressionFilter(handlerForExecution, eventId, payload)) {
            return SystemEventDispatcher.executeSendCommand(handlers, eventId, payload, handlersToExecute, executedHandlers);
        }

        // eslint-disable-next-line @typescript-eslint/no-unsafe-call,@typescript-eslint/no-unsafe-member-access,@typescript-eslint/no-unsafe-return
        return handlerForExecution.handlerRef
                                  .call(handlerForExecution.handlerClassInstance, payload, eventId)
                                  .then(() => SystemEventDispatcher
                                      .executeSendCommand(handlers, eventId, payload, handlersToExecute, executedHandlers + 1))
                                  .catch(() => Promise.reject(false));
    }

    /**
     * ** Execute Expression filter for Handler before execution.
     */
    private static executeExpressionFilter(handlerRecord: SystemEventHandlerRecord,
                                           eventId: SystemEvent,
                                           payload: any): boolean {

        const filterExpression = handlerRecord.handlerFilterExpression;

        if (CollectionsUtil.isNil(filterExpression)) {
            return true;
        }

        return handlerRecord.handlerFilterExpression.evaluate(
            // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
            SystemEventComparable.of({ eventId, payload })
        );
    }
}
