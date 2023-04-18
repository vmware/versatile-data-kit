/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { AppConfigService } from './app-config.service';

describe('AppConfigService', () => {
    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [HttpClientTestingModule],
            providers: [AppConfigService]
        });
    });

    it('can load instance', () => {
        const service = TestBed.inject(AppConfigService);
        service.loadAppConfig();
        expect(service).toBeTruthy();
    });
});
