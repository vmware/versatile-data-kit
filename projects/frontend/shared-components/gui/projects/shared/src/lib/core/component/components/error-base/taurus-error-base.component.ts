/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Directive, OnDestroy } from '@angular/core';

import { ErrorStore, generateErrorCode, ServiceHttpErrorCodes, TaurusObject } from '../../../../common';

import { ErrorStoreImpl, processServiceRequestError } from '../../../error';

/**
 * ** Taurus base component with provided in some way auto handling for errors.
 *
 *      - This component is mutually exclusive with TaurusBaseComponent.
 *      - In this component error handling like error recording, error filter, search, etc.. is handled into the Component itself,
 *          while in TaurusBaseComponent it's handled in the upper level inside the Effects and provided through ComponentModel to the Component itself.
 */
@Directive()
export class TaurusErrorBaseComponent extends TaurusObject implements OnDestroy {
    /**
     * @inheritDoc
     */
    static override readonly CLASS_NAME: string = 'TaurusErrorBaseComponent';

    /**
     * @inheritDoc
     */
    static override readonly PUBLIC_NAME: string = 'Taurus-Error-Base-Component';

    /**
     * ** Reference to local ErrorStore.
     */
    errors: ErrorStore;

    /**
     * ** Error codes supported in class and its corresponding subclasses.
     */
    errorCodes: Readonly<Record<string, string>>;

    /**
     * ** Constructor.
     */
    constructor(className: string = null) {
        super(className ?? TaurusErrorBaseComponent.CLASS_NAME);

        this.errors = ErrorStoreImpl.empty();
        this.errorCodes = {};
    }

    /**
     * @inheritDoc
     */
    override ngOnDestroy(): void {
        this.errors.dispose();

        super.ngOnDestroy();
    }

    /**
     * ** Generates Error code (token).
     *
     *      - Code (token) should start with Class name,
     *              then followed by underscore and class PUBLIC_NAME,
     *              then followed by underscore and method name or underscore with some error specifics,
     *              and followed by underscore and additional details to avoid overlaps with other Class errors.
     *
     * <br/>
     * <i>returned value pattern</i>:
     * <p>
     *     <Class Name><b>_</b><Class PUBLIC_NAME><b>_</b><Class method name><b>_</b><additional details, like HTTP Status Code>
     * </p>
     */
    protected generateErrorCode(className: string, classPublicName: string, methodName: string, additionalDetails?: string): string {
        return generateErrorCode(className, classPublicName, methodName, additionalDetails);
    }

    /**
     * ** Process service HTTP request error and return ErrorRecord.
     *
     * @param {Record<keyof ServiceHttpErrorCodes, string>} serviceHttpErrorCodes - is map of Service method supported error codes auto-handling
     * @param {unknown} error - is actual error object reference
     */
    protected processServiceRequestError(serviceHttpErrorCodes: Record<keyof ServiceHttpErrorCodes, string>, error: unknown): void {
        this.errors.record(processServiceRequestError(this.objectUUID, serviceHttpErrorCodes, error));
    }
}
