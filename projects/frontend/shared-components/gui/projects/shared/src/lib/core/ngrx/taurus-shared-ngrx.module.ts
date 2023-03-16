/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/unified-signatures */

import { InjectionToken, ModuleWithProviders, NgModule, Type } from '@angular/core';

import { Action, ActionReducer, ActionReducerMap, StoreConfig, StoreFeatureModule, StoreModule } from '@ngrx/store';
import { EffectsFeatureModule, EffectsModule } from '@ngrx/effects';

import { TaurusNgRxConfig } from './config';
import { TaurusSharedNgrxProdModule, TaurusSharedNgrxDevModule } from './helper-modules';

/**
 * ** Integration Class module for NgRx Redux.
 */
@NgModule({})
export class TaurusSharedNgRxModule {
    /**
     * ** Provides TaurusSharedNgrxProdModule and all Services related to Taurus Redux.
     *
     *      - Recommended for Prod (release) builds.
     *      - Should be invoke at Root and only once for entire project.
     *      - In FeaturesModules (lazy loaded Modules) invoke one of the methods <b>forFeatureEffects/forFeatureStore</b>.
     */
    static forRoot(): ModuleWithProviders<TaurusSharedNgrxProdModule> {
        return TaurusSharedNgrxProdModule.forRoot();
    }

    /**
     * ** Provides TaurusSharedNgrxDevModule including StoreDevTools and all Services related to Taurus Redux.
     *
     *      - Recommended for Dev (local) builds.
     *      - Should be invoke at Root and only once for entire project.
     *      - In FeaturesModules (lazy loaded Modules) invoke one of the methods <b>forFeatureEffects/forFeatureStore</b>.
     */
    static forRootWithDevtools(config: TaurusNgRxConfig = {}): ModuleWithProviders<TaurusSharedNgrxDevModule> {
        return TaurusSharedNgrxDevModule.forRoot(config.storeDevToolsConfig);
    }

    /**
     * ** Load Features Effects.
     *
     *      - Should be invoke in FeatureModules (lazy loaded Modules).
     *      - It will register Effects for that Feature.
     */
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    static forFeatureEffects(effects: Array<Type<any>>): ModuleWithProviders<EffectsFeatureModule> {
        return EffectsModule.forFeature(effects);
    }

    /**
     * ** Load Features Store reducers.
     *
     *      - Should be invoke in FeatureModules (lazy loaded Modules).
     *      - It will extend Store and add reducers for that Feature.
     */
    static forFeatureStore<T, V extends Action = Action>(
        featureName: string,
        reducers: ActionReducerMap<T, V> | InjectionToken<ActionReducerMap<T, V>>,
        config?: StoreConfig<T, V> | InjectionToken<StoreConfig<T, V>>
    ): ModuleWithProviders<StoreFeatureModule>;
    static forFeatureStore<T, V extends Action = Action>(
        featureName: string,
        reducer: ActionReducer<T, V> | InjectionToken<ActionReducer<T, V>>,
        config?: StoreConfig<T, V> | InjectionToken<StoreConfig<T, V>>
    ): ModuleWithProviders<StoreFeatureModule>;
    static forFeatureStore<T, V extends Action = Action>(
        featureName: string,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        reducer: any,
        config?: StoreConfig<T, V> | InjectionToken<StoreConfig<T, V>>
    ): ModuleWithProviders<StoreFeatureModule> {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
        return StoreModule.forFeature(featureName, reducer, config);
    }
}
