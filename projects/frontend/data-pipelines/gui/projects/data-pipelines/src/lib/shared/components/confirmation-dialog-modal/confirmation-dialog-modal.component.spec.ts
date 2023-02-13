/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ConfirmationDialogModalComponent } from './confirmation-dialog-modal.component';

describe('ConfirmationDialogModalComponent', () => {
    let component: ConfirmationDialogModalComponent;
    let fixture: ComponentFixture<ConfirmationDialogModalComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [
                ConfirmationDialogModalComponent
            ]
        })
                     .compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(ConfirmationDialogModalComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    describe('confirm', () => {
        it('makes expected calls', () => {
            spyOn(component.changeStatus, 'emit').and.callThrough();
            component.confirm();
            expect(component.changeStatus.emit).toHaveBeenCalled();
        });
    });
});
