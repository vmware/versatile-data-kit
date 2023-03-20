/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpStatusCode } from '@angular/common/http';

import { Copy, Equals, Literal } from '../../../../interfaces';

import { ErrorRecord } from '../../../ui-error/model/interfaces';

export type ErrorStoreChangeListener<T extends ErrorStore> = (store: T) => void;

/**
 * ** Interface for ErrorStore.
 */
export interface ErrorStore extends Literal<ErrorRecord[]>, Copy<ErrorStore>, Equals<ErrorStore> {
    /**
     * ** Error records store.
     *
     *      - It's store for error codes (tokens), where every code is represented in string format as key part of compound object ErrorRecord.
     *      - Codes (tokens) should start with Class name,
     *              then followed by underscore and class PUBLIC_NAME,
     *              then followed by underscore and method name or underscore with some error specifics,
     *              and followed by underscore and additional details to avoid overlaps with other Class errors.
     *
     * <br/>
     * <i>pattern</i>:
     * <p>
     *     <Class Name><b>_</b><class PUBLIC_NAME><b>_</b><class method name><b>_</b><additional details, like HTTP Status Code>
     * </p>
     */
    records: ErrorRecord[];

    /**
     * ** Mutation listeners invoked whenever changed occurs in records of ErrorRecord.
     */
    changeListeners: Array<ErrorStoreChangeListener<ErrorStore>>;

    /**
     * ** Returns boolean that indicates if there is any ErrorRecords.
     */
    hasErrors(): boolean;

    /**
     * ** Check if store has some error code(s) by providing one or more error codes.
     *
     *      - Comparison is executed with exact match.
     *      - It will return TRUE if at least one of the provided error code is found in store.
     *      - Evaluation is executed with operator OR for every error code.
     */
    hasCode(...errorCodes: string[]): boolean;

    /**
     * ** Check if store has some error code(s) by providing one or more error code patterns that will be translated to RegExp.
     *
     *      - Comparison is executed with RegExp.
     *      - It will return TRUE if at least one of the provided error code patterns match error codes in store.
     *      - Evaluation is executed with operator OR for every error code pattern.
     */
    hasCodePattern(...errorCodesPatterns: string[]): boolean;

    /**
     * ** Record in store error code, object UUID and optionally actual error and Http status code if it's Http request error.
     *
     *      - Comparison is executed with exact match.
     *      - Error codes are unique and distinct in context of store.
     *      - There could be only one error code present in the queue for given error code from one objectUUID at any moment.
     */
    record(errorCode: string, objectUUID: string, error: Error, httpStatusCode?: HttpStatusCode): void;

    /**
     * ** Record in store ErrorRecord.
     *
     *      - Comparison is executed with exact match.
     *      - Error codes are unique and distinct in context of store.
     *      - There could be only one error code present in the queue for given error code from one objectUUID at any moment.
     */
    record(errorRecord: ErrorRecord): void;

    /**
     * ** Remove error code from store by providing one or more error codes.
     *
     *      - Comparison is executed with exact match.
     *      - Error codes are unique and distinct in context of store.
     *      - There could be only one error code present in the queue for given error code at any moment.
     */
    removeCode(...errorCodes: string[]): void;

    /**
     * ** Remove error code pattern from store by providing one or more error code patterns that will be translated to RegExp.
     *
     *      - Comparison is executed with exact RegExp.
     *      - Error codes are unique and distinct in context of store.
     *      - There could be only one error code present in the queue for given error code at any moment.
     */
    removeCodePattern(...errorCodePatterns: string[]): void;

    /**
     * ** Find ErrorRecord(s) for provided error code(s).
     *
     *      - Comparison is executed with exact match.
     *      - Error codes are unique and distinct in context of store.
     *      - There could be only one error code present in the queue for given error code at any moment.
     */
    findRecords(...errorCodes: string[]): ErrorRecord[];

    /**
     * ** Find ErrorRecord(s) for provided error code pattern(s) that will be translated to RegExp.
     *
     *      - Comparison is executed with exact RegExp.
     *      - Error codes are unique and distinct in context of store.
     *      - There could be only one error code present in the queue for given error code at any moment.
     */
    findRecordsByPattern(...errorCodePatterns: string[]): ErrorRecord[];

    /**
     * ** Distinct and return only error records that don't match any from provided.
     */
    distinctErrorRecords(errorRecords: ErrorRecord[]): ErrorRecord[];

    /**
     * ** Purge ErrorRecords.
     */
    purge(injectedStore: ErrorStore): void;

    /**
     * ** Attach listener for change.
     */
    onChange(callback: (store: this) => void): void;

    /**
     * ** Dispose and clean store.
     *
     *      - Useful to call before container Object get destroyed, to clean all references.
     */
    dispose(): void;

    /**
     * ** Clear Store.
     */
    clear(): void;

    /**
     * ** Make shallow copy of current Object.
     * @override
     */
    copy(): ErrorStore;
}
