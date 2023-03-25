/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/no-explicit-any */

import { CollectionsUtil } from '../../../../utils';

import { Expression } from '../../../../common';

import { SE_ALL_EVENTS, SystemEvent } from '../../event';
import { SystemEventHandlerFindByRef, SystemEventHandlerRecord, SystemEventHandlerRef } from '../models';

/**
 * ** Registry for Events Handlers.
 */
export class SystemEventHandlerRegistry {
    /**
     * ** Returns Singleton instance.
     */
    static get instance(): SystemEventHandlerRegistry {
        if (CollectionsUtil.isNil(SystemEventHandlerRegistry._instance)) {
            SystemEventHandlerRegistry._instance = new SystemEventHandlerRegistry();
        }

        return SystemEventHandlerRegistry._instance;
    }

    private static _instance: SystemEventHandlerRegistry;

    private readonly handlers: Map<SystemEvent, Set<SystemEventHandlerRecord>> = new Map<SystemEvent, Set<SystemEventHandlerRecord>>();

    /**
     * ** Constructor.
     *
     *    - Private constructor to make it Singleton.
     */
    private constructor() {
        // No-op.
    }

    /**
     * ** Register Handler for SystemEvent/s.
     */
    static register<T>(
        knownEvents: SystemEvent | SystemEvent[],
        handlerRef: SystemEventHandlerRef,
        handlerClassInstance: T,
        handlerFilterExpression: Expression = null
    ): boolean {
        return SystemEventHandlerRegistry.instance.register<T>(knownEvents, handlerRef, handlerClassInstance, handlerFilterExpression);
    }

    /**
     * ** Unregister Handler from registry.
     *
     *   - It should be done in ngOnDestroy() method in Services/Components to avoid potential memory leaks.
     */
    static unregister(knownEvents: SystemEvent | SystemEvent[], handlerRef: SystemEventHandlerRef): boolean {
        return SystemEventHandlerRegistry.instance.unregister(knownEvents, handlerRef);
    }

    /**
     * ** Find Handler by reference looking through the Registry.
     */
    static findHandlerByReference(
        eventId: SystemEvent,
        handlerRef: SystemEventHandlerRef,
        handlerClassInstance?: any
    ): SystemEventHandlerFindByRef {
        return SystemEventHandlerRegistry.instance.findHandlerByReference(eventId, handlerRef, handlerClassInstance);
    }

    /**
     * ** Prepare array of handlers for execution of post or send.
     */
    static getPreparedArrayOfHandlers(eventId: SystemEvent, reversed = false): SystemEventHandlerRecord[] {
        return SystemEventHandlerRegistry.instance.getPreparedArrayOfHandlers(eventId, reversed);
    }

    private register<T>(
        knownEvents: SystemEvent | SystemEvent[],
        handlerRef: SystemEventHandlerRef,
        handlerClassInstance: T,
        handlerFilterExpression: Expression = null
    ): boolean {
        return this.execute(
            knownEvents,
            handlerRef,
            // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
            this.executeRegister.bind(this),
            handlerClassInstance,
            handlerFilterExpression
        );
    }

    private unregister(knownEvents: SystemEvent | SystemEvent[], handlerRef: SystemEventHandlerRef): boolean {
        return this.execute(
            knownEvents,
            handlerRef,
            // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
            this.executeUnregister.bind(this)
        );
    }

    private findHandlerByReference(
        eventId: SystemEvent,
        handlerRef: SystemEventHandlerRef,
        handlerClassInstance?: any
    ): SystemEventHandlerFindByRef {
        const handlers = this.handlers.has(eventId) ? this.handlers.get(eventId) : new Set<SystemEventHandlerRecord>();

        const handlerRecord = Array.from(handlers.values()).find((r) => {
            let isEqual = r.handlerRef === handlerRef;

            if (handlerClassInstance) {
                isEqual = isEqual && r.handlerClassInstance === handlerClassInstance;
            }

            return isEqual;
        });

        return {
            active: CollectionsUtil.isDefined(handlerRecord),
            handlerRecord,
            handlerRef: CollectionsUtil.isDefined(handlerRecord) ? handlerRecord.handlerRef : undefined
        };
    }

    private getPreparedArrayOfHandlers(eventId: SystemEvent, reversed = false): SystemEventHandlerRecord[] {
        const specialHandlers: SystemEventHandlerRecord[] = this.getSpecialHandlers();

        if (!this.handlers.has(eventId)) {
            return specialHandlers;
        }

        return reversed
            ? Array.from(this.handlers.get(eventId).values()).concat(specialHandlers).reverse()
            : Array.from(this.handlers.get(eventId).values()).concat(specialHandlers);
    }

    /**
     * ** Generic abstraction for Register and Unregister handlers.
     */
    private execute(
        knownEvents: SystemEvent | SystemEvent[],
        handlerRef: SystemEventHandlerRef,
        executeMethodRef: (...arg: any[]) => any,
        handlerClassInstance?: any,
        handlerFilterExpression?: Expression
    ): boolean {
        const preparedData = this.prepareEventNames(knownEvents);

        if (!preparedData.status || !CollectionsUtil.isFunction(handlerRef)) {
            return false;
        }

        try {
            preparedData.eventNames.forEach((eventId) => {
                executeMethodRef(eventId, handlerRef, handlerClassInstance, handlerFilterExpression);
            });

            return true;
        } catch (_e) {
            return false;
        }
    }

    /**
     * ** Evaluate Handler register.
     */
    private executeRegister(
        eventId: SystemEvent,
        handlerRef: SystemEventHandlerRef,
        handlerClassInstance: any,
        handlerFilterExpression: Expression
    ): boolean {
        if (!this.handlers.has(eventId)) {
            this.handlers.set(eventId, new Set());
        }

        if (this.findHandlerByReference(eventId, handlerRef, handlerClassInstance).active) {
            return false;
        }

        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        this.handlers.get(eventId).add({ handlerRef, handlerClassInstance, handlerFilterExpression });

        return true;
    }

    /**
     * ** Evaluate Handler unregister.
     */
    private executeUnregister(eventId: SystemEvent, handlerRef: SystemEventHandlerRef): boolean {
        if (!this.handlers.has(eventId)) {
            return false;
        }

        const findHandlerResponse = this.findHandlerByReference(eventId, handlerRef);

        if (!findHandlerResponse.active) {
            return false;
        }

        this.handlers.get(eventId).delete(findHandlerResponse.handlerRecord);

        return true;
    }

    /**
     * ** Prepares Event names in Array of strings format.
     */
    private prepareEventNames(knownEvents: SystemEvent | SystemEvent[]): { status: boolean; eventNames?: SystemEvent[] } {
        if (!CollectionsUtil.isString(knownEvents) && !CollectionsUtil.isArray(knownEvents)) {
            return {
                status: false
            };
        }

        return {
            status: true,
            eventNames: CollectionsUtil.isString(knownEvents) ? [knownEvents] : knownEvents
        };
    }

    /**
     * ** Returns special Handlers.
     */
    private getSpecialHandlers(): SystemEventHandlerRecord[] {
        if (!this.handlers.has(SE_ALL_EVENTS)) {
            return [];
        }

        return Array.from(this.handlers.get(SE_ALL_EVENTS).values());
    }
}
