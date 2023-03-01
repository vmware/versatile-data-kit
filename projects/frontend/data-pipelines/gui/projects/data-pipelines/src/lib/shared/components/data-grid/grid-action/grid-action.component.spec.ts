/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { GridActionComponent } from './grid-action.component';

describe('GridActionComponent', () => {
    let component: GridActionComponent;
    let fixture: ComponentFixture<GridActionComponent>;

    beforeEach(() => {
        TestBed.configureTestingModule({
            schemas: [NO_ERRORS_SCHEMA],
            declarations: [GridActionComponent],
        });
        fixture = TestBed.createComponent(GridActionComponent);
        component = fixture.componentInstance;
    });

    it('can load instance', () => {
        expect(component).toBeTruthy();
    });

    it(`id has default value`, () => {
        expect(component.id).toBeDefined();
    });

    it(`addId has default value`, () => {
        expect(component.addId).toBeDefined();
    });

    it(`editId has default value`, () => {
        expect(component.editId).toBeDefined();
    });

    it(`removeId has default value`, () => {
        expect(component.removeId).toBeDefined();
    });
});
