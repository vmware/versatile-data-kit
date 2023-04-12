/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { catchError, map, tap } from 'rxjs/operators';
import { firstValueFrom, of } from 'rxjs';

@Injectable()
export class AppConfigService<T> {
    private appConfig: T;

    constructor(private readonly httpClient: HttpClient) {}

    loadConfig(jsonUrl: string): Promise<boolean> {
        return firstValueFrom(
            this.httpClient.get<T>(jsonUrl).pipe(
                tap((data: T) => (this.appConfig = data)),
                map(() => true),
                catchError((err: unknown) => {
                    console.error('Environment variable file was not found, application will not load');
                    console.error(err);
                    return of(false);
                })
            )
        );
    }

    getConfig(): T {
        return this.appConfig;
    }
}
