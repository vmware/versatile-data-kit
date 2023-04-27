/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentRef, Injectable, OnDestroy, ViewContainerRef, ViewRef } from '@angular/core';

import { CollectionsUtil } from '../../../utils';

import { TaurusObject } from '../../../common';

import { DynamicComponentsService } from '../../dynamic-components';

import { ConfirmationInputModel, ConfirmationOutputModel } from '../model';
import { ConfirmationModelImpl, ERROR_CODE_CONFIRMATION_FORCEFULLY_DESTROYED_COMPONENT } from '../model/confirmation.model';

import { ConfirmationComponent, ConfirmationContainerComponent } from '../components';

/**
 * ** Confirmation Service that create confirmation view for every confirm request,
 *      and upon User action Confirm/Reject returns flow to the Invoker.
 *
 *      - Utilizes <code>Promise<ConfirmationOutputModel></code> for communication.
 */
@Injectable()
export class ConfirmationService extends TaurusObject implements OnDestroy {
    /**
     * @inheritDoc
     */
    static override readonly CLASS_NAME: string = 'ConfirmationService';

    /**
     * ** Acquired ViewContainerRef from {@link DynamicComponentsService},
     *      where Confirmation Container {@link ConfirmationContainerComponent} will be inserted.
     * @private
     */
    private _acquiredViewContainerRef: { uuid: string; viewContainerRef: ViewContainerRef; hostView: ViewRef };

    /**
     * ** Confirmation Container reference {@link ConfirmationContainerComponent},
     *      where all contextual Confirmation components {@link ConfirmationComponent} will be inserted.
     * @private
     */
    private _confirmationContainerRef: ComponentRef<ConfirmationContainerComponent>;

    /**
     * ** Constructor.
     */
    constructor(private readonly dynamicComponentsService: DynamicComponentsService) {
        super(ConfirmationService.CLASS_NAME);
    }

    /**
     * ** Show confirm view according the provided model instructions, and return flow to the invoker upon User action Confirm/Reject.
     *
     *      - Utilizes <b><code>Promise<ConfirmationOutputModel></code></b> for communication.
     *      - Sets some default values if model instructions are incomplete because most of them are optional.
     */
    confirm(model: ConfirmationInputModel): Promise<ConfirmationOutputModel> {
        const modelImpl = new ConfirmationModelImpl(model);
        const promise = new Promise<ConfirmationOutputModel>((resolve, reject) => {
            modelImpl.handler.confirm = resolve;
            modelImpl.handler.dismiss = reject;
        });

        const acquireViewContainerRefStatus = this._acquireDynamicViewContainerRef();
        if (!acquireViewContainerRefStatus.status) {
            return Promise.reject(new Error(acquireViewContainerRefStatus.error));
        }

        const createConfContainerComponentStatus = this._createConfirmationContainerComponent();
        if (!createConfContainerComponentStatus.status) {
            return Promise.reject(new Error(createConfContainerComponentStatus.error));
        }

        const createConfComponentStatus = this._createConfirmationComponent(modelImpl);
        if (!createConfComponentStatus.status) {
            return Promise.reject(new Error(createConfComponentStatus.error));
        }

        if (!this._confirmationContainerRef.instance.open) {
            this._confirmationContainerRef.instance.open = true;
            this._confirmationContainerRef.changeDetectorRef.detectChanges();
        }

        return promise
            .catch((reason: ConfirmationOutputModel) => {
                if (reason instanceof Error && reason.message === ERROR_CODE_CONFIRMATION_FORCEFULLY_DESTROYED_COMPONENT) {
                    console.error(
                        `${ConfirmationService.CLASS_NAME}: Potential bug found, views where destroyed externally from unknown source`
                    );
                }

                throw reason;
            })
            .finally(() => {
                this._clearSingleConfirmationResources(createConfComponentStatus as { componentRef: ComponentRef<ConfirmationComponent> });
            });
    }

    /**
     * ** Initialize service.
     *
     *      - Should be invoked only once.
     *      - Ideal place for invoking is <code>AppComponent.ngOnInit()</code>.
     */
    initialize(): void {
        // No-op.
    }

    /**
     * @inheritDoc
     */
    override ngOnDestroy(): void {
        this._clearResources();

        super.ngOnDestroy();
    }

    private _acquireDynamicViewContainerRef(): { status: boolean; error?: string } {
        if (this._isAcquiredViewContainerRefUnhealthy()) {
            this._clearResources();
        }

        if (!this._acquiredViewContainerRef) {
            const acquiredViewContainerRef = this.dynamicComponentsService.getUniqueViewContainerRef();
            if (!acquiredViewContainerRef) {
                const errorMessage = `${ConfirmationService.CLASS_NAME}: Potential bug found, cannot acquire unique ViewContainerRef where to insert confirmation Views`;
                console.error(errorMessage);

                return {
                    status: false,
                    error: errorMessage
                };
            }

            this._acquiredViewContainerRef = acquiredViewContainerRef;
        }

        return {
            status: true
        };
    }

    private _createConfirmationContainerComponent(): { status: boolean; error?: string } {
        if (!this._confirmationContainerRef) {
            try {
                this._confirmationContainerRef =
                    this._acquiredViewContainerRef.viewContainerRef.createComponent(ConfirmationContainerComponent);
                this._confirmationContainerRef.changeDetectorRef.detectChanges();
            } catch (e) {
                const errorMessage = `${ConfirmationService.CLASS_NAME}: Potential bug found, Failed to create instance of ConfirmationContainerComponent`;
                console.error(errorMessage);

                return {
                    status: false,
                    error: errorMessage
                };
            }
        }

        return {
            status: true
        };
    }

    private _createConfirmationComponent(model: ConfirmationModelImpl): {
        status: boolean;
        componentRef?: ComponentRef<ConfirmationComponent>;
        error?: string;
    } {
        try {
            const confirmationComponentRef =
                this._confirmationContainerRef.instance.viewContainerRef.createComponent(ConfirmationComponent);

            const assignMessageAndModelStatus = ConfirmationService._assignMessageAndModel(confirmationComponentRef, model);

            if (!assignMessageAndModelStatus.status) {
                console.error(assignMessageAndModelStatus.error);

                return {
                    status: false,
                    error: assignMessageAndModelStatus.error
                };
            }

            confirmationComponentRef.changeDetectorRef.detectChanges();

            return {
                status: true,
                componentRef: confirmationComponentRef
            };
        } catch (e) {
            const errorMessage = `${ConfirmationService.CLASS_NAME}: Potential bug found, Failed to create instance of ConfirmationComponent`;
            console.error(errorMessage);

            return {
                status: false,
                error: errorMessage
            };
        }
    }

    private _isAcquiredViewContainerRefUnhealthy(): boolean {
        return (
            this._acquiredViewContainerRef && this._acquiredViewContainerRef.hostView && this._acquiredViewContainerRef.hostView.destroyed
        );
    }

    private _refineConfirmationContainerVisibility(forceHide = false): void {
        if (this._confirmationContainerRef.instance.viewContainerRef.length === 0 || forceHide) {
            this._confirmationContainerRef.instance.open = false;
            this._confirmationContainerRef.changeDetectorRef.detectChanges();
        }
    }

    private _clearSingleConfirmationResources(internalModelRef: { componentRef: ComponentRef<ConfirmationComponent> }): void {
        try {
            const foundViewRefIndex = this._confirmationContainerRef.instance.viewContainerRef.indexOf(
                internalModelRef.componentRef.hostView
            );
            if (foundViewRefIndex !== -1) {
                this._confirmationContainerRef.instance.viewContainerRef.remove(foundViewRefIndex);
            }

            if (!internalModelRef.componentRef.hostView.destroyed) {
                internalModelRef.componentRef.destroy();
            }

            internalModelRef.componentRef = null;

            this._refineConfirmationContainerVisibility();

            return;
        } catch (e) {
            console.error(`${ConfirmationService.CLASS_NAME}: Potential bug found, failed to cleanup confirmation views after User action`);
        }

        try {
            this._refineConfirmationContainerVisibility(true);
        } catch (e) {
            console.error(`${ConfirmationService.CLASS_NAME}: Potential bug found, failed to force container to hide`);
        }
    }

    private _clearResources(): void {
        try {
            if (this._confirmationContainerRef?.hostView && !this._confirmationContainerRef.hostView.destroyed) {
                this._confirmationContainerRef.destroy();
            }
        } catch (e) {
            console.error(
                `${ConfirmationService.CLASS_NAME}: Potential bug found, failed to destroy ConfirmationContainerComponent reference`
            );
        }

        this._confirmationContainerRef = null;

        if (!this._acquiredViewContainerRef) {
            return;
        }

        try {
            this._acquiredViewContainerRef.viewContainerRef.clear();
        } catch (e) {
            console.error(`${ConfirmationService.CLASS_NAME}: Potential bug found, failed to clear views in acquired ViewContainerRef`);
        }

        this.dynamicComponentsService.destroyUniqueViewContainerRef(this._acquiredViewContainerRef.uuid);

        this._acquiredViewContainerRef = null;
    }

    private static _assignMessageAndModel(
        confirmationComponentRef: ComponentRef<ConfirmationComponent>,
        model: ConfirmationModelImpl
    ): { status: boolean; error?: string } {
        let isMessageComponentCreated = false;

        if (CollectionsUtil.isDefined(model.messageComponent)) {
            try {
                const messageComponentRef = confirmationComponentRef.instance.viewContainerRef.createComponent(model.messageComponent);

                isMessageComponentCreated = true;

                if (CollectionsUtil.isStringWithContent(model.messageCode)) {
                    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
                    messageComponentRef.instance.messageCode = model.messageCode;
                }
            } catch (e) {
                const errorMessage = `${ConfirmationService.CLASS_NAME}: Potential bug found, Failed to create Component instance for Confirmation Message`;
                console.error(errorMessage);

                return {
                    status: false,
                    error: errorMessage
                };
            }
        }

        confirmationComponentRef.instance.model = new ConfirmationModelImpl({
            ...model,
            messageComponent: undefined,
            messageCode: undefined,
            message: isMessageComponentCreated ? undefined : model.message
        });

        return {
            status: true
        };
    }
}
