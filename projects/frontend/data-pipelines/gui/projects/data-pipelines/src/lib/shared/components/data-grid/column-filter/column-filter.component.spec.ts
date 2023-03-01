/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ClrDatagridFilter } from '@clr/angular';

import { ColumnFilterComponent } from './column-filter.component';

describe('ColumnFilterComponent', () => {
    let component: ColumnFilterComponent;
    let fixture: ComponentFixture<ColumnFilterComponent>;

    const TEST_VALUE = 'test_value';

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [ColumnFilterComponent],
            providers: [
                {
                    provide: ClrDatagridFilter,
                    useFactory: () => ({
                        setFilter: () => ({}),
                    }),
                },
            ],
        }).compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(ColumnFilterComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    describe('toggle selection', () => {
        it('change value', () => {
            component.toggleSelection({
                target: { value: TEST_VALUE } as unknown as EventTarget,
            } as Event);
            expect(component.value).toBe(TEST_VALUE);
        });
    });

    describe('clean filter', () => {
        it('remove value', () => {
            component.cleanFilter();
            expect(component.value).toBe(null);
        });
    });
});
