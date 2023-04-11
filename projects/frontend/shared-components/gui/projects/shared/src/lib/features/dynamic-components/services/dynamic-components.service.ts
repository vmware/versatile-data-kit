/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentRef, Injectable, OnDestroy, ViewContainerRef, ViewRef } from '@angular/core';

import { CollectionsUtil } from '../../../utils';

import { TaurusObject } from '../../../common';

import { DynamicContainerComponent, DynamicContextComponent } from '../components';

/**
 * ** Internal service model.
 */
interface AcquireViewContainerRefModel {
    /**
     * ** ViewContainerRef uuid.
     *
     *      - ViewContainerRefs could be reused by providing issued UUID.
     *      - References are stored in the service Map where for every issued UUID key there is ViewContainerRef behind as value.
     */
    uuid: string;

    /**
     * ** Unique ViewContainerRef created on behalf of the invoker.
     */
    viewContainerRef: ViewContainerRef;

    /**
     * ** ViewRef to the unique ViewContainerRef created on behalf of the invoker.
     */
    hostView: ViewRef;
}

/**
 * ** Dynamic Components Service that generates ViewContainerRefs in context that could be used once or reused multiple times.
 */
@Injectable()
export class DynamicComponentsService extends TaurusObject implements OnDestroy {
    /**
     * @inheritDoc
     */
    static override readonly CLASS_NAME: string = 'DynamicComponentsService';

    /**
     * ** Acquired ViewContainerRef with dependency injection during service initialization {@link DynamicComponentsService.initialize},
     *      where Dynamic Container {@link DynamicContainerComponent} will be inserted.
     * @private
     */
    private _appRootViewContainerRef: ViewContainerRef;

    /**
     * ** Dynamic Container reference {@link DynamicContainerComponent},
     *      where all contextual Dynamic components {@link DynamicContextComponent} will be inserted.
     * @private
     */
    private _dynamicContainerRef: ComponentRef<DynamicContainerComponent>;

    /**
     * ** Local store where all created Dynamic Context Components are stored under their corresponding issued UUID.
     * @private
     */
    private readonly _uniqueComponentRefsStore: Map<string, ComponentRef<DynamicContextComponent>>;

    /**
     * ** Constructor.
     */
    constructor() {
        super(DynamicComponentsService.CLASS_NAME);

        this._uniqueComponentRefsStore = new Map<string, ComponentRef<DynamicContextComponent>>();
    }

    /**
     * ** Create or retrieve unique ViewContainerRef together with ViewRef and bound UUID.
     *
     *      - if UUID is provided it will try to retrieve such reference if exists,
     *              otherwise will create new ViewContainerRef which will be stored under provided UUID key.
     *      - if no UUID provided will proceed to issue new UUID,
     *              then will create new ViewContainerRef which will be stored under the issued UUID,
     *              and both together with ViewRef will be returned to the invoker according provided return interface.
     *      - if some error is thrown in process of ViewContainerRef acquisition,
     *              service will return <code>null</code> instead of reference and that should be handled on invoker side.
     *      - Currently there is no automatic garbage collection, but only manual destroy utilizing {@link this.destroyUniqueViewContainerRef},
     *              so be careful not to acquire too many unique ViewContainerRef references,
     *              because they could downgrade Application performance (they are created as Component instances in root of the application).
     *      - Automatic GC is not currently developed because there is possibility to retrieve existing
     *              contextual ViewContainerRef instances with issued UUIDs for re-usage,
     *              or created instances refs could be kept into the invoker scope (context),
     *              or instances refs could be destroyed using the provided method with issued UUIDs {@link this.destroyUniqueViewContainerRef}
     */
    getUniqueViewContainerRef(requestedUUID?: string): AcquireViewContainerRefModel {
        const isContainerComponentSuccessfullyCreated = this._createDynamicContainerComponent();
        if (!isContainerComponentSuccessfullyCreated) {
            return null;
        }

        const isContainerComponentHealthy = this._validateDynamicContainerComponent();
        if (!isContainerComponentHealthy) {
            return null;
        }

        const uuid = DynamicComponentsService._getOrGenerateUUID(requestedUUID);

        if (!this._uniqueComponentRefsStore.has(uuid)) {
            const isContextComponentSuccessfullyCreated = this._createDynamicContextComponent(uuid);
            if (!isContextComponentSuccessfullyCreated) {
                return null;
            }
        }

        const isContextComponentHealthy = this._validateDynamicContextComponent(uuid);
        if (!isContextComponentHealthy) {
            return null;
        }

        return {
            uuid: uuid,
            viewContainerRef: this._uniqueComponentRefsStore.get(uuid).instance.viewContainerRef,
            hostView: this._uniqueComponentRefsStore.get(uuid).hostView
        };
    }

    /**
     * ** Destroy unique ViewContainerRef for provided UUID.
     *
     *      - If reference is found for provided UUID and is successfully destroyed will return true otherwise false.
     *      - If reference for provided UUID is not found will return null.
     */
    destroyUniqueViewContainerRef(uuid: string): boolean {
        if (!this._uniqueComponentRefsStore.has(uuid)) {
            return null;
        }

        try {
            this._uniqueComponentRefsStore.get(uuid).destroy();
            this._uniqueComponentRefsStore.delete(uuid);

            return true;
        } catch (e) {
            console.error(
                `${DynamicComponentsService.CLASS_NAME}: Potential bug found, Failed to destroy unique ViewContainerRef instance in DynamicContextComponent`
            );

            return false;
        }
    }

    /**
     * ** Initialize service.
     *
     *      - Should be invoked only once.
     *      - Ideal place for invoking is <code>AppComponent.ngOnInit()</code>.
     */
    initialize(viewContainerRef: ViewContainerRef): void {
        this._appRootViewContainerRef = viewContainerRef;
    }

    /**
     * @inheritDoc
     */
    override ngOnDestroy(): void {
        this._clearUniqueComponentsRef();
        this._clearContextContainerRef();
        this._clearAppRootViewContainerRef();

        super.ngOnDestroy();
    }

    private _createDynamicContainerComponent(): boolean {
        if (!this._appRootViewContainerRef) {
            return false;
        }

        if (this._dynamicContainerRef && this._dynamicContainerRef.hostView && !this._dynamicContainerRef.hostView.destroyed) {
            return true;
        }

        try {
            this._dynamicContainerRef = this._appRootViewContainerRef.createComponent(DynamicContainerComponent);
            this._dynamicContainerRef.changeDetectorRef.detectChanges();

            return true;
        } catch (e) {
            console.error(
                `${DynamicComponentsService.CLASS_NAME}: Potential bug found, Failed to create instance of DynamicContainerComponent`
            );

            return false;
        }
    }

    private _validateDynamicContainerComponent(): boolean {
        if (!(this._dynamicContainerRef && this._dynamicContainerRef.instance && this._dynamicContainerRef.instance.viewContainerRef)) {
            console.error(
                `${DynamicComponentsService.CLASS_NAME}: Potential bug found, Service is not initialized correctly ` +
                    `or during initialization failed to create instance of DynamicContainerComponent`
            );

            return false;
        }

        return true;
    }

    private _createDynamicContextComponent(uuid: string): boolean {
        try {
            const uniqueDynamicComponentRef = this._dynamicContainerRef.instance.viewContainerRef.createComponent(DynamicContextComponent);
            uniqueDynamicComponentRef.changeDetectorRef.detectChanges();
            this._uniqueComponentRefsStore.set(uuid, uniqueDynamicComponentRef);

            return true;
        } catch (e) {
            console.error(
                `${DynamicComponentsService.CLASS_NAME}: Potential bug found, Failed to create instance of DynamicContextComponent`
            );

            return false;
        }
    }

    private _validateDynamicContextComponent(uuid: string): boolean {
        const retrievedComponentRef = this._uniqueComponentRefsStore.get(uuid);
        if (!(retrievedComponentRef && retrievedComponentRef.instance && retrievedComponentRef.instance.viewContainerRef)) {
            console.error(
                `${DynamicComponentsService.CLASS_NAME}: Potential bug found, Failed to retrieve context instance of DynamicContextComponent`
            );

            return false;
        }

        return true;
    }

    private _clearUniqueComponentsRef(): void {
        this._uniqueComponentRefsStore.forEach((componentRef, uuid) => {
            try {
                if (!componentRef.hostView.destroyed) {
                    componentRef.destroy();
                }
            } catch (e) {
                console.error(
                    `${DynamicComponentsService.CLASS_NAME}: Potential bug found, failed to destroy unique component ref ${uuid}`
                );
            }
        });

        this._uniqueComponentRefsStore.clear();
    }

    private _clearContextContainerRef(): void {
        try {
            this._dynamicContainerRef.destroy();
        } catch (e) {
            console.error(`${DynamicComponentsService.CLASS_NAME}: Potential bug found, failed to destroy DynamicContextContainer ref`);
        }

        this._dynamicContainerRef = null;
    }

    private _clearAppRootViewContainerRef(): void {
        try {
            this._appRootViewContainerRef.clear();
        } catch (e) {
            console.error(`${DynamicComponentsService.CLASS_NAME}: Potential bug found, failed to destroy root ViewContainerRef`);
        }

        this._appRootViewContainerRef = null;
    }

    private static _getOrGenerateUUID(uuid: string): string {
        return uuid ?? CollectionsUtil.generateUUID();
    }
}
