/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/unified-signatures,ngrx/avoid-mapping-selectors */

import { Injectable } from '@angular/core';

import { Observable } from 'rxjs';
import { filter, map, switchMap, take, withLatestFrom } from 'rxjs/operators';

import { Store } from '@ngrx/store';

import { CollectionsUtil } from '../../../utils';

import { RouterService, RouterState, RouteState } from '../../router';
import { GenericAction, STORE_COMPONENTS, StoreState } from '../../ngrx';

import {
	ComponentIdle,
	ComponentInit,
	ComponentLoading,
	ComponentUpdate
} from '../state';
import {
	ComponentsStateHelper,
	ComponentState,
	ComponentStateImpl,
	FAILED,
	IDLE,
	INITIALIZED,
	LiteralComponentsState,
	LOADED,
	LOADING,
	StatusType
} from '../model/state';
import { ComponentModel } from '../model';

/**
 * ** Service that manage Components State.
 *
 *
 */
export abstract class ComponentService {
	/**
	 * ** Initialize Component State and return Model.
	 */
	abstract init(id: string, routeState: RouteState): Observable<ComponentModel>;

	/**
	 * ** Set Component status to IDLE.
	 */
	abstract idle(componentState: ComponentState): void;

	/**
	 * ** Load Component State and return Model.
	 */
	abstract load(componentState: ComponentState): Observable<ComponentModel>;

	/**
	 * ** Update Component State.
	 */
	abstract update(componentState: ComponentState): void;

	/**
	 * ** Acknowledge if has ComponentState in segment.
	 *
	 *      - true - has ComponentState.
	 *      - false - doesn't have ComponentState.
	 */
	abstract hasInSegment(
		id: string,
		routePathSegments: string[]
	): Observable<boolean>;

	/**
	 * ** Listener that fires once after successful Component State initialization and returns Model.
	 */
	abstract onInit(
		id: string,
		routePathSegments: string[]
	): Observable<ComponentModel>;

	/**
	 * ** Listener that fires once after successful Component State load and returns Model.
	 */
	abstract onLoaded(
		id: string,
		routePathSegments: string[]
	): Observable<ComponentModel>;

	/**
	 * ** Returns stream with value Component Model and fires whenever Component State changes in Store.
	 *
	 *      - If no statusWatch provided by default will listen for statuses {@link LOADED} and {@link FAILED}.
	 */
	abstract getModel(
		id: string,
		routePathSegments: string[],
		statusWatch?: Array<StatusType | '*'>
	): Observable<ComponentModel>;

	/**
	 * ** Dispatch GenericAction with provided Type, ComponentState and optionally task.
	 */
	abstract dispatchAction(
		type: string,
		componentState: ComponentState,
		task?: string
	): void;

	/**
	 * ** Initialize Service.
	 */
	abstract initialize(): void;
}

/**
 * @inheritDoc
 */
@Injectable()
export class ComponentServiceImpl extends ComponentService {
	private readonly componentsStateHelper: ComponentsStateHelper;

	/**
	 * ** Constructor.
	 */
	constructor(
		private readonly store$: Store<StoreState>,
		private readonly routerService: RouterService
	) {
		super();

		this.componentsStateHelper = new ComponentsStateHelper();
	}

	/**
	 * @inheritDoc
	 */
	init(id: string, routeState: RouteState): Observable<ComponentModel> {
		this.store$
			.select((store) => store)
			.pipe(
				take(1),
				map((store) =>
					this._getComponentState(
						id,
						routeState.routePathSegments,
						store.router,
						store.components
					)
				)
			)
			.subscribe((componentState) => {
				if (componentState.status === INITIALIZED) {
					this.store$.dispatch(ComponentInit.of(componentState));
				}
			});

		return this.onInit(id, routeState.routePathSegments);
	}

	/**
	 * @inheritDoc
	 */
	idle(componentState: ComponentState): void {
		this.store$.dispatch(ComponentIdle.of(componentState));
	}

	/**
	 * @inheritDoc
	 */
	load(componentState: ComponentState): Observable<ComponentModel> {
		this.routerService
			.get()
			.pipe(take(1))
			.subscribe((routerState: RouterState) => {
				if (componentState.status === INITIALIZED) {
					this.store$.dispatch(
						ComponentIdle.of(
							componentState.copy({
								status: IDLE,
								navigationId: routerState.navigationId
							})
						)
					);
				}

				this.store$.dispatch(
					ComponentLoading.of(
						componentState.copy({
							status: LOADING,
							navigationId: routerState.navigationId
						})
					)
				);
			});

		return this.onLoaded(componentState.id, componentState.routePathSegments);
	}

	/**
	 * @inheritDoc
	 */
	update(componentState: ComponentState): void {
		this.routerService
			.get()
			.pipe(take(1))
			.subscribe((routerState) => {
				this.store$.dispatch(
					ComponentUpdate.of(
						componentState.copy({
							navigationId: routerState.navigationId
						})
					)
				);
			});
	}

	/**
	 * @inheritDoc
	 */
	hasInSegment(id: string, routePathSegments: string[]): Observable<boolean> {
		return this.store$.select(STORE_COMPONENTS).pipe(
			withLatestFrom(this.routerService.getState()),
			map(([literalComponentsState, routeState]) =>
				this._isComponentInStatus(
					id,
					routePathSegments,
					literalComponentsState,
					routeState,
					['*']
				)
			),
			take(1)
		);
	}

	/**
	 * @inheritDoc
	 */
	onInit(id: string, routePathSegments: string[]): Observable<ComponentModel> {
		return this.store$.select(STORE_COMPONENTS).pipe(
			withLatestFrom(this.routerService.getState()),
			map(([literalComponentsState, routeState]) =>
				this._isComponentInStatus(
					id,
					routePathSegments,
					literalComponentsState,
					routeState,
					['*']
				)
			),
			filter((isInitialized) => isInitialized),
			switchMap(() => this.getModel(id, routePathSegments, ['*'])),
			take(1)
		);
	}

	/**
	 * @inheritDoc
	 */
	onLoaded(
		id: string,
		routePathSegments: string[]
	): Observable<ComponentModel> {
		return this.store$.select(STORE_COMPONENTS).pipe(
			withLatestFrom(this.routerService.getState()),
			map(([literalComponentsState, routeState]) =>
				this._isComponentInStatus(
					id,
					routePathSegments,
					literalComponentsState,
					routeState,
					[LOADED, FAILED]
				)
			),
			filter((isLoaded) => isLoaded),
			switchMap(() => this.getModel(id, routePathSegments)),
			take(1)
		);
	}

	/**
	 * @inheritDoc
	 */
	getModel(
		id: string,
		routePathSegments: string[],
		statusWatch?: Array<StatusType | '*'>
	): Observable<ComponentModel> {
		const _statusWatch = statusWatch ?? [LOADED, FAILED];

		return this.store$.select(STORE_COMPONENTS).pipe(
			switchMap((literalComponentsState) =>
				this.routerService
					.get()
					.pipe(map((routerState) => [literalComponentsState, routerState]))
			),
			filter(
				([literalComponentsState, routerState]: [
					LiteralComponentsState,
					RouterState
				]) =>
					this._isComponentInStatus(
						id,
						routePathSegments,
						literalComponentsState,
						routerState.state,
						_statusWatch
					)
			),
			map(([literalComponentsState, routerState]) =>
				this._createModel(
					id,
					routePathSegments,
					literalComponentsState,
					routerState
				)
			)
		);
	}

	/**
	 * @inheritDoc
	 */
	dispatchAction(
		type: string,
		componentState: ComponentState,
		task?: string
	): void {
		this.getModel(componentState.id, componentState.routePathSegments, ['*'])
			.pipe(take(1))
			.subscribe((model) =>
				this.store$.dispatch(
					GenericAction.of(type, model.getComponentState(), task)
				)
			);
	}

	/**
	 * @inheritDoc
	 */
	initialize() {
		// No-op.
	}

	// Get Component State from Store if exist, otherwise create new State.
	private _getComponentState(
		id: string,
		routePathSegments: string[],
		routerState: RouterState,
		literalComponentsState: LiteralComponentsState
	): ComponentState {
		let _navigationId: number = null;
		let _routePath: string = null;
		let _routePathSegments: string[] = [];

		if (routerState) {
			_navigationId = routerState.navigationId;

			if (routerState.state && !routePathSegments) {
				_routePath = routerState.state.routePath;
				_routePathSegments = routerState.state.routePathSegments;
			}
		}

		if (routePathSegments) {
			_routePath = routePathSegments.slice().pop();
			_routePathSegments = routePathSegments;
		}

		let componentState = this.componentsStateHelper
			.setState(literalComponentsState)
			.getComponentState(id, _routePathSegments);

		if (componentState) {
			return componentState;
		}

		componentState = ComponentStateImpl.of({
			id,
			status: INITIALIZED,
			routePath: _routePath,
			routePathSegments: _routePathSegments,
			navigationId: _navigationId
		});

		return componentState;
	}

	// Utility method that filter if provided state is in desired status.
	private _isComponentInStatus(
		id: string,
		routePathSegments: string[],
		literalComponentsState: LiteralComponentsState,
		routeState: RouteState,
		statusWatch: Array<StatusType | '*'>
	): boolean {
		let _routePathSegments: string[] = [];

		if (CollectionsUtil.isArray(routePathSegments)) {
			_routePathSegments = routePathSegments;
		} else if (routeState) {
			_routePathSegments = routeState.routePathSegments;
		}

		const componentLiteralState = this.componentsStateHelper
			.setState(literalComponentsState)
			.getLiteralComponentState(id, _routePathSegments);

		if (!componentLiteralState) {
			return false;
		}

		if (statusWatch.indexOf('*') !== -1) {
			return true;
		}

		return statusWatch.indexOf(componentLiteralState.status) !== -1;
	}

	// Creates Model from provided data.
	private _createModel(
		id: string,
		routePathSegments: string[],
		literalComponentsState: LiteralComponentsState,
		routerState: RouterState
	): ComponentModel {
		let _routePathSegments: string[] = [];

		if (CollectionsUtil.isArray(routePathSegments)) {
			_routePathSegments = routePathSegments;
		} else if (routerState && routerState.state) {
			_routePathSegments = routerState.state.routePathSegments;
		}

		const componentState = this.componentsStateHelper
			.setState(literalComponentsState)
			.getComponentState(id, _routePathSegments);

		return ComponentModel.of(
			componentState,
			CollectionsUtil.cloneDeep(routerState)
		);
	}
}
