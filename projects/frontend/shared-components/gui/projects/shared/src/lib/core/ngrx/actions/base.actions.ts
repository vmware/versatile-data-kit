

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Action } from '@ngrx/store';

import { createTaskIdentifier } from '../../../common';

/**
 * ** Base Action for Redux Impl.
 *
 *
 */
export abstract class BaseAction implements Action {
    /**
     * ** Type of Action.
     */
    readonly type: string;

    /**
     * ** Constructor.
     */
    protected constructor(type: string) {
        this.type = type;
    }
}

/**
 * ** Base Action with payload for Redux Impl.
 *
 *
 */
export abstract class BaseActionWithPayload<T> extends BaseAction {

    /**
     * ** Action payload data.
     */
    readonly payload: T;

    /**
     * ** Action Task.
     */
    readonly task: string;

    /**
     * ** Constructor.
     */
    protected constructor(type: string,
                          payload: T,
                          task?: string) {
        super(type);

        this.payload = payload;
        this.task = createTaskIdentifier(task);
    }

    /**
     * ** Factory method that have to be overridden in Subclasses.
     */
    static of(..._args: unknown[]): BaseActionWithPayload<unknown> {
        throw new Error('Method have to be overridden in Subclasses.');
    }
}

/**
 * ** Generic Action with payload for Redux Impl.
 *
 *      - All parameters type, payload and optional task are provided to Constructor.
 *
 *
 */
export class GenericAction<T> extends BaseActionWithPayload<T> {
    /**
     * ** Constructor.
     */
    constructor(type: string,
                payload: T,
                task?: string) {
        super(type, payload, task);
    }

    /**
     * ** Factory method for Generic Action with type and payload in Constructor.
     */
    static override of<K>(type: string, payload: K, task?: string): GenericAction<K> {
        return new GenericAction<K>(type, payload, task);
    }
}
