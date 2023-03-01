/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentModel } from '../../model';

/**
 * ** Taurus Component Lifecycle hook for Model initialized.
 *
 *
 */
export interface OnTaurusModelInit {
	/**
	 * ** Fires once per Route, after Component is initialized and
	 *      immediately after {@link ComponentModel} is initialized and it is bound to the Component model field.
	 *
	 *      - model - ComponentModel optional parameter.
	 *      - task - Is string optional parameter that inject context to callback for the specific operation.
	 */
	onModelInit(model?: ComponentModel, task?: string): void;
}

/**
 * @deprecated Deprecated since version 1.5.0 in favor of {@link OnTaurusModelInitialLoad}
 *
 * ** Taurus Component Lifecycle hook for Model First Load.
 *
 *
 */
export interface OnTaurusModelFirstLoad {
	/**
	 * ** Fires when something in State change and its status is LOADED or FAILED, and it fires only once.
	 *
	 *      - model - ComponentModel optional parameter.
	 *      - task - Is string optional parameter that inject context to callback for the specific operation.
	 *
	 * <p>
	 *     - General hook ideal for Ui state restore, or something that need Read->Action->Done behaviour.
	 * </p>
	 */
	onModelFirstLoad(model?: ComponentModel, task?: string): void;
}

/**
 * ** Taurus Component Lifecycle hook for Model Initial Load.
 *
 *
 */
export interface OnTaurusModelInitialLoad {
	/**
	 * ** Fires when something in State change and its status is LOADED or FAILED, and it fires only once.
	 *
	 *      - model - ComponentModel optional parameter.
	 *      - task - Is string optional parameter that inject context to callback for the specific operation.
	 *
	 * <p>
	 *     - General hook ideal for Ui state restore, or something that need Read->Action->Done behaviour.
	 * </p>
	 */
	onModelInitialLoad(model?: ComponentModel, task?: string): void;
}

/**
 * ** Taurus Component Lifecycle hook for Model Loaded.
 *
 *
 */
export interface OnTaurusModelLoad {
	/**
	 * ** Fires when something in State change and its status is LOADED or FAILED.
	 *
	 *      - model - ComponentModel optional parameter.
	 *      - task - Is string optional parameter that inject context to callback for the specific operation.
	 *
	 * <p>
	 *     - General hook ideal for loading spinner HIDE.
	 * </p>
	 */
	onModelLoad(model?: ComponentModel, task?: string): void;
}

/**
 * ** Taurus Component Lifecycle hook for Model Changed.
 *
 *
 */
export interface OnTaurusModelChange {
	/**
	 * ** Fires when something in State change and its status is LOADED.
	 *
	 *      - model - ComponentModel optional parameter.
	 *      - task - Is string optional parameter that inject context to callback for the specific operation.
	 */
	onModelChange(model?: ComponentModel, task?: string): void;
}

/**
 * @deprecated Deprecated since version 1.5.0 in favor of {@link OnTaurusModelError}
 *
 * ** Taurus Component Lifecycle hook for Model Failed.
 *
 *
 */
export interface OnTaurusModelFail {
	/**
	 * ** Fires when something in State change and its status is FAILED.
	 *
	 *      - model - ComponentModel optional parameter.
	 *      - task - Is string optional parameter that inject context to callback for the specific operation.
	 */
	onModelFail(model?: ComponentModel, task?: string): void;
}

/**
 * ** Taurus Component Lifecycle hook for Model Failed.
 *
 *
 */
export interface OnTaurusModelError {
	/**
	 * ** Fires when something in State change and its status is FAILED.
	 *
	 *      - model - ComponentModel optional parameter.
	 *      - task - Is string optional parameter that inject context to callback for the specific operation.
	 */
	onModelError(model?: ComponentModel, task?: string): void;
}

export type TaurusComponentHooks = OnTaurusModelInit &
	OnTaurusModelInitialLoad &
	OnTaurusModelFirstLoad &
	OnTaurusModelLoad &
	OnTaurusModelChange &
	OnTaurusModelError &
	OnTaurusModelFail;
