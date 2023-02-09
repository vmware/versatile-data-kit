

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { BaseActionWithPayload } from '../../../ngrx/actions';

import { ComponentState } from '../../model';

/**
 * ** Action Identifier for Component Initialization.
 */
export const COMPONENT_INIT = '[component] Init';

/**
 * ** Action Identifier for Component Idle.
 */
export const COMPONENT_IDLE = '[component] Idle';

/**
 * ** Action Identifier for Component start Loading data.
 */
export const COMPONENT_LOADING = '[component] Loading';

/**
 * ** Action Identifier for Component Loaded data.
 */
export const COMPONENT_LOADED = '[component] Loaded';

/**
 * ** Action Identifier for Component Failed loading data.
 */
export const COMPONENT_FAILED = '[component] Failed';

/**
 * ** Action Identifier for Component Update state.
 */
export const COMPONENT_UPDATE = '[component] Update';

/**
 * ** Action Identifier for Component Clear data.
 */
export const COMPONENT_CLEAR_DATA = '[component] Clear data';

/**
 * ** Action for Component Initialization.
 *
 *
 */
export class ComponentInit extends BaseActionWithPayload<ComponentState> {
    constructor(payload: ComponentState) {
        super(COMPONENT_INIT, payload);
    }

    /**
     * ** Factory method.
     */
    static override of(payload: ComponentState) {
        return new ComponentInit(payload);
    }
}

/**
 * ** Action for Component Idle.
 *
 *
 */
export class ComponentIdle extends BaseActionWithPayload<ComponentState> {
    constructor(payload: ComponentState) {
        super(COMPONENT_IDLE, payload);
    }

    /**
     * ** Factory method.
     */
    static override of(payload: ComponentState) {
        return new ComponentIdle(payload);
    }
}

/**
 * ** Action for Component Loading.
 *
 *
 */
export class ComponentLoading extends BaseActionWithPayload<ComponentState> {
    constructor(payload: ComponentState) {
        super(COMPONENT_LOADING, payload);
    }

    /**
     * ** Factory method.
     */
    static override of(payload: ComponentState) {
        return new ComponentLoading(payload);
    }
}

/**
 * ** Action for Component Loaded.
 *
 *
 */
export class ComponentLoaded extends BaseActionWithPayload<ComponentState> {
    constructor(payload: ComponentState) {
        super(COMPONENT_LOADED, payload);
    }

    /**
     * ** Factory method.
     */
    static override of(payload: ComponentState) {
        return new ComponentLoaded(payload);
    }
}

/**
 * ** Action for Component Failed.
 *
 *
 */
export class ComponentFailed extends BaseActionWithPayload<ComponentState> {
    constructor(payload: ComponentState) {
        super(COMPONENT_FAILED, payload);
    }

    /**
     * ** Factory method.
     */
    static override of(payload: ComponentState) {
        return new ComponentFailed(payload);
    }
}

/**
 * ** Action for Component Update.
 *
 *
 */
export class ComponentUpdate extends BaseActionWithPayload<ComponentState> {
    constructor(payload: ComponentState) {
        super(COMPONENT_UPDATE, payload);
    }

    /**
     * ** Factory method.
     */
    static override of(payload: ComponentState) {
        return new ComponentUpdate(payload);
    }
}

/**
 * ** Action for Component Clear Data.
 *
 *
 */
export class ComponentClearData extends BaseActionWithPayload<ComponentState> {
    constructor(payload: ComponentState) {
        super(COMPONENT_CLEAR_DATA, payload);
    }

    /**
     * ** Factory method.
     */
    static override of(payload: ComponentState) {
        return new ComponentClearData(payload);
    }
}

/**
 * ** Union of all Actions that could be use as a type in Effects/Reducers/etc...
 */
export type ComponentActions = ComponentInit | ComponentIdle | ComponentLoading |
    ComponentLoaded | ComponentFailed | ComponentUpdate | ComponentClearData;
