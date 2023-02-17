/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { VmwToastType } from '../../../commons';

import { ToastsComponent } from './toasts.component';
import { ToastService } from '../service';

describe('ToastsComponent', () => {
    let component: ToastsComponent;
    let fixture: ComponentFixture<ToastsComponent>;

    const TEST_TOAST = {
        title: 'title001',
        description: 'description001',
        type: VmwToastType.FAILURE,
        id: 10,
        time: new Date()
    };

    const FIRST_ELEMENT_INDEX = 0;
    const EMPTY_LIST_LENGTH = 0;

    beforeEach(
        async () => {
            await TestBed.configureTestingModule({
                providers: [
                    ToastService
                ],
                schemas: [NO_ERRORS_SCHEMA],
                declarations: [ToastsComponent]
            }).compileComponents();
        }
    );

    beforeEach(() => {
        fixture = TestBed.createComponent(ToastsComponent);
        component = fixture.componentInstance;
        component.toasts = [TEST_TOAST];
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    describe('remove', () => {
        it('removes an element from the toasts list ', () => {
            component.removeToast(FIRST_ELEMENT_INDEX);
            expect(component.toasts.length).toEqual(EMPTY_LIST_LENGTH);
        });
    });
});
