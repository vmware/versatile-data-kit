

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/no-explicit-any */

import { CollectionsUtil } from '../../../../utils';

import {
    Copy,
    Literal,
    LiteralApiPredicates,
    LiteralRequestPage,
    RequestFilter,
    RequestFilterImpl,
    RequestOrder,
    RequestOrderImpl,
    RequestPage,
    RequestPageImpl
} from '../../../../common';

import { IDLE, StatusType } from './component-status.model';

/**
 * ** Literal Component State in purest format ready for Store persisting.
 *
 *
 */
export interface LiteralComponentState {
    /**
     * ** Identifier for Component State.
     */
    readonly id: string;

    /**
     * ** Status for Component State.
     */
    readonly status: StatusType;

    /**
     * ** Component State Data.
     * <p>
     *     - Free format Literal Object.
     * </p>
     */
    readonly data?: { [key: string]: any };

    /**
     * ** Route path for current State.
     */
    readonly routePath?: string;

    /**
     * ** Route path segments for current State.
     */
    readonly routePathSegments?: string[];

    /**
     * ** Search query for Http requests.
     */
    readonly search?: string;

    /**
     * ** Page for Http requests.
     */
    readonly page?: LiteralRequestPage;

    /**
     * ** Order for Http requests.
     */
    readonly order?: LiteralApiPredicates;

    /**
     * ** Filter for Http requests.
     */
    readonly filter?: LiteralApiPredicates;

    /**
     * ** Order for Http requests.
     */
    readonly requestParams?: { [key: string]: any };

    /**
     * ** Task is property that give bi-directional refinement context.
     *
     *      - Gives context to Effect through Action.
     *      - Gives context to Component through ComponentState (ComponentModel).
     */
    readonly task?: string;

    /**
     * ** Router NavigationId bound to this Component State.
     */
    readonly navigationId?: number;

    /**
     * ** Error that could happen in Stream manipulation down to the Components.
     * <p>
     *     - Ideal for storing Http errors, so Component could easily leverage that knowledge and show info for User.
     * </p>
     */
    readonly error?: Error;

    /**
     * ** Component State UiState, that holds all information for UiElements.
     * <p>
     *     - Free format Literal Object where key identifier could be (Component/Html Element) name/id/class etc...
     * </p>
     */
    readonly uiState?: { [key: string]: any };
}

export interface ComponentState extends Literal<LiteralComponentState>, Copy<ComponentState> {
    /**
     * ** Identifier for Component State.
     */
    readonly id: string;

    /**
     * ** Status for Component State.
     */
    readonly status: StatusType;

    /**
     * ** Component State Data.
     * <p>
     *     - Free format Map.
     * </p>
     */
    readonly data?: Map<string, any>;

    /**
     * ** Route path for current State.
     */
    readonly routePath?: string;

    /**
     * ** Route Path Segments for current State.
     */
    readonly routePathSegments?: string[];

    /**
     * ** Search query for Http requests.
     */
    readonly search?: string;

    /**
     * ** Page for Http requests.
     */
    readonly page?: RequestPage;

    /**
     * ** Order for Http requests.
     */
    readonly order?: RequestOrder;

    /**
     * ** Filter for Http requests.
     */
    readonly filter?: RequestFilter;

    /**
     * ** Map with different parameters for Http requests.
     */
    readonly requestParams?: Map<string, any>;

    /**
     * ** Task is property that give bi-directional refinement context.
     *
     *      - Gives context to Effect through Action.
     *      - Gives context to Component through ComponentState (ComponentModel).
     */
    readonly task?: string;

    /**
     * ** Router NavigationId bound to this Component State.
     */
    readonly navigationId?: number;

    /**
     * ** Error that could happen in Stream manipulation down to the Components.
     * <p>
     *     - Ideal for storing Http errors, so Component could easily leverage that knowledge and show info for User.
     * </p>
     */
    readonly error?: Error;

    /**
     * ** Component State UiState, that holds all information for UiElements.
     * <p>
     *     - Free format Map where key identifier could be (Component/Html Element) name/id/class etc...
     * </p>
     */
    readonly uiState?: Map<string, any>;

    /**
     * @inheritDoc
     */
    toLiteral(): LiteralComponentState;

    /**
     * @inheritDoc
     */
    toLiteralDeepClone(): LiteralComponentState;

    /**
     * @inheritDoc
     */
    copy(state?: Partial<ComponentState>): ComponentState;
}

/**
 * ** ComponentState implementation will all methods and other utilities.
 */
export class ComponentStateImpl implements ComponentState {
    /**
     * @inheritDoc
     */
    readonly id: string;

    /**
     * @inheritDoc
     */
    readonly status: StatusType;

    /**
     * @inheritDoc
     */
    readonly data: Map<string, any>;

    /**
     * @inheritDoc
     */
    readonly routePath: string;

    /**
     * @inheritDoc
     */
    readonly routePathSegments: string[];

    /**
     * @inheritDoc
     */
    readonly search: string;

    /**
     * @inheritDoc
     */
    readonly page: RequestPageImpl;

    /**
     * @inheritDoc
     */
    readonly order: RequestOrderImpl;

    /**
     * @inheritDoc
     */
    readonly filter: RequestFilterImpl;

    /**
     * @inheritDoc
     */
    readonly requestParams: Map<string, any>;

    /**
     * @inheritDoc
     */
    readonly task: string;

    /**
     * @inheritDoc
     */
    readonly navigationId: number;

    /**
     * @inheritDoc
     */
    readonly error: Error;

    /**
     * @inheritDoc
     */
    readonly uiState: Map<string, any>;

    /**
     * ** Constructor.
     *
     * <p><b>
     *     Important:
     * </b></p>
     * <p>
     *     If you add new Property in {@link LiteralComponentState}/{@link ComponentState}
     *  <ul>
     *     <li>
     *        Implement field in {@link ComponentStateImpl} and handle null/undefined, assign defaults (required for Collections).
     *     </li>
     *     <li>
     *        Copy/Clone process have to be handled manually (for performance gain) in methods:
     *
     *        {@link ComponentStateImpl.fromLiteralComponentState}
     *        {@link ComponentStateImpl.cloneDeepLiteral}
     *        {@link ComponentStateImpl.toLiteral}
     *     </li>
     *  </ul>
     * </p>
     */
    constructor(stateModelProp: Partial<ComponentState>) {
        const stateModel: Partial<ComponentState> = CollectionsUtil.isDefined(stateModelProp)
            ? stateModelProp
            : {};

        this.id = stateModel.id;
        this.status = stateModel.status ?? IDLE;
        this.navigationId = stateModel.navigationId ?? null;
        this.routePath = stateModel.routePath;
        this.routePathSegments = stateModel.routePathSegments ?? [];
        this.search = stateModel.search ?? '';
        this.page = stateModel.page ?? RequestPageImpl.empty();
        this.order = stateModel.order ?? RequestOrderImpl.empty();
        this.filter = stateModel.filter ?? RequestFilterImpl.empty();
        this.requestParams = stateModel.requestParams ?? new Map<string, any>();
        this.task = stateModel.task ?? null;
        this.error = stateModel.error ?? null;
        this.data = stateModel.data ?? new Map<string, any>();
        this.uiState = stateModel.uiState ?? new Map<string, any>();
    }

    /**
     * ** Factory method.
     */
    static of(stateModel: Partial<ComponentState>): ComponentStateImpl {
        return new ComponentStateImpl(stateModel);
    }

    /**
     * ** Convert provided {@link LiteralComponentState} into instance of {@link ComponentStateImpl}.
     * <p>
     *     Every literals could be transformed to their original Collection format.
     *     <ul>
     *         <li>
     *             Object literals could be transformed to Map/WeakMap/Set depends of the needs.
     *         </li>
     *         <li>
     *             Array is keep as it is.
     *         </li>
     *     </ul>
     * </p>
     *
     * @see CollectionsUtil.transformObjectToMap
     * @see CollectionsUtil.transformMapToObject
     */
    static fromLiteralComponentState(literalStateModel: LiteralComponentState): ComponentStateImpl {
        return ComponentStateImpl.of({
            ...literalStateModel,
            page: RequestPageImpl.fromLiteral(literalStateModel.page),
            order: RequestOrderImpl.fromLiteral(literalStateModel.order),
            filter: RequestFilterImpl.fromLiteral(literalStateModel.filter),
            requestParams: CollectionsUtil.transformObjectToMap(literalStateModel.requestParams),
            data: CollectionsUtil.transformObjectToMap(literalStateModel.data),
            uiState: CollectionsUtil.transformObjectToMap(literalStateModel.uiState)
        });
    }

    /**
     * ** Make deep clone from Literal Component State.
     */
    static cloneDeepLiteral(literalStateModel: LiteralComponentState): LiteralComponentState {
        return {
            id: literalStateModel.id,
            status: literalStateModel.status,
            data: CollectionsUtil.cloneDeep(literalStateModel.data),
            routePath: literalStateModel.routePath,
            routePathSegments: [...literalStateModel.routePathSegments],
            search: literalStateModel.search,
            page: CollectionsUtil.cloneDeep(literalStateModel.page),
            order: CollectionsUtil.cloneDeep(literalStateModel.order),
            filter: CollectionsUtil.cloneDeep(literalStateModel.filter),
            requestParams: CollectionsUtil.cloneDeep(literalStateModel.requestParams),
            task: literalStateModel.task,
            navigationId: literalStateModel.navigationId,
            error: literalStateModel.error,
            uiState: CollectionsUtil.cloneDeep(literalStateModel.uiState)
        };
    }

    /**
     * <p>
     *     Every Collection should be transformed to format of JSON supported literals, ready for LocalStorage/SessionStorage persist.
     *     <ul>
     *         <li>
     *             Map/WeakMap/Set have to be transform to Object literal.
     *         </li>
     *         <li>
     *             Array is keep as it is.
     *         </li>
     *     </ul>
     * </p>
     *
     * @see CollectionsUtil.transformObjectToMap
     * @see CollectionsUtil.transformMapToObject
     *
     * @inheritDoc
     */
    toLiteral(): LiteralComponentState {
        return {
            ...this,
            page: this.page.toLiteral(),
            order: this.order.toLiteral(),
            filter: this.filter.toLiteral(),
            requestParams: CollectionsUtil.transformMapToObject(this.requestParams),
            data: CollectionsUtil.transformMapToObject(this.data),
            uiState: CollectionsUtil.transformMapToObject(this.uiState)
        };
    }

    /**
     * @inheritDoc
     */
    toLiteralDeepClone(): LiteralComponentState {
        return ComponentStateImpl.cloneDeepLiteral(
            this.toLiteral()
        );
    }

    /**
     * @inheritDoc
     */
    copy(state: Partial<ComponentState> = {}): ComponentStateImpl {
        return ComponentStateImpl.of({
            ...this,
            ...state
        });
    }
}
