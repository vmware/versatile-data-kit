/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/dot-notation,@typescript-eslint/no-unsafe-argument */

import { Component, CUSTOM_ELEMENTS_SCHEMA, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, ActivatedRouteSnapshot, Params } from '@angular/router';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BehaviorSubject, of } from 'rxjs';
import { take } from 'rxjs/operators';

import { CallFake } from '../../../../unit-testing';

import { CollectionsUtil } from '../../../../utils';

import { ErrorRecord, TaurusObject } from '../../../../common';

import { RouteState } from '../../../router';
import { RouteStateFactory } from '../../../router/factory';

import { NavigationService } from '../../../navigation';

import { ComponentModel, ComponentState, FAILED, LOADED } from '../../model';
import { ComponentService } from '../../services';

import {
    OnTaurusModelChange,
    OnTaurusModelError,
    OnTaurusModelFail,
    OnTaurusModelFirstLoad,
    OnTaurusModelInit,
    OnTaurusModelInitialLoad,
    OnTaurusModelLoad
} from './interfaces';

import { TaurusBaseComponent } from './taurus-base.component';

const errorRecord1: ErrorRecord = {
    code: 'ClassName_Public-Name_methodName_unknown',
    error: new Error('Error 1'),
    time: CollectionsUtil.dateNow(),
    objectUUID: 'objectUUID'
} as ErrorRecord;
const errorRecord2: ErrorRecord = {
    code: 'ClassName_Public-Name_methodName_unknown',
    error: new Error('Error 2'),
    time: CollectionsUtil.dateNow(),
    objectUUID: 'objectUUID'
} as ErrorRecord;
const errorRecord3: ErrorRecord = {
    code: 'ClassName_Public-Name_methodName_500',
    error: new Error('Error 3'),
    time: CollectionsUtil.dateNow(),
    objectUUID: 'objectUUID'
} as ErrorRecord;

@Component({
    selector: 'shared-taurus-base-subclass-component',
    template: ''
})
// eslint-disable-next-line @angular-eslint/component-class-suffix
class TaurusBaseComponentStub
    extends TaurusBaseComponent
    implements OnInit, OnDestroy, OnTaurusModelInit, OnTaurusModelLoad, OnTaurusModelFirstLoad, OnTaurusModelChange, OnTaurusModelFail
{
    uuid = 'TaurusBaseComponentStub';

    constructor(componentService: ComponentService, navigationService: NavigationService, activatedRoute: ActivatedRoute) {
        super(componentService, navigationService, activatedRoute);
    }

    onModelInit(_model?: ComponentModel, _task?: string) {
        // No-op.
    }

    onModelFirstLoad(_model?: ComponentModel, _task?: string) {
        // No-op.
    }

    onModelLoad(_model?: ComponentModel, _task?: string) {
        // No-op.
    }

    onModelChange(_model?: ComponentModel, _task?: string) {
        // No-op.
    }

    onModelFail(_model?: ComponentModel, _task?: string) {
        // No-op.
    }

    override ngOnInit() {
        super.ngOnInit();
    }

    override ngOnDestroy() {
        super.ngOnDestroy();
    }
}

@Component({
    selector: 'shared-taurus-base-subclass-component-v1',
    template: ''
})
// eslint-disable-next-line @angular-eslint/component-class-suffix
class TaurusBaseComponentStubV1 extends TaurusBaseComponentStub implements OnTaurusModelInitialLoad, OnTaurusModelError {
    override uuid = 'TaurusBaseComponentStubV1';

    override enforceRouteReuse = true;

    onModelInitialLoad(_model?: ComponentModel, _task?: string): void {
        // No-op.
    }

    onModelError(_model?: ComponentModel, _task?: string, _newErrorRecords?: ErrorRecord[]): void {
        // No-op.
    }
}

class ComponentModelStub extends ComponentModel {
    task: string;

    randomId = 0;

    constructor(task?: string, randomId?: number) {
        super(null, null);

        this.task = task;
        this.randomId = randomId;
    }

    get errors() {
        return {
            distinctErrorRecords: (_errorRecords: ErrorRecord[]) => {
                if (this.randomId === 1) {
                    return [];
                }

                if (this.randomId === 2) {
                    return [errorRecord1];
                }

                if (this.randomId === 3) {
                    return [errorRecord2, errorRecord3];
                }

                return [];
            },
            records: []
        };
    }

    override get status() {
        return null;
    }

    override isModified(): boolean {
        return null;
    }

    override withStatusIdle() {
        return this;
    }

    override prepareForDestroy() {
        return this;
    }

    override getComponentState() {
        return {
            errors: this.errors
        } as ComponentState;
    }

    override getTask() {
        return this.task;
    }

    override clearTask() {
        return this;
    }
}

class ComponentModelStubV1 extends ComponentModelStub {
    // @ts-ignore
    override get previousModel(): Readonly<ComponentModel> {
        return this._previousModel;
    }

    // @ts-ignore
    set previousModel(previousModel: Readonly<ComponentModel>) {
        this._previousModel = previousModel;
    }

    private _previousModel: Readonly<ComponentModel>;
}

describe('TaurusBaseComponent -> TaurusSubclassComponent', () => {
    let componentServiceStub: jasmine.SpyObj<ComponentService>;
    let navigationServiceStub: jasmine.SpyObj<NavigationService>;
    let activatedRouteStub: Partial<ActivatedRoute>;
    let activatedRouteSnapshotStub: ActivatedRouteSnapshot;
    let paramsSubject: BehaviorSubject<Params>;

    let routeStateStub: RouteState;

    let fixture: ComponentFixture<TaurusBaseComponentStub>;
    let component: TaurusBaseComponentStub;
    let modelStub: ComponentModel;

    beforeEach(() => {
        componentServiceStub = jasmine.createSpyObj<ComponentService>('componentService', ['init', 'idle', 'getModel', 'update']);
        navigationServiceStub = jasmine.createSpyObj<NavigationService>('navigationService', ['navigateTo', 'navigateBack']);
        activatedRouteSnapshotStub = {
            url: '',
            params: {},
            data: {}
        } as any;
        paramsSubject = new BehaviorSubject<Params>({ name: 'Ina', asset: 2 });
        activatedRouteStub = { snapshot: activatedRouteSnapshotStub, params: paramsSubject };
        routeStateStub = {
            routePathSegments: ['path1/path2', 'path3/path4']
        } as RouteState;
        spyOn(RouteStateFactory.prototype, 'create').and.returnValue(routeStateStub);

        modelStub = new ComponentModelStub() as any;

        TestBed.configureTestingModule({
            declarations: [TaurusBaseComponentStub, TaurusBaseComponentStubV1],
            providers: [
                { provide: ComponentService, useValue: componentServiceStub },
                { provide: NavigationService, useValue: navigationServiceStub },
                { provide: ActivatedRoute, useValue: activatedRouteStub }
            ],
            schemas: [CUSTOM_ELEMENTS_SCHEMA]
        });

        fixture = TestBed.createComponent(TaurusBaseComponentStub);
        component = fixture.componentInstance;
    });

    it('should verify component is created', () => {
        // Given
        component.model = modelStub;

        // Then
        expect(component).toBeDefined();
        expect(component).toBeInstanceOf(TaurusBaseComponentStub);
        expect(component).toBeInstanceOf(TaurusBaseComponent);
    });

    describe('Properties::', () => {
        describe('|uuid|', () => {
            it('should verify default value is undefined', () => {
                // Given
                component.model = modelStub;

                // When
                expect(component.uuid).toEqual('TaurusBaseComponentStub');
            });
        });

        describe('|componentService|', () => {
            it('should verify ComponentService will be injected', () => {
                // Given
                component.model = modelStub;

                // When
                expect(component['componentService']).toBeDefined();
            });
        });

        describe('|navigationService|', () => {
            it('should verify NavigationService will be injected', () => {
                // Given
                component.model = modelStub;

                // When
                expect(component['navigationService']).toBeDefined();
            });
        });

        describe('|activatedRoute|', () => {
            it('should verify ActivatedRoute will be injected', () => {
                // Given
                component.model = modelStub;

                // When
                expect(component['activatedRoute']).toBeDefined();
            });
        });
    });

    describe('Angular lifecycle hooks::', () => {
        beforeEach(() => {
            component.model = modelStub;
        });

        describe('|ngOnInit|', () => {
            it('should verify will invoke expected method', () => {
                // Given
                // @ts-ignore
                const bindModelSpy = spyOn(component, 'bindModel').and.callFake(CallFake);

                // When
                fixture.detectChanges();

                // Then
                expect(bindModelSpy).toHaveBeenCalled();

                // Post
                fixture.componentInstance.model = modelStub;
            });
        });

        describe('|ngOnDestroy|', () => {
            it('should verify will invoke expected methods', () => {
                // Given
                spyOn(TaurusBaseComponent.prototype, 'ngOnInit').and.callFake(CallFake);
                // @ts-ignore
                const setIdleSpy: jasmine.Spy<() => void> = spyOn(TaurusBaseComponent.prototype, 'setStateIdle').and.callFake(CallFake);
                const ngOnDestroySpy: jasmine.Spy<() => void> = spyOn(TaurusObject.prototype, 'ngOnDestroy').and.callFake(CallFake);

                // When
                fixture = TestBed.createComponent(TaurusBaseComponentStub);
                fixture.componentInstance.model = modelStub;
                fixture.detectChanges();
                fixture.destroy();

                // Then
                expect(setIdleSpy).toHaveBeenCalled();
                expect(ngOnDestroySpy).toHaveBeenCalled();
            });
        });
    });

    describe('Methods::', () => {
        describe('|navigateTo|', () => {
            it('should verify will invoke correct methods', () => {
                // Given
                const replaceValues = { '$.team': 'team1', '$.entity': 'Prime' };
                navigationServiceStub.navigateTo.and.returnValue(Promise.resolve(true));
                component.model = modelStub;

                // When
                const promise = component.navigateTo(replaceValues);

                // Then
                expect(promise).toBeInstanceOf(Promise);
                expect(navigationServiceStub.navigateTo).toHaveBeenCalledWith(replaceValues);
            });
        });

        describe('|navigateBack|', () => {
            it('should verify will invoke correct methods', () => {
                // Given
                const replaceValues = { '$.team': 'team10', '$.entity': 'Second' };
                navigationServiceStub.navigateBack.and.returnValue(Promise.resolve(false));
                component.model = modelStub;

                // When
                const promise = component.navigateBack(replaceValues);

                // Then
                expect(promise).toBeInstanceOf(Promise);
                expect(navigationServiceStub.navigateBack).toHaveBeenCalledWith(replaceValues);
            });
        });

        describe('|bindModel|', () => {
            it('should verify will create correct subscriptions', () => {
                // Given
                componentServiceStub.init.and.returnValue(of(modelStub).pipe(take(1)));
                componentServiceStub.getModel.and.returnValue(of(modelStub));

                // When
                // @ts-ignore
                component.bindModel();

                // Then 2
                expect(componentServiceStub.init).toHaveBeenCalledWith(component.uuid, routeStateStub);
                expect(componentServiceStub.getModel).toHaveBeenCalledWith(component.uuid, routeStateStub.routePathSegments);
                expect(component['subscriptions'].length).toEqual(1); // eslint-disable-line @typescript-eslint/no-unsafe-member-access
            });

            it('should verify will invoke correct Taurus lifecycle hooks for LOADED and modified', () => {
                // Given
                const onModelInitSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelInit').and.callFake(CallFake);
                const onModelFirstLoadSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelFirstLoad').and.callFake(CallFake);
                const onModelLoadSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelLoad').and.callFake(CallFake);
                const onModelChangeSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelChange').and.callFake(CallFake);
                const onModelFailSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelFail').and.callFake(CallFake);
                const isModelModifiedSpy = spyOn(modelStub, 'isModified').and.returnValue(true);
                const modelStatusSpy = spyOnProperty(modelStub, 'status', 'get').and.returnValue(LOADED);

                componentServiceStub.init.and.returnValue(of(modelStub));
                componentServiceStub.getModel.and.returnValue(of(modelStub));

                // Then 1
                expect(component.model).toBeUndefined();

                // When
                // @ts-ignore
                component.bindModel();

                // Then 2
                expect(component.model).toBe(modelStub);
                expect(onModelInitSpy).toHaveBeenCalledWith(modelStub, undefined);
                expect(onModelFirstLoadSpy).toHaveBeenCalledWith(modelStub, undefined);
                expect(onModelLoadSpy).toHaveBeenCalledWith(modelStub, undefined);
                expect(isModelModifiedSpy).toHaveBeenCalledWith(modelStub);
                expect(component.model).toBe(modelStub);
                expect(modelStatusSpy).toHaveBeenCalled();
                expect(onModelChangeSpy).toHaveBeenCalledWith(modelStub, undefined);
                expect(onModelFailSpy).not.toHaveBeenCalled();
            });

            it('should verify will invoke correct Taurus lifecycle hooks for LOADED and modified with Task', () => {
                // Given
                const task = 'delete_entity';
                modelStub = new ComponentModelStub(task) as any;
                const onModelInitSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelInit').and.callFake(CallFake);
                const onModelFirstLoadSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelFirstLoad').and.callFake(CallFake);
                const onModelLoadSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelLoad').and.callFake(CallFake);
                const onModelChangeSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelChange').and.callFake(CallFake);
                const onModelFailSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelFail').and.callFake(CallFake);
                const isModelModifiedSpy = spyOn(modelStub, 'isModified').and.returnValue(true);
                const modelStatusSpy = spyOnProperty(modelStub, 'status', 'get').and.returnValue(LOADED);

                componentServiceStub.init.and.returnValue(of(modelStub));
                componentServiceStub.getModel.and.returnValue(of(modelStub));

                // Then 1
                expect(component.model).toBeUndefined();

                // When
                // @ts-ignore
                component.bindModel();

                // Then 2
                expect(component.model).toBe(modelStub);
                expect(onModelInitSpy).toHaveBeenCalledWith(modelStub, task);
                expect(onModelFirstLoadSpy).toHaveBeenCalledWith(modelStub, task);
                expect(onModelLoadSpy).toHaveBeenCalledWith(modelStub, task);
                expect(isModelModifiedSpy).toHaveBeenCalledWith(modelStub);
                expect(component.model).toBe(modelStub);
                expect(modelStatusSpy).toHaveBeenCalled();
                expect(onModelChangeSpy).toHaveBeenCalledWith(modelStub, task);
                expect(onModelFailSpy).not.toHaveBeenCalled();
            });

            it('should verify will invoke correct Taurus lifecycle hooks for FAILED and modified deprecated', () => {
                // Given
                const onModelInitSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelInit').and.callFake(CallFake);
                const onModelFirstLoadSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelFirstLoad').and.callFake(CallFake);
                const onModelLoadSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelLoad').and.callFake(CallFake);
                const onModelChangeSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelChange').and.callFake(CallFake);
                const onModelFailSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelFail').and.callFake(CallFake);
                const isModelModifiedSpy = spyOn(modelStub, 'isModified').and.returnValue(true);
                const modelStatusSpy = spyOnProperty(modelStub, 'status', 'get').and.returnValue(FAILED);

                componentServiceStub.init.and.returnValue(of(modelStub));
                componentServiceStub.getModel.and.returnValue(of(modelStub));

                // Then 1
                expect(component.model).toBeUndefined();

                // When
                // @ts-ignore
                component.bindModel();

                // Then 2
                expect(component.model).toBe(modelStub);
                expect(onModelInitSpy).toHaveBeenCalledWith(modelStub, undefined);
                expect(onModelFirstLoadSpy).toHaveBeenCalledWith(modelStub, undefined);
                expect(onModelLoadSpy).toHaveBeenCalledWith(modelStub, undefined);
                expect(isModelModifiedSpy).toHaveBeenCalledWith(modelStub);
                expect(component.model).toBe(modelStub);
                expect(modelStatusSpy).toHaveBeenCalled();
                expect(onModelFailSpy).toHaveBeenCalledWith(modelStub, undefined);
                expect(onModelChangeSpy).not.toHaveBeenCalled();
            });

            it('should verify will invoke correct Taurus lifecycle hooks for FAILED and modified with Task deprecated', () => {
                // Given
                const task = 'patch_entity';
                modelStub = new ComponentModelStub(task) as any;
                const onModelInitSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelInit').and.callFake(CallFake);
                const onModelFirstLoadSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelFirstLoad').and.callFake(CallFake);
                const onModelLoadSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelLoad').and.callFake(CallFake);
                const onModelChangeSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelChange').and.callFake(CallFake);
                const onModelFailSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelFail').and.callFake(CallFake);
                const isModelModifiedSpy = spyOn(modelStub, 'isModified').and.returnValue(true);
                const modelStatusSpy = spyOnProperty(modelStub, 'status', 'get').and.returnValue(FAILED);

                componentServiceStub.init.and.returnValue(of(modelStub));
                componentServiceStub.getModel.and.returnValue(of(modelStub));

                // Then 1
                expect(component.model).toBeUndefined();

                // When
                // @ts-ignore
                component.bindModel();

                // Then 2
                expect(component.model).toBe(modelStub);
                expect(onModelInitSpy).toHaveBeenCalledWith(modelStub, task);
                expect(onModelFirstLoadSpy).toHaveBeenCalledWith(modelStub, task);
                expect(onModelLoadSpy).toHaveBeenCalledWith(modelStub, task);
                expect(isModelModifiedSpy).toHaveBeenCalledWith(modelStub);
                expect(component.model).toBe(modelStub);
                expect(modelStatusSpy).toHaveBeenCalled();
                expect(onModelFailSpy).toHaveBeenCalledWith(modelStub, task);
                expect(onModelChangeSpy).not.toHaveBeenCalled();
            });

            it('should verify will invoke correct Taurus lifecycle hooks for FAILED and modified', () => {
                // Given
                spyOn(TaurusBaseComponentStubV1.prototype, 'onModelInit').and.callFake(CallFake);
                spyOn(TaurusBaseComponentStubV1.prototype, 'onModelInitialLoad').and.callFake(CallFake);
                spyOn(TaurusBaseComponentStubV1.prototype, 'onModelLoad').and.callFake(CallFake);
                spyOn(TaurusBaseComponentStubV1.prototype, 'onModelChange').and.callFake(CallFake);
                const onModelErrorSpy = spyOn(TaurusBaseComponentStubV1.prototype, 'onModelError').and.callFake(CallFake);

                spyOn(modelStub, 'isModified').and.returnValue(true);
                spyOnProperty(modelStub, 'status', 'get').and.returnValue(FAILED);

                const modelStub1: ComponentModel = new ComponentModelStub(null, 1) as any;
                spyOn(modelStub1, 'isModified').and.returnValue(true);
                spyOnProperty(modelStub1, 'status', 'get').and.returnValue(FAILED);
                const modelStub2: ComponentModel = new ComponentModelStub(null, 2) as any;
                spyOn(modelStub2, 'isModified').and.returnValue(true);
                spyOnProperty(modelStub2, 'status', 'get').and.returnValue(FAILED);
                const modelStub3: ComponentModel = new ComponentModelStub(null, 3) as any;
                spyOn(modelStub3, 'isModified').and.returnValue(true);
                spyOnProperty(modelStub3, 'status', 'get').and.returnValue(FAILED);
                const modelStub4: ComponentModel = new ComponentModelStub(null, 4) as any;
                spyOn(modelStub4, 'isModified').and.returnValue(true);
                spyOnProperty(modelStub4, 'status', 'get').and.returnValue(FAILED);

                componentServiceStub.init.and.returnValue(of(modelStub));

                const modelSubject = new BehaviorSubject<ComponentModel>(modelStub1);
                componentServiceStub.getModel.and.returnValue(modelSubject);

                const component1: TaurusBaseComponentStubV1 = TestBed.createComponent(TaurusBaseComponentStubV1).componentInstance;

                // When
                // @ts-ignore
                component1.bindModel();
                // @ts-ignore
                component1.model = null;
                modelSubject.next(modelStub2);
                modelSubject.next(modelStub3);
                modelSubject.next(modelStub4);

                // Then
                expect(onModelErrorSpy.calls.argsFor(0)).toEqual([modelStub1, undefined, []]);
                expect(onModelErrorSpy.calls.argsFor(1)).toEqual([modelStub2, undefined, [errorRecord1]]);
                expect(onModelErrorSpy.calls.argsFor(2)).toEqual([modelStub3, undefined, [errorRecord2, errorRecord3]]);
                expect(onModelErrorSpy.calls.argsFor(3)).toEqual([modelStub4, undefined, []]);

                // Post
                component.model = modelStub;
                component1.model = modelStub;
            });

            it('should verify will invoke correct Taurus lifecycle hooks for FAILED and modified with Task', () => {
                // Given
                const task = 'delete_entity';
                modelStub = new ComponentModelStub(task) as any;
                const onModelInitSpy = spyOn(TaurusBaseComponentStubV1.prototype, 'onModelInit').and.callFake(CallFake);
                const onModelInitialLoadSpy = spyOn(TaurusBaseComponentStubV1.prototype, 'onModelInitialLoad').and.callFake(CallFake);
                const onModelLoadSpy = spyOn(TaurusBaseComponentStubV1.prototype, 'onModelLoad').and.callFake(CallFake);
                const onModelChangeSpy = spyOn(TaurusBaseComponentStubV1.prototype, 'onModelChange').and.callFake(CallFake);
                const onModelErrorSpy = spyOn(TaurusBaseComponentStubV1.prototype, 'onModelError').and.callFake(CallFake);
                const isModelModifiedSpy = spyOn(modelStub, 'isModified').and.returnValue(true);
                const modelStatusSpy = spyOnProperty(modelStub, 'status', 'get').and.returnValue(FAILED);

                componentServiceStub.init.and.returnValue(of(modelStub));
                componentServiceStub.getModel.and.returnValue(of(modelStub));

                const component1: TaurusBaseComponentStubV1 = TestBed.createComponent(TaurusBaseComponentStubV1).componentInstance;

                // Then 1
                expect(component1.model).toBeUndefined();

                // When
                // @ts-ignore
                component1.bindModel();

                // Then 2
                expect(component1.model).toBe(modelStub);
                expect(onModelInitSpy).toHaveBeenCalledWith(modelStub, task);
                expect(onModelInitialLoadSpy).toHaveBeenCalledWith(modelStub, task);
                expect(onModelLoadSpy).toHaveBeenCalledWith(modelStub, task);
                expect(onModelErrorSpy).toHaveBeenCalledWith(modelStub, task, []);

                expect(isModelModifiedSpy).toHaveBeenCalledWith(modelStub);
                expect(modelStatusSpy).toHaveBeenCalled();

                expect(component1.model).toBe(modelStub);

                expect(onModelChangeSpy).not.toHaveBeenCalled();

                // Post
                component.model = modelStub;
                component1.model = modelStub;
            });

            it('should verify will invoke correct Taurus lifecycle hooks for LOADED and not modified', () => {
                // Given
                const localModelStub: ComponentModel = new ComponentModelStub() as any;
                const onModelInitSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelInit').and.callFake(CallFake);
                const onModelFirstLoadSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelFirstLoad').and.callFake(CallFake);
                const onModelLoadSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelLoad').and.callFake(CallFake);
                const onModelChangeSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelChange').and.callFake(CallFake);
                const onModelFailSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelFail').and.callFake(CallFake);
                const isModelModifiedSpy = spyOn(localModelStub, 'isModified').and.returnValue(false);
                const modelStatusSpy = spyOnProperty(localModelStub, 'status', 'get').and.returnValue(LOADED);

                componentServiceStub.init.and.returnValue(of(modelStub));
                componentServiceStub.getModel.and.returnValue(of(localModelStub));

                // Then 1
                expect(component.model).toBeUndefined();

                // When
                // @ts-ignore
                component.bindModel();

                // Then 2
                expect(component.model).toBe(modelStub);
                expect(onModelInitSpy).toHaveBeenCalledWith(modelStub, undefined);
                expect(onModelFirstLoadSpy).toHaveBeenCalledWith(localModelStub, undefined);
                expect(onModelLoadSpy).toHaveBeenCalledWith(localModelStub, undefined);
                expect(isModelModifiedSpy).toHaveBeenCalledWith(modelStub);
                expect(component.model).not.toBe(localModelStub);
                expect(modelStatusSpy).not.toHaveBeenCalled();
                expect(onModelChangeSpy).not.toHaveBeenCalled();
                expect(onModelFailSpy).not.toHaveBeenCalled();
            });

            it('should verify will invoke correct Taurus lifecycle hooks for LOADED and not modified with Task', () => {
                // Given
                const task = 'move_entity';
                modelStub = new ComponentModelStub() as any;
                const localModelStub: ComponentModel = new ComponentModelStub(task) as any;
                const onModelInitSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelInit').and.callFake(CallFake);
                const onModelFirstLoadSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelFirstLoad').and.callFake(CallFake);
                const onModelLoadSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelLoad').and.callFake(CallFake);
                const onModelChangeSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelChange').and.callFake(CallFake);
                const onModelFailSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelFail').and.callFake(CallFake);
                const isModelModifiedSpy = spyOn(localModelStub, 'isModified').and.returnValue(false);
                const modelStatusSpy = spyOnProperty(localModelStub, 'status', 'get').and.returnValue(LOADED);

                componentServiceStub.init.and.returnValue(of(modelStub));
                componentServiceStub.getModel.and.returnValue(of(localModelStub));

                // Then 1
                expect(component.model).toBeUndefined();

                // When
                // @ts-ignore
                component.bindModel();

                // Then 2
                expect(component.model).toBe(modelStub);
                expect(onModelInitSpy).toHaveBeenCalledWith(modelStub, undefined);
                expect(onModelFirstLoadSpy).toHaveBeenCalledWith(localModelStub, task);
                expect(onModelLoadSpy).toHaveBeenCalledWith(localModelStub, task);
                expect(isModelModifiedSpy).toHaveBeenCalledWith(modelStub);
                expect(component.model).not.toBe(localModelStub);
                expect(modelStatusSpy).not.toHaveBeenCalled();
                expect(onModelChangeSpy).not.toHaveBeenCalled();
                expect(onModelFailSpy).not.toHaveBeenCalled();
            });

            it('should verify Taurus lifecycle hook will throw/catch error and log it to console', () => {
                // Given
                const error = new Error('Random Error');
                const onModelInitSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelInit').and.callFake(CallFake);
                const onModelFirstLoadSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelFirstLoad').and.callFake(CallFake);
                const onModelLoadSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelLoad').and.callFake(CallFake);
                const onModelChangeSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelChange').and.throwError(error);
                const onModelFailSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelFail').and.callFake(CallFake);
                const isModelModifiedSpy = spyOn(modelStub, 'isModified').and.returnValue(true);
                const modelStatusSpy = spyOnProperty(modelStub, 'status', 'get').and.returnValue(LOADED);
                const spyError = spyOn(console, 'error').and.callFake(CallFake);

                componentServiceStub.init.and.returnValue(of(modelStub));
                componentServiceStub.getModel.and.returnValue(of(modelStub));

                // Then 1
                expect(component.model).toBeUndefined();

                // When
                // @ts-ignore
                component.bindModel();

                // Then 2
                expect(component.model).toBe(modelStub);
                expect(onModelInitSpy).toHaveBeenCalledWith(modelStub, undefined);
                expect(onModelFirstLoadSpy).toHaveBeenCalledWith(modelStub, undefined);
                expect(onModelLoadSpy).toHaveBeenCalledWith(modelStub, undefined);
                expect(isModelModifiedSpy).toHaveBeenCalledWith(modelStub);
                expect(component.model).toBe(modelStub);
                expect(modelStatusSpy).toHaveBeenCalled();
                expect(onModelChangeSpy).toHaveBeenCalledWith(modelStub, undefined);
                expect(spyError).toHaveBeenCalledWith(`Taurus NgRx Redux failed to execute lifecycle hook "onModelChange"!`, error);
                expect(onModelFailSpy).not.toHaveBeenCalled();
            });

            it('should verify Taurus lifecycle hook post normalize will throw/catch error and log it to console', () => {
                // Given
                const error = new Error('Random Error');
                const onModelInitSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelInit').and.callFake(CallFake);
                const onModelFirstLoadSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelFirstLoad').and.callFake(CallFake);
                const onModelLoadSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelLoad').and.callFake(CallFake);
                const onModelChangeSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelChange').and.callFake(CallFake);
                const onModelFailSpy = spyOn(TaurusBaseComponentStub.prototype, 'onModelFail').and.callFake(CallFake);
                const isModelModifiedSpy = spyOn(modelStub, 'isModified').and.returnValue(true);
                const modelStatusSpy = spyOnProperty(modelStub, 'status', 'get').and.returnValue(LOADED);
                const spyError = spyOn(console, 'error').and.callFake(CallFake);
                // @ts-ignore
                spyOn(component, 'normalizeModelState').and.throwError(error);

                componentServiceStub.init.and.returnValue(of(modelStub));
                componentServiceStub.getModel.and.returnValue(of(modelStub));

                // Then 1
                expect(component.model).toBeUndefined();

                // When
                // @ts-ignore
                component.bindModel();

                // Then 2
                expect(component.model).toBe(modelStub);
                expect(onModelInitSpy).toHaveBeenCalledWith(modelStub, undefined);
                expect(onModelFirstLoadSpy).toHaveBeenCalledWith(modelStub, undefined);
                expect(onModelLoadSpy).toHaveBeenCalledWith(modelStub, undefined);
                expect(isModelModifiedSpy).toHaveBeenCalledWith(modelStub);
                expect(component.model).toBe(modelStub);
                expect(modelStatusSpy).toHaveBeenCalled();
                expect(onModelChangeSpy).toHaveBeenCalledWith(modelStub, undefined);
                expect(spyError).toHaveBeenCalledWith(`Taurus NgRx Redux failed to normalize ComponentModel!`, error);
                expect(onModelFailSpy).not.toHaveBeenCalled();
            });
        });

        describe('|setStateIdle|', () => {
            it('should verify will invoke correct methods', () => {
                // Given
                const componentState: ComponentState = {
                    id: 'TaurusBaseComponentStub',
                    status: LOADED,
                    toLiteral: CallFake,
                    toLiteralCloneDeep: CallFake,
                    copy: CallFake
                };
                const prepareForDestroySpy = spyOn(modelStub, 'prepareForDestroy').and.callFake(() => modelStub);
                const getComponentStateSpy = spyOn(modelStub, 'getComponentState').and.returnValue(componentState);
                component.model = modelStub;

                // When
                // @ts-ignore
                component.setStateIdle();

                // Then
                expect(prepareForDestroySpy).toHaveBeenCalled();
                expect(getComponentStateSpy).toHaveBeenCalled();
                expect(componentServiceStub.idle).toHaveBeenCalledWith(componentState);
            });
        });

        describe('|normalizeModelState|', () => {
            it('should verify will invoke correct methods', () => {
                // Given
                const componentState: ComponentState = {
                    id: 'TaurusBaseComponentStub',
                    status: LOADED,
                    toLiteral: CallFake,
                    toLiteralCloneDeep: CallFake,
                    copy: CallFake
                };
                const clearTaskSpy = spyOn(modelStub, 'clearTask').and.callFake(() => modelStub);
                const getComponentStateSpy = spyOn(modelStub, 'getComponentState').and.returnValue(componentState);
                component.model = modelStub;

                // When
                // @ts-ignore
                component.normalizeModelState(modelStub);

                // Then
                expect(clearTaskSpy).toHaveBeenCalled();
                expect(getComponentStateSpy).toHaveBeenCalled();
                expect(componentServiceStub.update).toHaveBeenCalledWith(componentState);
            });
        });

        describe('|refreshModel|', () => {
            it('should verify will assign previous model until depth 3', () => {
                // Given
                const modelStub1: ComponentModel = new ComponentModelStub(null, 1) as any;
                const modelStub2: ComponentModel = new ComponentModelStub(null, 2) as any;
                const modelStub3: ComponentModel = new ComponentModelStub(null, 3) as any;
                const modelStub4: ComponentModel = new ComponentModelStub(null, 4) as any;
                const modelStub5: ComponentModel = new ComponentModelStub(null, 5) as any;
                const modelStub6: ComponentModel = new ComponentModelStub(null, 6) as any;
                component.model = modelStub1;

                // When
                // @ts-ignore
                component.refreshModel(modelStub2);
                // @ts-ignore
                component.refreshModel(modelStub3);
                // @ts-ignore
                component.refreshModel(modelStub4);
                // @ts-ignore
                component.refreshModel(modelStub5);
                // @ts-ignore
                component.refreshModel(modelStub6);

                // Then
                expect(component.model.previousModel).toBe(modelStub5);
                expect(component.model.previousModel.previousModel).toBe(modelStub4);
                expect(component.model.previousModel.previousModel.previousModel).toBe(modelStub3);
                expect(component.model.previousModel.previousModel.previousModel.previousModel).toBeUndefined();
            });

            it('should verify will throw/catch error and log to console', () => {
                // Given
                const error = new Error('Random Error');
                const modelStub1: ComponentModel = new ComponentModelStubV1(null, 1) as any;
                const modelStub2: ComponentModel = new ComponentModelStubV1(null, 2) as any;
                const consoleSpy = spyOn(console, 'error').and.callFake(CallFake);
                spyOnProperty(modelStub1, 'previousModel', 'get').and.throwError(error);
                component.model = modelStub1;

                // When
                // @ts-ignore
                component.refreshModel(modelStub2);

                // Then
                expect(consoleSpy).toHaveBeenCalledWith('Failed to clean previous ComponentModel', error);
            });
        });

        describe('|initializeRouteReuse|', () => {
            it('should verify if route change event is fired will bind new model', () => {
                // Given
                const componentFixture1 = TestBed.createComponent(TaurusBaseComponentStubV1);
                const component1 = componentFixture1.componentInstance;
                const modelStub1 = new ComponentModelStubV1(null, 1) as any;
                const modelStub2 = new ComponentModelStubV1(null, 2) as any;

                // @ts-ignore
                const spyBindModel = spyOn(component1, 'bindModel').and.callThrough();
                // @ts-ignore
                const spySetStateIdle = spyOn(component1, 'setStateIdle').and.callThrough();

                component1.model = modelStub1;
                componentServiceStub.init.and.returnValues(of(modelStub1), of(modelStub2));
                componentServiceStub.getModel.and.returnValues(of(modelStub1), of(modelStub2));

                componentFixture1.detectChanges();

                // When
                paramsSubject.next({ asset: 10, name: 'Jack' });

                // Then
                expect(component1.model).toBe(modelStub2);
                expect(spyBindModel).toHaveBeenCalledTimes(2);
                expect(spySetStateIdle).toHaveBeenCalledTimes(1);

                // Post
                component.model = modelStub;
            });
        });
    });
});
