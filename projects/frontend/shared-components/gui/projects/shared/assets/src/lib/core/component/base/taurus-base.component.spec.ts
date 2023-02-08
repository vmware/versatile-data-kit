

/* eslint-disable @typescript-eslint/dot-notation */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, ActivatedRouteSnapshot } from '@angular/router';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { of } from 'rxjs';
import { take } from 'rxjs/operators';

import { CallFake } from '../../../unit-testing';

import { TaurusObject } from '../../../common';

import { RouteState } from '../../router';
import { RouteStateFactory } from '../../router/factory';

import { NavigationService } from '../../navigation';

import { ComponentModel, ComponentState, FAILED, LOADED } from '../model';
import { ComponentService } from '../services';

import {
    OnTaurusModelChange,
    OnTaurusModelFail,
    OnTaurusModelFirstLoad,
    OnTaurusModelInit,
    OnTaurusModelLoad
} from './interfaces';

import { TaurusBaseComponent } from './taurus-base.component';

@Component({
    selector: 'shared-taurus-base-subclass-component',
    template: ''
})
    // eslint-disable-next-line @angular-eslint/component-class-suffix
class TaurusBaseComponentStub extends TaurusBaseComponent
    implements OnInit, OnDestroy,
        OnTaurusModelInit, OnTaurusModelLoad,
        OnTaurusModelFirstLoad, OnTaurusModelChange,
        OnTaurusModelFail {

    uuid = 'TaurusBaseComponentStub';

    constructor(componentService: ComponentService,
                navigationService: NavigationService,
                activatedRoute: ActivatedRoute) {
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

class ComponentModelStub {
    task: string;

    constructor(task?: string) {
        this.task = task;
    }

    get status() {
        return null;
    }

    isModified(): boolean {
        return null;
    }

    withStatusIdle() {
        return this;
    }

    getComponentState() {
        return {};
    }

    getTask() {
        return this.task;
    }

    clearTask() {
        return this;
    }
}

describe('TaurusBaseComponent -> TaurusSubclassComponent', () => {
    let componentServiceStub: jasmine.SpyObj<ComponentService>;
    let navigationServiceStub: jasmine.SpyObj<NavigationService>;
    let activatedRouteStub: Partial<ActivatedRoute>;
    let activatedRouteSnapshotStub: ActivatedRouteSnapshot;

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
        activatedRouteStub = { snapshot: activatedRouteSnapshotStub };
        routeStateStub = {
            routePathSegments: ['path1/path2', 'path3/path4']
        } as RouteState;
        spyOn(RouteStateFactory.prototype, 'create').and.returnValue(routeStateStub);

        modelStub = new ComponentModelStub() as any;

        TestBed.configureTestingModule({
            declarations: [
                TaurusBaseComponentStub
            ],
            providers: [
                { provide: ComponentService, useValue: componentServiceStub },
                { provide: NavigationService, useValue: navigationServiceStub },
                { provide: ActivatedRoute, useValue: activatedRouteStub }
            ]
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
        describe('navigateTo', () => {
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

        describe('navigateBack', () => {
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
                expect(component['subscriptions'].length).toEqual(1);
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
                expect(onModelInitSpy).toHaveBeenCalledWith(modelStub);
                expect(onModelFirstLoadSpy).toHaveBeenCalledWith(modelStub);
                expect(onModelLoadSpy).toHaveBeenCalledWith(modelStub);
                expect(isModelModifiedSpy).toHaveBeenCalledWith(modelStub);
                expect(component.model).toBe(modelStub);
                expect(modelStatusSpy).toHaveBeenCalled();
                expect(onModelChangeSpy).toHaveBeenCalledWith(modelStub);
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

            it('should verify will invoke correct Taurus lifecycle hooks for FAILED and modified', () => {
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
                expect(onModelInitSpy).toHaveBeenCalledWith(modelStub);
                expect(onModelFirstLoadSpy).toHaveBeenCalledWith(modelStub);
                expect(onModelLoadSpy).toHaveBeenCalledWith(modelStub);
                expect(isModelModifiedSpy).toHaveBeenCalledWith(modelStub);
                expect(component.model).toBe(modelStub);
                expect(modelStatusSpy).toHaveBeenCalled();
                expect(onModelFailSpy).toHaveBeenCalledWith(modelStub);
                expect(onModelChangeSpy).not.toHaveBeenCalled();
            });

            it('should verify will invoke correct Taurus lifecycle hooks for FAILED and modified with Task', () => {
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
                expect(onModelInitSpy).toHaveBeenCalledWith(modelStub);
                expect(onModelFirstLoadSpy).toHaveBeenCalledWith(localModelStub);
                expect(onModelLoadSpy).toHaveBeenCalledWith(localModelStub);
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
                expect(onModelInitSpy).toHaveBeenCalledWith(modelStub);
                expect(onModelFirstLoadSpy).toHaveBeenCalledWith(localModelStub, task);
                expect(onModelLoadSpy).toHaveBeenCalledWith(localModelStub, task);
                expect(isModelModifiedSpy).toHaveBeenCalledWith(modelStub);
                expect(component.model).not.toBe(localModelStub);
                expect(modelStatusSpy).not.toHaveBeenCalled();
                expect(onModelChangeSpy).not.toHaveBeenCalled();
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
                    toLiteralDeepClone: CallFake,
                    copy: CallFake
                };
                const setStatusIdleSpy = spyOn(modelStub, 'withStatusIdle').and.callFake(() => modelStub);
                const getComponentStateSpy = spyOn(modelStub, 'getComponentState').and.returnValue(componentState);
                component.model = modelStub;

                // When
                // @ts-ignore
                component.setStateIdle();

                // Then
                expect(setStatusIdleSpy).toHaveBeenCalled();
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
                    toLiteralDeepClone: CallFake,
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
    });
});
