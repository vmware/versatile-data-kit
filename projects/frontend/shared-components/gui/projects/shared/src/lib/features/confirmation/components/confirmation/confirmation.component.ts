/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnDestroy, ViewChild, ViewContainerRef } from '@angular/core';

import { ConfirmationModelImpl, ERROR_CODE_CONFIRMATION_FORCEFULLY_DESTROYED_COMPONENT } from '../../model/confirmation.model';

/**
 * ** Confirmation Component that is created for every confirmation as in {@link ConfirmationService}.
 *
 *      - It is created multiple times, once for every single confirmation, and its field {@link ConfirmationComponent.model}
 *              is managed from {@link ConfirmationService}.
 */
@Component({
    selector: 'shared-confirmation',
    templateUrl: './confirmation.component.html',
    styleUrls: ['./confirmation.component.scss']
})
export class ConfirmationComponent implements OnDestroy {
    /**
     * ** ViewContainerRef reference that is used as point where Message component could be inserted,
     *      and that Component is provided from invoker.
     *
     *      - Reference is contextual and unique for every confirmation message.
     */
    @ViewChild('confirmationMessageComponent', { read: ViewContainerRef, static: true })
    public readonly viewContainerRef: ViewContainerRef;

    /**
     * ** Model provided to component
     *
     *      - It instructs view rendering and behavior.
     *      - Provided handler is invoked when User interact with Confirmation view, whether its confirm or cancel (dismiss).
     */
    @Input() model: ConfirmationModelImpl = {} as ConfirmationModelImpl;

    /**
     * ** Whether User opt-out from future confirmation with the same context.
     *
     *      - Only when model instructs such field to be rendered, otherwise it's by default FALSE.
     */
    doNotShowFutureConfirmation = false;

    /**
     * ** Flag that is set to TRUE when User interact with Confirmation view, whether it is Confirm or Dismiss.
     * @private
     */
    private _componentInteracted = false;

    /**
     * ** User give confirmation, propagate model to invoker.
     */
    confirm($event: MouseEvent): void {
        $event.preventDefault();

        this._componentInteracted = true;

        this.model.handler.confirm({
            doNotShowFutureConfirmation: this.doNotShowFutureConfirmation
        });
    }

    /**
     * ** User cancel (dismiss) confirmation, propagate reason to invoker that it's on User behalf.
     */
    cancel($event: MouseEvent): void {
        $event.preventDefault();

        this._componentInteracted = true;

        this.model.handler.dismiss('Confirmation canceled on User behalf');
    }

    /**
     * @inheritDoc
     */
    ngOnDestroy(): void {
        if (this._componentInteracted) {
            return;
        }

        this.model.handler.dismiss(new Error(ERROR_CODE_CONFIRMATION_FORCEFULLY_DESTROYED_COMPONENT));
    }
}
