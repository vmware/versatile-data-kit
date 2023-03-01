/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/no-explicit-any */

import {
	ApiPredicate,
	extractTaskFromIdentifier,
	RequestFilterImpl,
	RequestPageImpl
} from '../../../common';

import { RouterState } from '../../router';

import {
	ComponentState,
	ComponentStateImpl,
	FAILED,
	IDLE,
	LOADED,
	LOADING,
	StatusType
} from './state';

import { ComponentModelComparable } from './component-model.comparable';

import { AbstractComponentModel } from './component.model.interface';

/**
 * ** Generic Model for all Components.
 *
 *
 */
export class ComponentModel extends AbstractComponentModel {
	/**
	 * ** Constructor.
	 */
	constructor(
		protected _componentState: ComponentState,
		protected _routerState: RouterState
	) {
		super();
	}

	/**
	 * ** Factory method.
	 */
	static of(componentState: ComponentState, routerState: RouterState) {
		return new ComponentModel(componentState, routerState);
	}

	/**
	 * @inheritDoc
	 */
	get routerState(): RouterState {
		return this._routerState;
	}

	/**
	 * @inheritDoc
	 */
	get status(): StatusType {
		return this.getComponentState().status;
	}

	/**
	 * @inheritDoc
	 */
	get routePath(): string {
		return (
			this.getComponentState().routePath ||
			this.routerState.state.routeSegments.routePath
		);
	}

	/**
	 * @inheritDoc
	 */
	getComponentState(): ComponentState {
		return this._componentState;
	}

	/**
	 * @inheritDoc
	 */
	withSearch(search: string) {
		this.updateComponentState({
			search
		});

		return this;
	}

	/**
	 * @inheritDoc
	 */
	withPage(page: number, size: number) {
		this.updateComponentState({
			page: RequestPageImpl.of(page, size)
		});

		return this;
	}

	/**
	 * @inheritDoc
	 */
	withFilter(filterPredicates: ApiPredicate[]) {
		this.updateComponentState({
			filter: RequestFilterImpl.of(...filterPredicates)
		});

		return this;
	}

	/**
	 * @inheritDoc
	 */
	withRequestParam(key: string, value: any) {
		this.getComponentState().requestParams.set(key, value);

		return this;
	}

	/**
	 * @inheritDoc
	 */
	withData(key: string, data: any) {
		this.getComponentState().data.set(key, data);

		return this;
	}

	/**
	 * @inheritDoc
	 */
	withTask(taskIdentifier: string) {
		this.updateComponentState({ task: taskIdentifier });

		return this;
	}

	/**
	 * @inheritDoc
	 */
	clearTask() {
		this.updateComponentState({ task: null });

		return this;
	}

	/**
	 * @inheritDoc
	 */
	getTask(): string {
		return extractTaskFromIdentifier(this.getComponentState().task);
	}

	/**
	 * @inheritDoc
	 */
	getTaskUniqueIdentifier(): string {
		return this.getComponentState().task;
	}

	/**
	 * @inheritDoc
	 */
	withError(error: Error) {
		this.updateComponentState({ error });

		return this;
	}

	/**
	 * @inheritDoc
	 */
	clearError() {
		this.updateComponentState({ error: null });

		return this;
	}

	/**
	 * @inheritDoc
	 */
	withUiState(key: string, value: any) {
		this.getComponentState().uiState.set(key, value);

		return this;
	}

	/**
	 * @inheritDoc
	 */
	getUiState<T>(key: string): T {
		return this.getComponentState().uiState.get(key) as T;
	}

	/**
	 * @inheritDoc
	 */
	withStatusIdle() {
		this.updateComponentState({ status: IDLE });

		return this;
	}

	/**
	 * @inheritDoc
	 */
	withStatusLoading() {
		this.updateComponentState({ status: LOADING });

		return this;
	}

	/**
	 * @inheritDoc
	 */
	withStatusLoaded() {
		this.updateComponentState({ status: LOADED });

		return this;
	}

	/**
	 * @inheritDoc
	 */
	withStatusFailed() {
		this.updateComponentState({ status: FAILED });

		return this;
	}

	/**
	 * @inheritDoc
	 */
	updateComponentState(patchState: Partial<ComponentState>) {
		this._componentState = ComponentStateImpl.of({
			...this.getComponentState(),
			...patchState
		});

		return this;
	}

	/**
	 * @inheritDoc
	 */
	isModified(model: ComponentModel): boolean {
		return ComponentModelComparable.of(this).notEqual(
			ComponentModelComparable.of(model)
		);
	}
}
