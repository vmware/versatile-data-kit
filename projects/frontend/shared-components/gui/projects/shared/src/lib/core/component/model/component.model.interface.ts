/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/no-explicit-any */

import { ApiPredicate, ErrorRecord } from '../../../common';

import { RouterState } from '../../router';

import { ComponentState, StatusType } from './state';

/**
 * ** Interface for Model for all Components.
 */
export abstract class AbstractComponentModel {
    /**
     * ** Return RouterState.
     */
    abstract get routerState(): RouterState;

    /**
     * ** Return Status from ComponentState.
     */
    abstract get status(): StatusType;

    /**
     * ** Return routePath from RouterState.
     */
    abstract get routePath(): string;

    /**
     * ** Return the ComponentState.
     */
    abstract getComponentState(): ComponentState;

    /**
     * ** Set Search query to ComponentState and get Model reference again.
     * <p>
     *     - Ready for method chaining.
     * </p>
     */
    abstract withSearch(search: string): this;

    /**
     * ** Set Page to ComponentState and get Model reference again.
     * <p>
     *     - Ready for method chaining.
     * </p>
     */
    abstract withPage(page: number, size: number): this;

    /**
     * ** Set Filter to ComponentState and get Model reference again.
     * <p>
     *     - Ready for method chaining.
     * </p>
     */
    abstract withFilter(filterPredicates: ApiPredicate[]): this;

    /**
     * ** Set Request params to ComponentState and get Model reference again.
     * <p>
     *     - Ready for method chaining.
     * </p>
     */
    abstract withRequestParam(key: string, value: any): this;

    /**
     * ** Set Data (bound to key identifier) to ComponentState and get Model reference again.
     * <p>
     *     - Ready for method chaining.
     * </p>
     */
    abstract withData(key: string, data: any): this;

    /**
     * ** Set Task identifier to ComponentState and get Model reference again.
     *
     *      - Should be set only after data comes from the API, action is asynchronous.
     *      - Don't set this property during action dispatch
     *
     * <p>
     *      - Ready for method chaining.
     * </p>
     */
    abstract withTask(taskIdentifier: string): this;

    /**
     * ** Clear Task identifier from ComponentState and get Model reference again.
     * <p>
     *     - Ready for method chaining.
     * </p>
     */
    abstract clearTask(): this;

    /**
     * ** Returns latest Task from ComponentState.
     */
    abstract getTask(): string;

    /**
     * ** Returns latest Task unique identifier from ComponentState.
     */
    abstract getTaskUniqueIdentifier(): string;

    /**
     * ** Set ErrorRecord to ComponentState and get Model reference again.
     * <p>
     *     - Ready for method chaining.
     * </p>
     */
    abstract withError(error: ErrorRecord): this;

    /**
     * ** Clear Errors from ComponentState and get Model reference again.
     * <p>
     *     - Ready for method chaining.
     * </p>
     */
    abstract clearErrors(): this;

    /**
     * ** Remove specific error codes from ErrorStore and altogether from ComponentState and get Model reference again.
     * <p>
     *     - Ready for method chaining.
     * </p>
     */
    abstract removeErrorCode(...errorCodes: string[]): this;

    /**
     * ** Remove specific error code patterns from ErrorStore and altogether from ComponentState and get Model reference again.
     * <p>
     *     - Ready for method chaining.
     * </p>
     */
    abstract removeErrorCodePatterns(...errorCodePatterns: string[]): this;

    /**
     * ** Set UiState for given identifier to ComponentState and get Model reference again.
     * <p>
     *     - Ready for method chaining.
     * </p>
     */
    abstract withUiState(key: string, value: any): this;

    /**
     * ** Returns UiState for given identifier.
     */
    abstract getUiState<T>(key: string): T;

    /**
     * ** Set Component State status to IDLE.
     * <p>
     *     - Ready for method chaining.
     * </p>
     */
    abstract withStatusIdle(): this;

    /**
     * ** Set Component State status to LOADING.
     * <p>
     *     - Ready for method chaining.
     * </p>
     */
    abstract withStatusLoading(): this;

    /**
     * ** Set Component State status to LOADED.
     * <p>
     *     - Ready for method chaining.
     * </p>
     */
    abstract withStatusLoaded(): this;

    /**
     * ** Set Component State status to FAILED.
     * <p>
     *     - Ready for method chaining.
     * </p>
     */
    abstract withStatusFailed(): this;

    /**
     * ** Update Component State with Partial Component State patch.
     * <p>
     *     - Ready for method chaining.
     * </p>
     */
    abstract updateComponentState(patchState: Partial<ComponentState>): this;

    /**
     * ** Prepare model for Component destroy and assign all fields to their targeted state.
     * <p>
     *     - Ready for method chaining.
     * </p>
     */
    abstract prepareForDestroy(): this;

    /**
     * ** Filter method that analyze if current Model is different from given one.
     */
    abstract isModified(model: AbstractComponentModel): boolean;
}
