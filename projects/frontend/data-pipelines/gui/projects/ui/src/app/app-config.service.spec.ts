/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { AppConfigService } from './app-config.service';
import { HttpBackend } from '@angular/common/http';

describe('AppConfigService', () => {
    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [HttpClientTestingModule],
            providers: [{ provide: AppConfigService, useClass: AppConfigService, deps: [HttpBackend] }]
        });
    });

    it('can load instance', () => {
        const service = TestBed.inject(AppConfigService);
        service.loadAppConfig();
        expect(service).toBeTruthy();
    });
});
