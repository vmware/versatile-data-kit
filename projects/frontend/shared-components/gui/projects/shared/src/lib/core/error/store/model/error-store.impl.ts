/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpStatusCode } from '@angular/common/http';

import { CollectionsUtil } from '../../../../utils';

import { ErrorRecord, ErrorStore, ErrorStoreChangeListener } from '../../../../common';

/**
 * @inheritDoc
 *
 * ** ErrorStore implementation.
 */
export class ErrorStoreImpl implements ErrorStore {
    /**
     * ** Factory method.
     */
    static of(errorRecords: ErrorRecord[]): ErrorStoreImpl {
        return new ErrorStoreImpl(errorRecords);
    }

    /**
     * ** Factory method that returns empty store.
     */
    static empty(): ErrorStoreImpl {
        return ErrorStoreImpl.of(null);
    }

    /**
     * ** Creates ErrorStore from literal.
     */
    static fromLiteral(errorRecords: ErrorRecord[]): ErrorStoreImpl {
        return ErrorStoreImpl.of(ErrorStoreImpl.cloneDeepErrorRecords(errorRecords));
    }

    /**
     * ** Clone deep provided ErrorRecords.
     */
    static cloneDeepErrorRecords(errorRecords: ErrorRecord[]): ErrorRecord[] {
        return (errorRecords ?? []).map((r) => ({ ...r }));
    }

    /**
     * @inheritDoc
     */
    records: ErrorRecord[];

    /**
     * @inheritDoc
     */
    changeListeners: Array<ErrorStoreChangeListener<ErrorStoreImpl>>;

    /**
     * ** Constructor.
     */
    constructor(errorRecords: ErrorRecord[] = []) {
        this.records = errorRecords ?? [];
        this.changeListeners = [];
    }

    /**
     * @inheritDoc
     */
    hasErrors(): boolean {
        return this.records.length > 0;
    }

    /**
     * @inheritDoc
     */
    hasCode(...errorCodes: string[]): boolean {
        return errorCodes.some((code) => this.records.findIndex((r) => r.code === code) !== -1);
    }

    /**
     * @inheritDoc
     */
    hasCodePattern(...errorCodesPatterns: string[]): boolean {
        try {
            return errorCodesPatterns.some((errorPattern) => {
                if (!CollectionsUtil.isString(errorPattern)) {
                    return false;
                }

                const errorPatternRegex = new RegExp(errorPattern);

                return this.records.findIndex((r) => errorPatternRegex.test(r.code)) !== -1;
            });
        } catch (e) {
            console.error(e);

            return false;
        }
    }

    /**
     * @inheritDoc
     */
    record(errorCode: string, objectUUID: string, error: Error, httpStatusCode?: HttpStatusCode): void;
    /**
     * @inheritDoc
     */
    record(errorRecord: ErrorRecord): void;
    record(param: string | ErrorRecord, objectUUID?: string, error?: Error, httpStatusCode?: HttpStatusCode): void {
        const errorRecordsShallowCopy = [...this.records];

        if (CollectionsUtil.isString(param) && CollectionsUtil.isString(objectUUID)) {
            const foundIndex = errorRecordsShallowCopy.findIndex((r) => r.code === param && r.objectUUID === objectUUID);
            const errorRecord: ErrorRecord = {
                code: param,
                objectUUID,
                time: CollectionsUtil.dateNow(),
                error: error ?? null,
                httpStatusCode: httpStatusCode ?? null
            };

            if (foundIndex === -1) {
                errorRecordsShallowCopy.push(errorRecord);
            } else {
                errorRecordsShallowCopy.splice(foundIndex, 1, errorRecord);
            }
        } else if (CollectionsUtil.isLiteralObject(param) && CollectionsUtil.isNil(objectUUID)) {
            const foundIndex = errorRecordsShallowCopy.findIndex(
                (r) => r.code === (param as ErrorRecord).code && r.objectUUID === (param as ErrorRecord).objectUUID
            );
            const errorRecord: ErrorRecord = {
                ...(param as ErrorRecord),
                time: CollectionsUtil.dateNow()
            };

            if (foundIndex === -1) {
                errorRecordsShallowCopy.push(errorRecord);
            } else {
                errorRecordsShallowCopy.splice(foundIndex, 1, errorRecord);
            }
        }

        this.records = errorRecordsShallowCopy;

        ErrorStoreImpl._executeChangeListeners(this, this.changeListeners);
    }

    /**
     * @inheritDoc
     */
    removeCode(...errorCodes: string[]): void {
        let errorRecordsShallowCopy = [...this.records];

        try {
            errorRecordsShallowCopy = errorRecordsShallowCopy.filter((r) => !errorCodes.includes(r.code));
        } catch (e) {
            console.error(e);
        }

        this.records = errorRecordsShallowCopy;

        ErrorStoreImpl._executeChangeListeners(this, this.changeListeners);
    }

    /**
     * @inheritDoc
     */
    removeCodePattern(...errorCodePatterns: string[]): void {
        let errorCodesShallowCopy = [...this.records];

        for (const errorPattern of errorCodePatterns) {
            try {
                if (!CollectionsUtil.isString(errorPattern)) {
                    continue;
                }

                const errorPatternRegex = new RegExp(errorPattern);

                errorCodesShallowCopy = errorCodesShallowCopy.filter((r) => !errorPatternRegex.test(r.code));
            } catch (e) {
                console.error(e);
            }
        }

        this.records = errorCodesShallowCopy;

        ErrorStoreImpl._executeChangeListeners(this, this.changeListeners);
    }

    /**
     * @inheritDoc
     */
    findRecords(...errorCodes: string[]): ErrorRecord[] {
        return this.records.filter((r) => errorCodes.includes(r.code));
    }

    /**
     * @inheritDoc
     */
    findRecordsByPattern(...errorCodePatterns: string[]): ErrorRecord[] {
        let foundRecords: ErrorRecord[] = [];

        for (const errorPattern of errorCodePatterns) {
            try {
                if (!CollectionsUtil.isString(errorPattern)) {
                    continue;
                }

                const errorPatternRegex = new RegExp(errorPattern);

                const filteredRecords = this.records.filter((r) => errorPatternRegex.test(r.code));

                foundRecords = foundRecords.concat(...filteredRecords);
            } catch (e) {
                console.error(e);
            }
        }

        return foundRecords;
    }

    /**
     * @inheritDoc
     */
    distinctErrorRecords(errorRecords: ErrorRecord[]): ErrorRecord[] {
        const _errorRecords: ErrorRecord[] = CollectionsUtil.isArray(errorRecords) ? errorRecords : [];

        return this.records.filter(
            (r) => _errorRecords.findIndex((rInjected) => ErrorStoreImpl._checkErrorRecordsEquality(r, rInjected)) === -1
        );
    }

    /**
     * @inheritDoc
     */
    purge(injectedStore: ErrorStoreImpl): void {
        if (!(injectedStore instanceof ErrorStoreImpl)) {
            return;
        }

        if (this.equals(injectedStore)) {
            return;
        }

        this.records = [...injectedStore.records];

        ErrorStoreImpl._executeChangeListeners(this, this.changeListeners);
    }

    /**
     * @inheritDoc
     */
    onChange(callback: (store: this) => void): void {
        if (CollectionsUtil.isFunction(callback)) {
            this.changeListeners.push(callback);
        }
    }

    /**
     * @inheritDoc
     */
    dispose(): void {
        this.clear();

        this.changeListeners = [];
    }

    /**
     * @inheritDoc
     */
    clear(): void {
        try {
            this.records.length = 0;
            this.records = [];
        } catch (e) {
            console.error(e);
        }
    }

    /**
     * @inheritDoc
     */
    toLiteral(): ErrorRecord[] {
        return [...this.records];
    }

    /**
     * @inheritDoc
     */
    toLiteralCloneDeep(): ErrorRecord[] {
        return this.records.map((r) => {
            return { ...r };
        });
    }

    /**
     * @inheritDoc
     */
    copy(): ErrorStoreImpl {
        return ErrorStoreImpl.of([...this.records]);
    }

    /**
     * @inheritDoc
     */
    equals(obj: ErrorStore): boolean {
        if (!(obj instanceof ErrorStoreImpl)) {
            return false;
        }

        if (this.records.length !== obj.records.length) {
            return false;
        }

        for (let i = 0; i < this.records.length; i++) {
            if (!ErrorStoreImpl._checkErrorRecordsEquality(this.records[i], obj.records[i])) {
                return false;
            }
        }

        return true;
    }

    private static _checkErrorRecordsEquality(errorRecord1: ErrorRecord, errorRecord2: ErrorRecord): boolean {
        if (errorRecord1.code !== errorRecord2.code) {
            return false;
        }

        if (errorRecord1.objectUUID !== errorRecord2.objectUUID) {
            return false;
        }

        if (errorRecord1.time !== errorRecord2.time) {
            return false;
        }

        if (errorRecord1.httpStatusCode !== errorRecord2.httpStatusCode) {
            return false;
        }

        return errorRecord1.error === errorRecord2.error;
    }

    private static _executeChangeListeners(store: ErrorStoreImpl, changeListeners: Array<ErrorStoreChangeListener<ErrorStore>>): void {
        if (!CollectionsUtil.isArray(changeListeners) || changeListeners.length === 0) {
            return;
        }

        for (const listener of changeListeners) {
            try {
                listener(store);
            } catch (e) {
                console.error(`Taurus ErrorStore failed to execute change listeners`, e);
            }
        }
    }
}

/**
 * ** Filter errorRecords and left only records of interests, that exact match provided errorCodes or match provided errorCodesPatterns.
 * @protected
 */
export const filterErrorRecords = (
    errorRecords: ErrorRecord[],
    errorCodes: string[] = [],
    errorCodesPatterns: string[] = []
): ErrorRecord[] => {
    const errorPatternsRegex: RegExp[] = [];

    try {
        (errorCodesPatterns ?? []).forEach((errorPattern) => {
            if (!CollectionsUtil.isString(errorPattern)) {
                return;
            }

            errorPatternsRegex.push(new RegExp(errorPattern));
        });
    } catch (e) {
        console.error(e);
    }

    return [...errorRecords]
        .sort((r1, r2) => r2.time - r1.time)
        .filter((r) => {
            return (errorCodes ?? []).includes(r.code) || errorPatternsRegex.some((errorPatternRegex) => errorPatternRegex.test(r.code));
        });
};
