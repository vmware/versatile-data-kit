

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ActivatedRouteSnapshot, UrlSegment } from '@angular/router';

import { CollectionsUtil } from '../../../utils';

import { RouteSegments, RouteState } from '../model';

/**
 * ** Route State Factory.
 *
 *
 */
export class RouteStateFactory {
    /**
     * ** Creates Router State from provided Route snapshot.
     */
    create(routeSnapshot: ActivatedRouteSnapshot, url: string): RouteState {
        return RouteState.of(
            this._getRouteSegments(routeSnapshot),
            url
        );
    }

    private _getRouteSegments(routeSnapshot: ActivatedRouteSnapshot): RouteSegments {
        if (CollectionsUtil.isNil(routeSnapshot)) {
            return null;
        }

        const routePathSegments: string[] = [];
        routeSnapshot.url.forEach((segment: UrlSegment) => {
            routePathSegments.push(segment.path);
        });

        const routePath = routePathSegments.join('/');
        const data = CollectionsUtil.cloneDeep(routeSnapshot.data);
        const params = CollectionsUtil.cloneDeep(routeSnapshot.params);
        const queryParams = CollectionsUtil.cloneDeep(routeSnapshot.queryParams);
        const configPath = routeSnapshot.routeConfig?.path;

        let parentNavSegments: RouteSegments;

        if (routeSnapshot.parent) {
            parentNavSegments = this._getRouteSegments(routeSnapshot.parent);
        }

        return RouteSegments.of(routePath, data, params, queryParams, parentNavSegments, configPath);
    }
}
