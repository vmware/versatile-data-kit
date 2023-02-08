

import { NavigationExtras } from '@angular/router';

import { BaseAction, BaseActionWithPayload } from '../../../ngrx/actions';

/**
 * ** Action Identifier for Router Navigate.
 *
 * @author gorankokin
 */
export const ROUTER_NAVIGATE = '[router] Navigate';

/**
 * ** Action Identifier for Location Go.
 *
 * @author gorankokin
 */
export const LOCATION_GO = '[location] Go';

/**
 * ** Action Identifier for Location Back.
 *
 * @author gorankokin
 */
export const LOCATION_BACK = '[location] Back';

/**
 * ** Action Identifier for Location Forward.
 *
 * @author gorankokin
 */
export const LOCATION_FORWARD = '[location] Forward';

export interface NavigatePayload {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    commands: any[];
    extras?: NavigationExtras;
}

/**
 * ** Navigate Action instruct subscribers that they should navigate to given path.
 *
 * @author gorankokin
 */
export class RouterNavigate extends BaseActionWithPayload<NavigatePayload> {
    constructor(payload: NavigatePayload) {
        super(ROUTER_NAVIGATE, payload);
    }

    /**
     * ** Factory method.
     */
    static override of(payload: NavigatePayload) {
        return new RouterNavigate(payload);
    }
}

export interface GoPayload {
    path: string;
    query?: string;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    state?: any;
}

/**
 * ** Location Go Action instruct subscribers that they should navigate using Location.
 *
 * @author gorankokin
 */
export class LocationGo extends BaseActionWithPayload<GoPayload> {
    constructor(payload: GoPayload) {
        super(LOCATION_GO, payload);
    }

    /**
     * ** Factory method.
     */
    static override of(payload: GoPayload) {
        return new LocationGo(payload);
    }
}

/**
 * ** Back Action instruct subscribers to pop history Backward.
 *
 * @author gorankokin
 */
export class LocationBack extends BaseAction {
    constructor() {
        super(LOCATION_BACK);
    }

    /**
     * ** Factory method.
     */
    static of() {
        return new LocationBack();
    }
}

/**
 * ** Forward Action instruct subscribers to go Forward.
 *
 * @author gorankokin
 */
export class LocationForward extends BaseAction {
    constructor() {
        super(LOCATION_FORWARD);
    }

    /**
     * ** Factory method.
     */
    static of() {
        return new LocationForward();
    }
}

export type NavigationActions = RouterNavigate | LocationGo | LocationBack | LocationForward;
