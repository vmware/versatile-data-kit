

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable max-len,
                  @typescript-eslint/naming-convention,
                  prefer-arrow/prefer-arrow-functions,
                  prefer-arrow/prefer-arrow-functions,
                  prefer-arrow/prefer-arrow-functions,
                  space-before-function-paren,
                  @typescript-eslint/no-unsafe-member-access,
                  @typescript-eslint/no-unsafe-argument,
                  @typescript-eslint/ban-ts-comment,
                  @typescript-eslint/no-explicit-any,
                  @typescript-eslint/no-unsafe-assignment
*/

import 'reflect-metadata';

import { CollectionsUtil } from '../../../utils';

import { SystemEventMetadataRecords } from '../dispatcher/models';
import { SystemEventHandlerRegistry } from '../dispatcher/registry';

import { SYSTEM_EVENTS_METADATA_KEY } from './models';

/**
 * ** Decorator to annotate Handler source Class as SystemEvent Handler source Class.
 *
 *   - Annotation should be add on top, before Class declaration starts,
 *        there should be no other annotations between this one and the Class declaration.
 *   - Annotation brings context from Object instance and make connection between Handler and the instance.
 *   - Take care for auto unsubscribe from HandlersRegistry for all Handlers from the Class on Object destroy,
 *        leveraging Angular ngOnDestroy lifecycle hook.
 *   - Annotation could be added only on Angular objects (like Services) to avoid memory leaks.
 *   - Decorator is evaluated on Class declaration and inside code is evaluated on Object/Instance creation.
 *   - For Dispatcher and Handler decorator read JSDoc {@link SystemEventDispatcher} {@link SystemEventHandler}
 *
 * @example
 *
 *   `@Injectable()`
 *   `@SystemEventHandlerClass()` // immediately before Class declaration!
 *    export class DataJobService {
 *      // some properties, methods and handlers
 *    }
 *
 *
 */
export function SystemEventHandlerClass(): ClassDecorator {
    // @ts-ignore
    return <T extends new(...args: any[]) => InstanceType<T>>(OriginConstructor: T):
        (...args: ConstructorParameters<T>) => InstanceType<T> => {

        const originMetadataKeys = Reflect.getMetadataKeys(OriginConstructor);
        const originMetadataRecords: SystemEventMetadataRecords = Reflect.getMetadata(SYSTEM_EVENTS_METADATA_KEY, OriginConstructor) ?? [];
        const originOnDestroyRef: () => void = getOriginOnDestroyRef<T>(OriginConstructor);

        let instance: InstanceType<T>;

        const OverriddenConstructor = function(...args: ConstructorParameters<T>): InstanceType<T> {
            instance = new OriginConstructor(...args);

            originMetadataRecords.forEach((r) => {
                SystemEventHandlerRegistry.register<InstanceType<T>>(
                    r.events,
                    r.handler,
                    instance,
                    r.filterExpression
                );
            });

            return instance;
        };

        OriginConstructor.prototype.ngOnDestroy = () => {
            originMetadataRecords.forEach((r) => {
                SystemEventHandlerRegistry.unregister(
                    r.events,
                    r.handler
                );

                if (originOnDestroyRef) {
                    originOnDestroyRef.call(instance);
                }
            });
        };

        originMetadataKeys.forEach((key) => {
            Reflect.defineMetadata(key, Reflect.getMetadata(key, OriginConstructor), OverriddenConstructor);
        });

        copyFromOriginToOverride(OriginConstructor, OverriddenConstructor);

        return OverriddenConstructor;
    };
}

const getOriginOnDestroyRef = <T extends new(...args: any[]) => InstanceType<T>>(classRef: T): () => void | null => {
    if (!classRef || !classRef.prototype) {
        return null;
    }

    if (classRef.prototype.ngOnDestroy) {
        return classRef.prototype.ngOnDestroy as (() => void);
    }

    return getOriginOnDestroyRef(classRef.prototype);
};

const copyFromOriginToOverride = <T extends new(...args: any[]) => InstanceType<T>>(
    OriginConstructor: T,
    OverriddenConstructor: (...args: ConstructorParameters<T>) => InstanceType<T>
) => {

    CollectionsUtil.iterateClassStatics(OriginConstructor, (descriptor, key) => {
        const overriddenPropertyDescriptor = CollectionsUtil.getObjectPropertyDescriptor(OverriddenConstructor, key);
        if (overriddenPropertyDescriptor && !overriddenPropertyDescriptor.writable) {
            return;
        }

        OverriddenConstructor[key] = descriptor.value;
    });

    OverriddenConstructor.prototype = Object.create(OriginConstructor.prototype);
    OverriddenConstructor.prototype.constructor = OverriddenConstructor;
};
