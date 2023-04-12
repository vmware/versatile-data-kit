/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { AppConfigService } from './app-config.service';

describe('AppConfigService', () => {
    interface AppConfig {
        issuer: string;
        cspClientId: string;
        logoutUrl: string;
        orgId?: string;
        consoleCloudUrl?: string;
        featureFlags?: FeatureFlags;
    }

    interface FeatureFlags {
        metadataSearchSupport?: boolean;
        extendedDemoSupport?: boolean;
    }

    let service: AppConfigService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [HttpClientTestingModule],
            providers: [AppConfigService]
        });
        service = TestBed.inject(AppConfigService);
    });

    it('can load instance', () => {
        service.loadConfig<AppConfig>('assets/config.json');
        expect(service).toBeTruthy();
    });
});
