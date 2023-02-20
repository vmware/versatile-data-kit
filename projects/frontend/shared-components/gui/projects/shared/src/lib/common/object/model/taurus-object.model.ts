

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Directive, OnDestroy } from '@angular/core';

import { Subscription } from 'rxjs';
import { CollectionsUtil } from '../../../utils';

/**
 * ** Base Class for all Angular related Objects.
 *
 *      - Cleans all rxjs subscriptions on object destroy.
 *
 *
 */
@Directive()
// eslint-disable-next-line @angular-eslint/directive-class-suffix
export class TaurusObject implements OnDestroy {

    /**
     * ** Store for Subscriptions references.
     */
    protected subscriptions: Subscription[];

    /**
     * ** Constructor.
     */
    constructor() {
        this.subscriptions = [];
    }

    /**
     * ** Methods that will dispose Object.
     *      - Clean all Subscriptions.
     */
    dispose(): void {
        this.cleanSubscriptions();
    }

    /**
     * @inheritDoc
     */
    ngOnDestroy() {
        this.dispose();
    }

    /**
     * ** Clean all Subscriptions.
     */
    protected cleanSubscriptions(): void {
        // unsubscribe all valid subscriptions
        this.subscriptions
            // eslint-disable-next-line @typescript-eslint/unbound-method
            .filter(CollectionsUtil.isDefined)
            // eslint-disable-next-line @typescript-eslint/unbound-method
            .forEach(TaurusObject._unsubscribeFromStream);
    }

    protected removeSubscriptionRef(subscriptionRef: Subscription): boolean {
        const subscriptionIndex = this.subscriptions.findIndex((s) => s === subscriptionRef);

        if (subscriptionIndex === -1) {
            if (subscriptionRef instanceof Subscription) {
                TaurusObject._unsubscribeFromStream(subscriptionRef);

                return true;
            }

            return false;
        }

        const removedSubscription = this.subscriptions.splice(subscriptionIndex, 1);

        return TaurusObject._unsubscribeFromStream(removedSubscription[0]);
    }

    private static _unsubscribeFromStream(s: Subscription): boolean {
        try {
            s.unsubscribe();

            return true;
        } catch (e) {
            console.error(`Taurus Object failed to unsubscribe from rxjs stream!`, e);

            return false;
        }
    }
}
