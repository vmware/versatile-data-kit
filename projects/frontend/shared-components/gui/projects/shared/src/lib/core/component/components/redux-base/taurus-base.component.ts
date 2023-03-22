/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @angular-eslint/directive-class-suffix */

import { Directive, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Params } from '@angular/router';

import { Subscription } from 'rxjs';

import { ArrayElement, CollectionsUtil } from '../../../../utils';

import { ErrorRecord, TaurusNavigateAction } from '../../../../common';

import { NavigationService } from '../../../navigation';
import { RouteStateFactory } from '../../../router/factory';

import { ComponentModel, FAILED } from '../../model';
import { ComponentService } from '../../services';

import { TaurusErrorBaseComponent } from '../error-base';

import { TaurusComponentHooks } from './interfaces';

/**
 * ** Superclass Component for all other Components that want to use NgRx Store and all lifecycle hooks from Taurus.
 */
@Directive()
export abstract class TaurusBaseComponent extends TaurusErrorBaseComponent implements OnInit, OnDestroy {
    /**
     * @inheritDoc
     */
    static override readonly CLASS_NAME: string = 'TaurusBaseComponent';

    /**
     * @inheritDoc
     */
    static override readonly PUBLIC_NAME: string = 'Taurus-Base-Component';

    private static _routeStateFactory: RouteStateFactory;

    /**
     * ** Field that hold Component Model.
     */
    model: ComponentModel;

    /**
     * ** UUID is identifier for every Subclass in Components state Store.
     */
    abstract readonly uuid: string;

    /**
     * ** Feature flag to enforce Route reuse in native way provided from Taurus NgRx.
     *
     *      - Introduced for backward compatibility.
     *      - Default value is false, and continues to operate like previous major version.
     *      - If set to true will enforce Route reuse strategy and will re-initialize Component with new Model for the new params.
     */
    enforceRouteReuse = false;

    /**
     * ** Model subscription ref.
     * @private
     */
    private _modelSubscription: Subscription;

    /**
     * ** Constructor.
     */
    protected constructor(
        protected readonly componentService: ComponentService,
        protected readonly navigationService: NavigationService,
        protected readonly activatedRoute: ActivatedRoute,
        className: string = null
    ) {
        super(className ?? TaurusBaseComponent.CLASS_NAME);
    }

    /**
     * ** Navigate to page using {@link NavigationService.navigateTo}.
     */
    navigateTo(replaceValues?: { [key: string]: ArrayElement<TaurusNavigateAction['replacers']>['replaceValue'] }): Promise<boolean> {
        return this.navigationService.navigateTo(replaceValues);
    }

    /**
     * ** Navigate back to previous page using {@link NavigationService.navigateBack}.
     */
    navigateBack(replaceValues?: { [key: string]: ArrayElement<TaurusNavigateAction['replacers']>['replaceValue'] }): Promise<boolean> {
        return this.navigationService.navigateBack(replaceValues);
    }

    /**
     * @inheritDoc
     */
    ngOnInit() {
        this.bindModel();

        this.initializeRouteReuse();
    }

    /**
     * @inheritDoc
     */
    override ngOnDestroy() {
        this.setStateIdle();

        super.ngOnDestroy();
    }

    /**
     * ** Invoking method register subscriber for Taurus NgRx Redux Store mutation in context of {@link ComponentState.routePathSegments},
     *      which binds {@link ComponentModel} to {@link TaurusBaseComponent.model}
     *      and start invocation of Taurus NgRx Redux Component lifecycle hooks.
     *
     *      <b>Invocation order:</b>
     *
     *      1. {@link OnTaurusModelInit}
     *      2. {@link OnTaurusModelInitialLoad} or {@link OnTaurusModelFirstLoad} - only one could be invoke,
     *              where deprecated shouldn't be implemented anymore.
     *      3. {@link OnTaurusModelLoad}
     *      4. {@link OnTaurusModelChange} when status is {@link LOADED}
     *      5. {@link OnTaurusModelError} or {@link OnTaurusModelFail} when status is {@link FAILED} - only one could be invoke,
     *              where deprecated shouldn't be implemented anymore.
     *
     *      <p>
     *          <br>
     *          Override it if you want to change default behavior.
     *      </p>
     *
     * @protected
     */
    protected bindModel(): void {
        let isOnModelInitialLoadExecuted = false;

        if (!TaurusBaseComponent._routeStateFactory) {
            TaurusBaseComponent._routeStateFactory = new RouteStateFactory();
        }

        const routeState = TaurusBaseComponent._routeStateFactory.create(this.activatedRoute.snapshot, null);

        this.componentService.init(this.uuid, routeState).subscribe((model) => {
            this.model = model;

            TaurusBaseComponent._executeTaurusComponentHook(this, 'onModelInit', model);
        });

        this._modelSubscription = this.componentService.getModel(this.uuid, routeState.routePathSegments).subscribe((model) => {
            if (!isOnModelInitialLoadExecuted) {
                isOnModelInitialLoadExecuted = true;
                if (!TaurusBaseComponent._executeTaurusComponentHook(this, 'onModelInitialLoad', model)) {
                    TaurusBaseComponent._executeTaurusComponentHook(this, 'onModelFirstLoad', model);
                }
            }

            this.evaluateTaurusComponentLifecycleHooks(model);
        });

        this.subscriptions.push(this._modelSubscription);
    }

    /**
     * ** Evaluates Taurus NgRx Redux Component lifecycle hooks
     *      ({@link OnTaurusModelLoad} and {@link OnTaurusModelChange} and ({@link OnTaurusModelFail} or {@link OnTaurusModelError})).
     *
     *      - Override it if you want to change default behavior.
     *
     * @protected
     */
    protected evaluateTaurusComponentLifecycleHooks(model: ComponentModel): void {
        TaurusBaseComponent._executeTaurusComponentHook(this, 'onModelLoad', model);

        if (!this.isModelModified(model)) {
            return;
        }

        const previousModel = this.model;

        this.refreshModel(model);

        if (model.status === FAILED) {
            const previousErrorRecords: ErrorRecord[] =
                previousModel instanceof ComponentModel ? previousModel.getComponentState().errors.records : [];
            const distinctErrorRecordsFromPreviousCycle = model.getComponentState().errors.distinctErrorRecords(previousErrorRecords);

            if (!TaurusBaseComponent._executeTaurusComponentHook(this, 'onModelError', model, distinctErrorRecordsFromPreviousCycle)) {
                TaurusBaseComponent._executeTaurusComponentHook(this, 'onModelFail', model);
            }
        } else {
            TaurusBaseComponent._executeTaurusComponentHook(this, 'onModelChange', model);
        }

        try {
            this.normalizeModelState(model);
        } catch (e) {
            console.error(`Taurus NgRx Redux failed to normalize ComponentModel!`, e);
        }
    }

    /**
     * ** Refresh model field {@link TaurusBaseComponent.model} with new one,
     *      and assigns previous model reference to field {@link ComponentModel.previousModel} in the new model,
     *      to the max depth 3.
     *
     *      - All assignments are by reference.
     *      - Override it if you want to change default behavior.
     *      - <b>Be cautious about your changes and intents!</b> It could affect features thar depend on this method Impl.
     *
     * @protected
     */
    protected refreshModel(model: ComponentModel): void {
        // purge component ErrorStore with data from ComponentModel ErrorStore
        this.errors.purge(model.getComponentState().errors);

        // assign current model as previous to the new one
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        model['previousModel'] = this.model; // eslint-disable-line @typescript-eslint/dot-notation

        // clean previous models that exceed max depth 3
        try {
            let depthLevel = 1;
            let previousModel = model.previousModel;

            while (previousModel instanceof ComponentModel) {
                if (++depthLevel <= 3) {
                    previousModel = previousModel.previousModel;
                } else {
                    if (previousModel.previousModel) {
                        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
                        // @ts-ignore
                        delete previousModel['previousModel']; // eslint-disable-line @typescript-eslint/dot-notation
                    }

                    break;
                }
            }
        } catch (e) {
            console.error('Failed to clean previous ComponentModel', e);
        }

        // assign model as current
        this.model = model;
    }

    /**
     * ** Normalize Model state, by default it clear Task field in {@link ComponentState.task} and update model in Taurus NgRx Redux Store.
     *
     *      - It is invoked only if {@link ComponentModel} is modified and after invocation of all Taurus components lifecycle hooks.
     *      - Override it if you want to change default behavior.
     *
     * @protected
     */
    protected normalizeModelState(model: ComponentModel): void {
        this.componentService.update(model.clearTask().getComponentState());
    }

    /**
     * ** Set Model state in IDLE to stop listening on Events from Store.
     *
     *      - It is invoked by default before Component is destroyed, in Angular lifecycle hook {@link OnDestroy}.
     *      - Override it if you want to change default behavior.
     *
     * @protected
     */
    protected setStateIdle(): void {
        this.componentService.idle(this.model.prepareForDestroy().getComponentState());
    }

    /**
     * ** Evaluation of this method acknowledge that new {@link ComponentModel} is modified or not.
     *
     *      - Comparison is evaluated between provided Model and assigned Component's Model {@link TaurusBaseComponent.model}.
     *      - Default implementation use {@link ComponentModel.isModified} for deep Comparison of specific fields.
     *      - Override it if you want to change default behavior.
     *
     * <p>
     *      <b>Be cautious about your changes and intents!</b>
     *      Examples what can wrong comparison do?
     * </p>
     *
     *      1. Infinite lifecycle hooks invocation, where consequences are: performance deterioration or application freeze.
     *      2. Prevent lifecycle hooks invocation, where consequences are: your Data never arrive to your Component fields.
     *
     * @protected
     */
    protected isModelModified(model: ComponentModel): boolean {
        return model.isModified(this.model);
    }

    /**
     * ** Initialize Route reuse strategy for Component in context of Taurus NgRx.
     *      - Turns on listener for Activated params change and if detects mutation
     *              sets current model in current RoutePathSegment to idle,
     *              and bind for new model stream to the new RoutePathSegment.
     *      - New feature this is completely backward compatible,
     *              and it can be turned on with feature flag per Component Class.
     *
     * @protected
     */
    protected initializeRouteReuse(): void {
        if (!this.enforceRouteReuse) {
            return;
        }

        let previousParams: Params;

        this.subscriptions.push(
            this.activatedRoute.params.subscribe((params) => {
                if (CollectionsUtil.isNil(previousParams)) {
                    previousParams = params;

                    return;
                }

                if (!CollectionsUtil.isEqual(previousParams, params)) {
                    previousParams = params;

                    const isRemoveSuccessful = this.removeSubscriptionRef(this._modelSubscription);
                    if (isRemoveSuccessful) {
                        // set current RoutePathSegment model state to idle
                        this.setStateIdle();
                        // bind new model stream to new RoutePathSegment
                        this.bindModel();
                    }
                }
            })
        );
    }

    /**
     * ** Invoke Taurus NgRx Redux Component lifecycle hook.
     *
     *      - Lifecycle hooks are invoked only if implementation they are found as implemented in subclasses.
     *      - Returns true if method is found and executed, otherwise false.
     *
     * @private
     */
    // eslint-disable-next-line @typescript-eslint/member-ordering
    private static _executeTaurusComponentHook(
        instance: TaurusBaseComponent,
        method: keyof TaurusComponentHooks,
        model: ComponentModel,
        ...additionalParams: any[]
    ): boolean {
        // eslint-disable-line @typescript-eslint/no-explicit-any

        if (CollectionsUtil.isFunction(instance[method])) {
            const currentTask = model.getTask();

            try {
                if (CollectionsUtil.isString(currentTask)) {
                    // eslint-disable-next-line @typescript-eslint/no-unsafe-call
                    instance[method](model, currentTask, ...additionalParams);
                } else {
                    // eslint-disable-next-line @typescript-eslint/no-unsafe-call
                    instance[method](model, undefined, ...additionalParams);
                }
            } catch (e) {
                console.error(`Taurus NgRx Redux failed to execute lifecycle hook "${method}"!`, e);
            }

            return true;
        }

        return false;
    }
}
