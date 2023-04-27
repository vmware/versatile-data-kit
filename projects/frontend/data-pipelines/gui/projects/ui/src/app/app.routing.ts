/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

// modules
import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';

import {
    DataJobDetailsPageComponent,
    DataJobExecutionsPageComponent,
    DataJobPageComponent,
    DataJobsExplorePageComponent,
    DataJobsManagePageComponent,
    DataPipelinesRoutes
} from '@versatiledatakit/data-pipelines';

import { GettingStartedComponent } from './getting-started/getting-started.component';
import { DataPipelinesRoute } from '../../../data-pipelines/src/lib/model';

const routes: DataPipelinesRoutes = [
    { path: 'get-started', component: GettingStartedComponent },

    //Explore
    {
        path: 'explore/data-jobs',
        component: DataJobsExplorePageComponent,
        data: {
            navigateTo: {
                path: '/explore/data-jobs/{0}/{1}',
                replacers: [
                    { searchValue: '{0}', replaceValue: '$.team' },
                    { searchValue: '{1}', replaceValue: '$.job' }
                ]
            },
            restoreUiWhen: {
                previousConfigPathLike: '/explore/data-jobs/:team/:job'
            }
        }
    },
    {
        path: 'explore/data-jobs/:team/:job',
        component: DataJobPageComponent,
        data: {
            context: 'explore',
            teamParamKey: 'team',
            jobParamKey: 'job'
        },
        children: [
            {
                path: 'details',
                component: DataJobDetailsPageComponent,
                data: {
                    editable: false,
                    navigateBack: {
                        path: '/explore/data-jobs'
                    }
                }
            },
            {
                path: 'executions',
                redirectTo: 'details'
            },
            { path: '**', redirectTo: 'details' }
        ]
    },

    //Manage
    {
        path: 'manage/data-jobs',
        component: DataJobsManagePageComponent,
        data: {
            navigateTo: {
                path: '/manage/data-jobs/{0}/{1}',
                replacers: [
                    { searchValue: '{0}', replaceValue: '$.team' },
                    { searchValue: '{1}', replaceValue: '$.job' }
                ]
            },
            restoreUiWhen: {
                previousConfigPathLike: '/manage/data-jobs/:team/:job'
            }
        } as DataPipelinesRoute
    },
    {
        path: 'manage/data-jobs/:team/:job',
        component: DataJobPageComponent,
        data: {
            context: 'manage',
            teamParamKey: 'team',
            jobParamKey: 'job'
        },
        children: [
            {
                path: 'details',
                component: DataJobDetailsPageComponent,
                data: {
                    editable: true,
                    navigateBack: {
                        path: '/manage/data-jobs'
                    }
                }
            },
            {
                path: 'executions',
                component: DataJobExecutionsPageComponent,
                data: {
                    editable: true,
                    navigateBack: {
                        path: '/manage/data-jobs'
                    }
                }
            },
            { path: '**', redirectTo: 'details' }
        ]
    },

    { path: '**', redirectTo: 'get-started' }
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})
export class AppRouting {}
