/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/no-explicit-any,@typescript-eslint/naming-convention */

import { Directive, Type } from '@angular/core';

import { CollectionsUtil, FilterMethods } from '../../../utils';

import { TaurusObject } from '../../object';

import { ServiceHttpErrorCodes } from '../../error';
import { generateSupportedHttpErrorCodes } from '../../error/utils';

/**
 * ** Store type for auto-generated codes for every method, where key is the method name and value is different error codes for auto-supported scenarios.
 */
export type ErrorCodes<CType, KExclude extends keyof any = ExcludedMethods> = Readonly<
    Record<keyof FilterMethods<CType, KExclude>, Readonly<Record<keyof ServiceHttpErrorCodes, string>>>
>;

/**
 * ** Excluded methods from auto-generated error codes.
 */
export type ExcludedMethods =
    | 'constructor'
    | 'errorCodes'
    | 'dispose'
    | 'ngOnDestroy'
    | 'cleanSubscriptions'
    | 'removeSubscriptionRef'
    | 'registerErrorCodes';

/**
 * ** Base Class for Angular Service related classes.
 *
 *      - Add abstraction for TaurusBaseApiService subclasses to auto-register their methods' error codes in relationship one method to many error codes for auto-supported scenarios.
 *      - There could be added additional error codes from subclasses.
 */
@Directive()
export class TaurusBaseApiService<CType extends TaurusBaseApiService = any> extends TaurusObject {
    /**
     * @inheritDoc
     */
    static override readonly CLASS_NAME: string = 'TaurusBaseApiService';

    /**
     * @inheritDoc
     */
    static override readonly PUBLIC_NAME: string = 'Taurus-Api-Service';

    /**
     * ** Class error codes Mapping.
     *
     *      - There are auto-generated error codes for every method name in runtime, where method name is the key, and the multiple values where each value is bound to unique error code.
     *      - Subclasses could override in definition time or in runtime to add additional error codes.
     */
    readonly errorCodes: ErrorCodes<CType> = {} as ErrorCodes<CType>;

    /**
     * ** Constructor.
     */
    protected constructor(className: string = null) {
        super(className ?? TaurusBaseApiService.CLASS_NAME);
    }

    /**
     * ** Register error codes for service.
     *
     *      - Exclude system methods.
     *      - Exclude private methods which names start with underscore (e.g. _methodName(): void;)
     * @protected
     */
    protected registerErrorCodes(service: Type<CType>): void {
        /* eslint-disable @typescript-eslint/no-unsafe-argument,
                          @typescript-eslint/no-unsafe-assignment,
                          @typescript-eslint/no-unsafe-member-access */

        try {
            Object.getOwnPropertyNames(service.prototype)
                .filter(
                    (method) =>
                        method !== 'constructor' &&
                        method !== 'dispose' &&
                        method !== 'ngOnDestroy' &&
                        method !== 'cleanSubscriptions' &&
                        method !== 'removeSubscriptionRef' &&
                        method !== 'registerErrorCodes' &&
                        !/^_/.test(method) &&
                        CollectionsUtil.isFunction(service.prototype[method])
                )
                .forEach((method) => {
                    this.errorCodes[method] = generateSupportedHttpErrorCodes(
                        (service as any).CLASS_NAME,
                        (service as any).PUBLIC_NAME,
                        method
                    );
                });
        } catch (e) {
            console.error(`Cannot register Service Error Codes!`);
        }
        /* eslint-enable @typescript-eslint/no-unsafe-argument,
                         @typescript-eslint/no-unsafe-assignment,
                         @typescript-eslint/no-unsafe-member-access */
    }
}
