/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { DeleteModalComponent } from './delete-modal.component';

describe('DeleteModalComponent', () => {
    let component: DeleteModalComponent;
    let fixture: ComponentFixture<DeleteModalComponent>;

    beforeEach(() => {
        TestBed.configureTestingModule({
            schemas: [NO_ERRORS_SCHEMA],
            declarations: [DeleteModalComponent]
        });
        fixture = TestBed.createComponent(DeleteModalComponent);
        component = fixture.componentInstance;
    });

    it('can load instance', () => {
        expect(component).toBeTruthy();
    });

    describe('confirm', () => {
        it('makes expected calls', () => {
            spyOn(component, 'close').and.callThrough();
            component.confirm();
            expect(component.close).toHaveBeenCalled();
        });
    });

    describe('cancel', () => {
        it('makes expected calls', () => {
            spyOn(component, 'close').and.callThrough();
            component.cancel();
            expect(component.close).toHaveBeenCalled();
        });
    });
});
