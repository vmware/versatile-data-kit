/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';

import { VmwToastType } from '../../../commons';

import { ToastService } from './toast.service';

describe('ToastServiceComponent', () => {
    let service: ToastService;

    const TEST_TOAST = {
        title: 'title001',
        description: 'descr001',
        type: VmwToastType.FAILURE
    };

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [ToastService]
        });
        service = TestBed.inject(ToastService);
    });

    it('should create', () => {
        expect(service).toBeTruthy();
    });

    describe('show', () => {
        it('makes expected calls', () => {
            spyOn(service.notificationsSubject, 'next').and.callThrough();
            service.show(TEST_TOAST);
            expect(service.notificationsSubject.next).toHaveBeenCalledWith(TEST_TOAST);
        });
    });
});
