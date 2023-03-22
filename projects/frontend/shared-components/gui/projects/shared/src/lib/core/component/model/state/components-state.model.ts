/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { CollectionsUtil } from '../../../../utils';

import { IDLE } from './component-status.model';
import { ComponentState, ComponentStateImpl, LiteralComponentState } from './component-state.model';

export interface LiteralComponentsState {
    readonly components: { [name: string]: LiteralComponentState };
    readonly routePathSegments: { [segmentId: string]: LiteralComponentsState };
}

/**
 * ** ComponentsState Helper.
 */
export class ComponentsStateHelper {
    private _literalComponentsState: LiteralComponentsState;

    constructor() {
        this._literalComponentsState = {
            components: {},
            routePathSegments: {}
        };
    }

    /**
     * ** Returns LiteralComponentsState from Helper.
     */
    getState(): LiteralComponentsState {
        return {
            ...this._literalComponentsState
        };
    }

    /**
     * ** Will set state to the local Helper state.
     */
    setState(literalComponentsState: LiteralComponentsState) {
        this._literalComponentsState = this._shallowCloneComponentsState(literalComponentsState);

        return this;
    }

    /**
     * ** Will return LiteralComponentState for given id and routePathSegments.
     */
    getLiteralComponentState(id: string, routePathSegments?: string[]): LiteralComponentState {
        return this._getLiteralComponentState(
            id,
            CollectionsUtil.isArray(routePathSegments) ? [...routePathSegments] : [],
            this._literalComponentsState
        );
    }

    /**
     * ** Get ComponentState for given id and routePathSegments.
     */
    getComponentState(id: string, routePathSegments?: string[]): ComponentState {
        const literalComponentState = this._getLiteralComponentState(
            id,
            CollectionsUtil.isArray(routePathSegments) ? [...routePathSegments] : [],
            this._literalComponentsState
        );

        return CollectionsUtil.isDefined(literalComponentState)
            ? ComponentStateImpl.fromLiteralComponentState(literalComponentState)
            : null;
    }

    /**
     * ** Get all ComponentState for given routePathSegments.
     */
    getAllComponentState(routePathSegments: string[]): ComponentState[] {
        return this._getAllComponentState(
            CollectionsUtil.isArray(routePathSegments) ? [...routePathSegments] : [],
            this._literalComponentsState
        );
    }

    /**
     * ** Update LiteralComponentState.
     */
    updateLiteralComponentState(literalComponentState: LiteralComponentState): void {
        return this._updateLiteralComponentState(
            literalComponentState,
            [...literalComponentState.routePathSegments],
            this._literalComponentsState
        );
    }

    /**
     * ** Reset component status to NOT_LOADED for all ComponentState in a given routePathSegment.
     */
    resetComponentStates(routePathSegments: string[]): void {
        this._resetComponentStates(CollectionsUtil.isArray(routePathSegments) ? [...routePathSegments] : [], this._literalComponentsState);
    }

    /**
     * ** Delete all ComponentState for given routePathSegment.
     */
    deleteRoutePathSegments(routePathSegments: string[]): void {
        this._deleteRoutePathSegments(
            CollectionsUtil.isArray(routePathSegments) ? [...routePathSegments] : [],
            this._literalComponentsState
        );
    }

    /**
     * ** Update ComponentState.
     */
    private _updateLiteralComponentState(
        literalComponentState: LiteralComponentState,
        routePathSegments: string[],
        state: LiteralComponentsState
    ): void {
        if (CollectionsUtil.isArrayEmpty(routePathSegments)) {
            state.components[literalComponentState.id] = literalComponentState;

            return;
        }

        const routePathSegment = routePathSegments.shift();

        this._updateLiteralComponentState(
            literalComponentState,
            routePathSegments,
            this._normalizeRoutePathSegments(state.routePathSegments, routePathSegment)
        );
    }

    /**
     * ** Get ComponentState.
     */
    private _getLiteralComponentState(
        id: string,
        routePathSegments: string[],
        state: LiteralComponentsState
    ): LiteralComponentState | null {
        if (!state) {
            return null;
        }

        if (CollectionsUtil.isArrayEmpty(routePathSegments)) {
            if (state.components[id]) {
                return ComponentStateImpl.cloneDeepLiteral(state.components[id]);
            }

            return null;
        }

        const routePathSegment = routePathSegments.shift();

        return this._getLiteralComponentState(id, routePathSegments, state.routePathSegments[routePathSegment]);
    }

    /**
     * ** Get all components for given routePathSegments.
     */
    private _getAllComponentState(routePathSegments: string[], state: LiteralComponentsState): ComponentState[] {
        if (!state) {
            return [];
        }

        const components: ComponentState[] = CollectionsUtil.objectValues(state.components).map((c) =>
            ComponentStateImpl.fromLiteralComponentState(ComponentStateImpl.cloneDeepLiteral(c))
        );

        if (CollectionsUtil.isArrayEmpty(routePathSegments)) {
            return components;
        }

        const routePathSegment = routePathSegments.shift();

        return [...components, ...this._getAllComponentState(routePathSegments, state.routePathSegments[routePathSegment])];
    }

    /**
     * ** Reset component status to NOT_LOADED for all component in a given context.
     */
    private _resetComponentStates(routePathSegments: string[], state: LiteralComponentsState): void {
        CollectionsUtil.iterateObject(state.components, (componentState, id) => {
            state.components[id] = { ...componentState, status: IDLE };
        });

        if (CollectionsUtil.isArrayEmpty(routePathSegments)) {
            return;
        }

        const routePathSegment = routePathSegments.shift();

        this._resetComponentStates(routePathSegments, this._normalizeRoutePathSegments(state.routePathSegments, routePathSegment));
    }

    /**
     * ** Delete all components state for a given route path segment.
     */
    private _deleteRoutePathSegments(routePathSegments: string[], state: LiteralComponentsState): void {
        const routePathSegment = routePathSegments.shift();

        if (!routePathSegment) {
            return;
        }

        if (CollectionsUtil.isArrayEmpty(routePathSegments)) {
            delete state.routePathSegments[routePathSegment];

            return;
        }

        this._deleteRoutePathSegments(routePathSegments, this._normalizeRoutePathSegments(state.routePathSegments, routePathSegment));
    }

    /**
     * ** Normalize Route path segments.
     */
    private _normalizeRoutePathSegments(
        urlSegments: { [segmentId: string]: LiteralComponentsState },
        urlSegmentName: string
    ): LiteralComponentsState {
        if (CollectionsUtil.isNil(urlSegments[urlSegmentName])) {
            urlSegments[urlSegmentName] = {
                components: {},
                routePathSegments: {}
            };
        }

        return urlSegments[urlSegmentName];
    }

    private _shallowCloneComponentsState(source: LiteralComponentsState, target?: LiteralComponentsState): LiteralComponentsState {
        const _source: LiteralComponentsState = source ?? { components: {}, routePathSegments: {} };
        const _target: LiteralComponentsState = target ?? { components: {}, routePathSegments: {} };

        CollectionsUtil.iterateObject(_source.components, (value, key) => {
            _target.components[key] = value;
        });

        CollectionsUtil.iterateObject(_source.routePathSegments, (value, key) => {
            _target.routePathSegments[key] = {
                components: {},
                routePathSegments: {}
            };

            this._shallowCloneComponentsState(value, _target.routePathSegments[key]);
        });

        return _target;
    }
}
