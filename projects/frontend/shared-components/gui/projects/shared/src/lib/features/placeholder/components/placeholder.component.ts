/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import {
    Component,
    ContentChild,
    ElementRef,
    Input,
    OnChanges,
    OnInit,
    Renderer2,
    SimpleChanges,
    TemplateRef,
    ViewChild
} from '@angular/core';
import { HttpStatusCode } from '@angular/common/http';

import { CollectionsUtil } from '../../../utils';

import { ApiErrorMessage, ErrorRecord, TaurusObject } from '../../../common';

import { filterErrorRecords } from '../../../core';

import { PlaceholderService } from '../services';

/* eslint-disable @typescript-eslint/naming-convention */

// empty state
const EmptyMessage = {
    Generic: 'No assets found!'
};

const EmptyImgSource = {
    Generic: 'assets/images/empty/empty-generic.svg'
};

const EmptyImgStyle = {
    Opacity: 1,
    Width: '64px'
};

// error state
const ErrorProblem = {
    Generic: '%s %s currently unavailable',
    Offline: 'No Internet Connection',
    NotFound: '%s %s not found'
};

const ErrorDescription = {
    Generic: '%s can not be loaded, due to technical error on our end.',
    Offline: 'Application recorded network outage.',
    NotFound: `%s for requested identifier does not exist in the system.`
};

const ErrorMitigation = {
    Generic: 'Please try again later.',
    Offline: 'Please check your internet connection.',
    NotFound: ''
};

const ErrorEscalation = {
    Generic: `If the issue persists, please <a href="https://servicedesk.eng.vmware.com/servicedesk/customer/portal/3/group/157?groupId=157" target="_blank" rel="noopener">open a service request.</a>`,
    Offline: '',
    NotFound: `If you think it is a bug, please <a href="https://servicedesk.eng.vmware.com/servicedesk/customer/portal/3/group/157?groupId=157" target="_blank">open a service request.</a>`
};

const ErrorImgSource = {
    Generic: 'assets/images/placeholder/server-error.svg',
    Offline: null,
    NotFound: 'assets/images/placeholder/not-found.svg'
};

const ErrorImgStyle = {
    Opacity: 1,
    Width: {
        Generic: '200px',
        Offline: '280px',
        NotFound: '150px'
    }
};

interface IdentifiedErrorRecordWithMessage {
    record: ErrorRecord[];
    problem: string;
    description: string;
    mitigation: string;
    escalation: string;
    impactedServices: string;
    apiMessage: ApiErrorMessage;
    imageSrc: string;
    imageWidth: string;
    imageOpacity: number;
}

/* eslint-enable @typescript-eslint/naming-convention */

/**
 * ** Generic placeholder component.
 *
 *      - Could be use in generic Component template but also, inside Clarity Datagrid as content projection of <clr-dg-placeholder> component.
 *      - Handles empty state and error state according provided parameters (instructions).
 */
@Component({
    selector: 'shared-placeholder',
    templateUrl: './placeholder.component.html',
    styleUrls: ['./placeholder.component.scss'],
    providers: [PlaceholderService]
})
export class PlaceholderComponent extends TaurusObject implements OnInit, OnChanges {
    /**
     * ** Template ref for system default Error Template.
     *
     *      - Fallback for any Error that doesn't match any of provided custom Error Templates.
     */
    @ViewChild('errorTemplateSystemDefault', { read: TemplateRef }) errorTemplateRefSystemDefault: TemplateRef<never>;

    /**
     * ** Content projection child query for custom Error Template with ID #errorTemplate.
     *
     *      - Template is generic and if provided will be used for every error that doesn't match any other template.
     *      - If not provided will execute next resolution
     *          - fallback to system default Error Template.
     */
    @ContentChild('errorTemplate', { read: TemplateRef }) errorTemplateRefGeneric: TemplateRef<never>;

    /**
     * ** Content projection child query for custom Error Template with ID #errorTemplate4xx.
     *
     *      - Template if provided will be use only for errors that are HttpErrorResponse with status 4xx.
     *      - If not provided will execute next resolution
     *          - try fallback to generic custom Error Template if found, if not go to next resolution
     *          - fallback to system default Error Template.
     */
    @ContentChild('errorTemplate4xx', { read: TemplateRef }) errorTemplateRefClientErrors: TemplateRef<never>;

    /**
     * ** Content projection child query for custom Error Template with ID #errorTemplate400.
     *
     *      - Template if provided will be use only for errors that are HttpErrorResponse with status 400.
     *      - If not provided will execute next resolution
     *          - try fallback to custom Error Template for HttpStatusCodes 4xx if found, if not go to next resolution
     *          - try fallback to generic custom Error Template if found, if not go to next resolution
     *          - fallback to system default Error Template.
     */
    @ContentChild('errorTemplate400', { read: TemplateRef }) errorTemplateRefBadRequest: TemplateRef<never>;

    /**
     * ** Content projection child query for custom Error Template with ID #errorTemplate401.
     *
     *      - Template if provided will be use only for errors that are HttpErrorResponse with status 401.
     *      - If not provided will execute next resolution
     *          - try fallback to custom Error Template for HttpStatusCodes 4xx if found, if not go to next resolution
     *          - try fallback to generic custom Error Template if found, if not go to next resolution
     *          - fallback to system default Error Template.
     */
    @ContentChild('errorTemplate401', { read: TemplateRef }) errorTemplateRefUnauthorized: TemplateRef<never>;

    /**
     * ** Content projection child query for custom Error Template with ID #errorTemplate403.
     *
     *      - Template if provided will be use only for errors that are HttpErrorResponse with status 403.
     *      - If not provided will execute next resolution
     *          - try fallback to custom Error Template for HttpStatusCodes 4xx if found, if not go to next resolution
     *          - try fallback to generic custom Error Template if found, if not go to next resolution
     *          - fallback to system default Error Template.
     */
    @ContentChild('errorTemplate403', { read: TemplateRef }) errorTemplateRefForbidden: TemplateRef<never>;

    /**
     * ** Content projection child query for custom Error Template with ID #errorTemplate404.
     *
     *      - Template if provided will be use only for errors that are HttpErrorResponse with status 404.
     *      - If not provided will execute next resolution
     *          - try fallback to custom Error Template for HttpStatusCodes 4xx if found, if not go to next resolution
     *          - try fallback to generic custom Error Template if found, if not go to next resolution
     *          - fallback to system default Error Template.
     */
    @ContentChild('errorTemplate404', { read: TemplateRef }) errorTemplateRefNotFound: TemplateRef<never>;

    /**
     * ** Content projection child query for custom Error Template with ID #errorTemplate405.
     *
     *      - Template if provided will be use only for errors that are HttpErrorResponse with status 405.
     *      - If not provided will execute next resolution
     *          - try fallback to custom Error Template for HttpStatusCodes 4xx if found, if not go to next resolution
     *          - try fallback to generic custom Error Template if found, if not go to next resolution
     *          - fallback to system default Error Template.
     */
    @ContentChild('errorTemplate405', { read: TemplateRef }) errorTemplateRefMethodNotAllowed: TemplateRef<never>;

    /**
     * ** Content projection child query for custom Error Template with ID #errorTemplate409.
     *
     *      - Template if provided will be use only for errors that are HttpErrorResponse with status 409.
     *      - If not provided will execute next resolution
     *          - try fallback to custom Error Template for HttpStatusCodes 4xx if found, if not go to next resolution
     *          - try fallback to generic custom Error Template if found, if not go to next resolution
     *          - fallback to system default Error Template.
     */
    @ContentChild('errorTemplate409', { read: TemplateRef }) errorTemplateRefConflict: TemplateRef<never>;

    /**
     * ** Content projection child query for custom Error Template with ID #errorTemplate422.
     *
     *      - Template if provided will be use only for errors that are HttpErrorResponse with status 422.
     *      - If not provided will execute next resolution
     *          - try fallback to custom Error Template for HttpStatusCodes 4xx if found, if not go to next resolution
     *          - try fallback to generic custom Error Template if found, if not go to next resolution
     *          - fallback to system default Error Template.
     */
    @ContentChild('errorTemplate422', { read: TemplateRef }) errorTemplateRefUnprocessableEntity: TemplateRef<never>;

    /**
     * ** Content projection child query for custom Error Template with ID #errorTemplate5xx.
     *
     *      - Template if provided will be use only for errors that are HttpErrorResponse with status 5xx.
     *      - If not provided will execute next resolution
     *          - try fallback to generic custom Error Template if found, if not go to next resolution
     *          - fallback to system default Error Template.
     */
    @ContentChild('errorTemplate5xx', { read: TemplateRef }) errorTemplateRefServerErrors: TemplateRef<never>;

    /**
     * ** Content projection child query for custom Error Template with ID #errorTemplate500.
     *
     *      - Template if provided will be use only for errors that are HttpErrorResponse with status 500.
     *      - If not provided will execute next resolution
     *          - try fallback to custom Error Template for HttpStatusCodes 5xx if found, if not go to next resolution
     *          - try fallback to generic custom Error Template if found, if not go to next resolution
     *          - fallback to system default Error Template.
     */
    @ContentChild('errorTemplate500', { read: TemplateRef }) errorTemplateRefInternalServerError: TemplateRef<never>;

    /**
     * ** Content projection child query for custom Error Template with ID #errorTemplate503.
     *
     *      - Template if provided will be use only for errors that are HttpErrorResponse with status 503.
     *      - If not provided will execute next resolution
     *          - try fallback to custom Error Template for HttpStatusCodes 5xx if found, if not go to next resolution
     *          - try fallback to generic custom Error Template if found, if not go to next resolution
     *          - fallback to system default Error Template.
     */
    @ContentChild('errorTemplate503', { read: TemplateRef }) errorTemplateRefServiceUnavailable: TemplateRef<never>;

    /**
     * ** Content projection child query for custom Empty Template with ID #emptyTemplate.
     *
     *      - Template if provided will be use for empty state otherwise fallback to system default Empty State Template.
     */
    @ContentChild('emptyTemplate', { read: TemplateRef }) emptyTemplateRef: TemplateRef<never>;

    /**
     * ** Boolean flag that identifies if parent is loading data.
     */
    @Input() loading: boolean;

    // empty state

    /**
     * ** Text for empty state, if component is rendered without errors or there is no listened error code(s).
     */
    @Input() set emptyMessage(value: string) {
        if (CollectionsUtil.isString(value) && value.length > 0) {
            this._isEmptyMessageExternal = true;
            this._emptyMessage = value;
        } else {
            this._isEmptyMessageExternal = false;
            this._emptyMessage = EmptyMessage.Generic;
        }
    }

    /**
     * ** Text for empty state.
     *
     *      - Visualized only if component is rendered without errors or there is no listened error code(s).
     */
    get emptyMessage(): string {
        return this._emptyMessage;
    }

    /**
     * ** Empty state image source url.
     *
     *      - Visualized only if component is rendered without errors or there is no listened error code(s).
     */
    @Input() set emptyImgSrc(value: string) {
        if (CollectionsUtil.isString(value) && value.length > 0) {
            this._isEmptyImgSrcExternal = true;
            this._emptyImgSrc = value;
        } else {
            this._isEmptyImgSrcExternal = false;
            this._emptyImgSrc = EmptyImgSource.Generic;
        }
    }

    /**
     * ** Empty state image source url.
     *
     *      - Visualized only if component is rendered without errors or there is no listened error code(s).
     */
    get emptyImgSrc(): string {
        return this._emptyImgSrc;
    }

    /**
     * ** Empty state image width.
     *
     *      - Visualized only if component is rendered without errors or there is no listened error code(s).
     */
    @Input() set emptyImgWidth(value: string) {
        if (CollectionsUtil.isString(value) && value.length > 0) {
            this._emptyImgWidth = value;
        } else {
            this._emptyImgWidth = EmptyImgStyle.Width;
        }
    }

    /**
     * ** Empty state image width.
     *
     *      - Visualized only if component is rendered without errors or there is no listened error code(s).
     */
    get emptyImgWidth(): string {
        return this._emptyImgWidth;
    }

    /**
     * ** Empty state image opacity.
     *
     *      - Visualized only if component is rendered without errors or there is no listened error code(s).
     */
    @Input() set emptyImgOpacity(value: number) {
        if (CollectionsUtil.isNumber(value) && value >= 1 && value <= 1) {
            this._emptyImgOpacity = value;
        } else {
            this._emptyImgOpacity = EmptyImgStyle.Opacity;
        }
    }

    /**
     * ** Empty state image opacity.
     *
     *      - Visualized only if component is rendered without errors or there is no listened error code(s).
     */
    get emptyImgOpacity(): number {
        return this._emptyImgOpacity;
    }

    /**
     * ** Flag to show or hide custom empty state image.
     *
     *      - default value is FALSE.
     */
    @Input() showCustomEmptyStateImage = false;

    /**
     * ** Flag to show or hide default empty state image in grid.
     *
     *      - default value is FALSE.
     */
    @Input() hideDefaultEmptyStateImageInGrid = false;

    // error state

    /**
     * ** Errors queue of ErrorRecords injected from parents transitive.
     */
    @Input() set errorsQueue(value: ErrorRecord[]) {
        if (CollectionsUtil.isArray(value)) {
            this._errorsQueue = value;
        } else {
            this._errorsQueue = [];
        }
    }

    /**
     * ** Errors queue of ErrorRecords injected from parents transitive.
     */
    get errorsQueue(): ErrorRecord[] {
        return this._errorsQueue;
    }

    /**
     * ** Flag to instruct component to show all processed error or to peak the most important one, which is latest, according the HTTP Status code.
     */
    @Input() renderAllErrors = false;

    /**
     * ** Array of error codes for which Placeholder should listen and on ChangeDetection cycle to look for exact match into errorsQueue.
     */
    @Input() listenForErrors: string[] = [];

    /**
     * ** Array of error codes pattern for which Placeholder should listen and on ChangeDetection cycle to look for match into errorsQueue.
     */
    @Input() listenForErrorPatterns: string[] = [];

    /**
     * ** Error context.
     *
     *      - Visualized only if listened error code(s) exist in errorsQueue.
     */
    get errorContext(): string {
        return this._errorContext;
    }

    /**
     * ** Error context.
     */
    @Input() set errorContext(value: string) {
        if (CollectionsUtil.isString(value) && value.length > 0) {
            this._errorContext = value;
        } else {
            this._errorContext = 'Page data';
        }
    }

    /**
     * ** Context singular or plural.
     *
     *      - If true - it's plural
     *      - If false - it's singular
     */
    @Input() plural = false;

    /**
     * ** Flag that identifies if error ot empty state template should be rendered.
     */
    showError = false;

    /**
     * ** Flag that indicates for error template is used system default.
     */
    isErrorTemplateSystemDefault = false;

    /**
     * ** Identified ErrorRecords in {@link errorsQueue} that exact match {@link listenForErrors} or match {@link listenForErrorPatterns}
     *
     *      - injected to custom error template if provided
     *      - used when only one error should be shown
     */
    identifiedErrors: ErrorRecord[] = [];

    /**
     * ** Identified ErrorRecord in {@link errorsQueue} that exact match {@link listenForErrors} or match {@link listenForErrorPatterns}
     *
     *      - injected to custom error template if provided
     *      - used when only one error should be shown
     */
    identifiedErrorWithApiMessage: IdentifiedErrorRecordWithMessage = {
        record: [],
        problem: '',
        description: '',
        mitigation: '',
        escalation: '',
        impactedServices: '',
        apiMessage: null,
        imageSrc: '',
        imageWidth: ErrorImgStyle.Width.Generic,
        imageOpacity: ErrorImgStyle.Opacity
    };

    /**
     * ** Identified ErrorRecords in {@link errorsQueue} that exact match {@link listenForErrors} or match {@link listenForErrorPatterns}
     *
     *      - injected to custom error template if provided
     *      - used if iteration of errors is requested
     */
    identifiedErrorsWithApiMessage: IdentifiedErrorRecordWithMessage[] = [];

    // empty state private fields
    private _emptyMessage = EmptyMessage.Generic;
    private _isEmptyMessageExternal = false;

    private _emptyImgSrc: string = EmptyImgSource.Generic;
    private _isEmptyImgSrcExternal = false;

    private _emptyImgWidth = EmptyImgStyle.Width;
    private _emptyImgOpacity = EmptyImgStyle.Opacity;

    private _hideDefaultEmptyStateImageInGrid = false;

    // error state private fields
    private _errorsQueue: ErrorRecord[] = [];

    private _errorContext = 'Page data';

    /**
     * ** Constructor.
     */
    constructor(
        private readonly elementRef: ElementRef<HTMLElement>,
        private readonly renderer2: Renderer2,
        private readonly placeholderService: PlaceholderService
    ) {
        super();
    }

    /**
     * ** Resolves custom or system error for identified Error.
     */
    resolveErrorTemplate(identifiedErrorRecordWithMessage: IdentifiedErrorRecordWithMessage): TemplateRef<never> {
        const httpStatusCode = identifiedErrorRecordWithMessage?.record[0]?.httpStatusCode;

        let templateRef: TemplateRef<never>;

        // find exact match for custom template depend on Http Status Code
        switch (httpStatusCode) {
            case HttpStatusCode.BadRequest:
                templateRef = this.errorTemplateRefBadRequest;
                break;
            case HttpStatusCode.Unauthorized:
                templateRef = this.errorTemplateRefUnauthorized;
                break;
            case HttpStatusCode.Forbidden:
                templateRef = this.errorTemplateRefForbidden;
                break;
            case HttpStatusCode.NotFound:
                templateRef = this.errorTemplateRefNotFound;
                break;
            case HttpStatusCode.MethodNotAllowed:
                templateRef = this.errorTemplateRefMethodNotAllowed;
                break;
            case HttpStatusCode.Conflict:
                templateRef = this.errorTemplateRefConflict;
                break;
            case HttpStatusCode.UnprocessableEntity:
                templateRef = this.errorTemplateRefUnprocessableEntity;
                break;
            case HttpStatusCode.InternalServerError:
                templateRef = this.errorTemplateRefInternalServerError;
                break;
            case HttpStatusCode.ServiceUnavailable:
                templateRef = this.errorTemplateRefServiceUnavailable;
                break;
            default:
            // No-op.
        }

        this.isErrorTemplateSystemDefault = false;

        // if found exact match for custom template to Http Status Code return immediately
        if (templateRef instanceof TemplateRef) {
            return templateRef;
        }

        // find match for custom template depend on group 4xx of Http Status Codes
        if (httpStatusCode >= 400 && httpStatusCode < 500 && this.errorTemplateRefClientErrors instanceof TemplateRef) {
            return this.errorTemplateRefClientErrors;
        }

        // find match for custom template depend on group 5xx of Http Status Codes
        if (httpStatusCode >= 500 && this.errorTemplateRefServerErrors instanceof TemplateRef) {
            return this.errorTemplateRefServerErrors;
        }

        // fallback to custom generic error template
        if (this.errorTemplateRefGeneric instanceof TemplateRef) {
            return this.errorTemplateRefGeneric;
        }

        this.isErrorTemplateSystemDefault = true;

        // return system default error template
        return this.errorTemplateRefSystemDefault;
    }

    /**
     * @inheritDoc
     */
    ngOnChanges(changes: SimpleChanges): void {
        if (
            PlaceholderComponent._isPropertyChanged(changes, 'loading') ||
            PlaceholderComponent._isPropertyChanged(changes, 'errorsQueue') ||
            PlaceholderComponent._isPropertyChanged(changes, 'listenForErrors') ||
            PlaceholderComponent._isPropertyChanged(changes, 'listenForErrorPatterns')
        ) {
            this._executeRefineCycle();
        }
    }

    /**
     * @inheritDoc
     */
    ngOnInit(): void {
        this._executeRefineCycle();
    }

    private _executeRefineCycle(): void {
        try {
            this._refineErrorState();
            this.placeholderService.refineElementsState(this.elementRef, this._hideDefaultEmptyStateImageInGrid);
        } catch (e) {
            console.error(e);
        }
    }

    private _refineErrorState(): void {
        // filter error records and return only records that for component is listening
        const filteredErrorRecords = filterErrorRecords(this.errorsQueue, this.listenForErrors, this.listenForErrorPatterns);

        // listened errors records exist, then show error state
        this.showError = filteredErrorRecords.length > 0;

        // check is empty state image in grid should be hidden
        // if error always hide
        // if empty hide/show depends on injected flag
        this._hideDefaultEmptyStateImageInGrid = this.showError || this.hideDefaultEmptyStateImageInGrid;

        // reset buffers that transport data to view template (HTML template)
        this._resetTransportBuffers();

        if (!this.showError) {
            return;
        }

        // populate buffers that transport data to view template (HTML template)
        this._populateTransportBuffers(filteredErrorRecords);
    }

    private _resetTransportBuffers(): void {
        this.identifiedErrors = [];

        this.identifiedErrorWithApiMessage = {
            record: [],
            problem: '',
            description: '',
            mitigation: '',
            escalation: '',
            impactedServices: '',
            apiMessage: null,
            imageSrc: '',
            imageWidth: ErrorImgStyle.Width.Generic,
            imageOpacity: ErrorImgStyle.Opacity
        };
        this.identifiedErrorsWithApiMessage = [];
    }

    private _populateTransportBuffers(errorRecords: ErrorRecord[]): void {
        this.identifiedErrors = [...errorRecords];
        this.identifiedErrorWithApiMessage = this._getErrorsToIdentifiedError(errorRecords);
        this.identifiedErrorsWithApiMessage = errorRecords.map((record) => this._getErrorToIdentifiedError(record));
    }

    private _getErrorToIdentifiedError(record: ErrorRecord): IdentifiedErrorRecordWithMessage {
        if (window && window.navigator && !window.navigator.onLine) {
            return {
                record: [record],
                problem: ErrorProblem.Offline,
                description: ErrorDescription.Offline,
                mitigation: ErrorMitigation.Offline,
                escalation: ErrorEscalation.Offline,
                impactedServices: '',
                apiMessage: this.placeholderService.extractErrorInformation(record.error),
                imageSrc: ErrorImgSource.Offline,
                imageWidth: ErrorImgStyle.Width.Offline,
                imageOpacity: ErrorImgStyle.Opacity
            };
        }

        if (record && record.httpStatusCode === HttpStatusCode.NotFound) {
            return {
                record: [record],
                problem: CollectionsUtil.interpolateString(ErrorProblem.NotFound, this._errorContext, this.plural ? 'are' : 'is'),
                description: CollectionsUtil.interpolateString(ErrorDescription.NotFound, this._errorContext, this.plural ? 'are' : 'is'),
                mitigation: ErrorMitigation.NotFound,
                escalation: ErrorEscalation.NotFound,
                impactedServices: '',
                apiMessage: this.placeholderService.extractErrorInformation(record.error),
                imageSrc: ErrorImgSource.NotFound,
                imageWidth: ErrorImgStyle.Width.NotFound,
                imageOpacity: ErrorImgStyle.Opacity
            };
        }

        return {
            record: [record],
            problem: CollectionsUtil.interpolateString(ErrorProblem.Generic, this._errorContext, this.plural ? 'are' : 'is'),
            description: CollectionsUtil.interpolateString(ErrorDescription.Generic, this._errorContext, this.plural ? 'are' : 'is'),
            mitigation: ErrorMitigation.Generic,
            escalation: ErrorEscalation.Generic,
            impactedServices: PlaceholderService.extractClassPublicName(record),
            apiMessage: this.placeholderService.extractErrorInformation(record.error),
            imageSrc: ErrorImgSource.Generic,
            imageWidth: ErrorImgStyle.Width.Generic,
            imageOpacity: ErrorImgStyle.Opacity
        };
    }

    private _getErrorsToIdentifiedError(errorRecords: ErrorRecord[]): IdentifiedErrorRecordWithMessage {
        if (window && window.navigator && !window.navigator.onLine) {
            return {
                record: errorRecords,
                problem: ErrorProblem.Offline,
                description: ErrorDescription.Offline,
                mitigation: ErrorMitigation.Offline,
                escalation: ErrorEscalation.Offline,
                impactedServices: '',
                apiMessage: this.placeholderService.extractErrorInformation(new Error('No Internet Connection')),
                imageSrc: ErrorImgSource.Offline,
                imageWidth: ErrorImgStyle.Width.Offline,
                imageOpacity: ErrorImgStyle.Opacity
            };
        }

        const latestIdentifiedError: ErrorRecord = errorRecords[0];
        let filteredErrors: ErrorRecord[] = [];
        let filteredErrorsTmp: ErrorRecord[];

        // search for ServiceUnavailable 503
        filteredErrorsTmp = errorRecords.filter((r) => r.httpStatusCode === HttpStatusCode.ServiceUnavailable);
        if (filteredErrorsTmp.length > 0) {
            // if time between latest and identified service unavailable is less than 2s show Service Unavailable
            if (latestIdentifiedError.code === filteredErrorsTmp[0].code || latestIdentifiedError.time - filteredErrorsTmp[0].time < 2000) {
                filteredErrors = filteredErrorsTmp;
            }
        }

        // search for InternalServerError 500
        filteredErrorsTmp = errorRecords.filter((r) => r.httpStatusCode === HttpStatusCode.InternalServerError);
        if (filteredErrors.length === 0 && filteredErrorsTmp.length > 0) {
            // if time between latest and identified internal server error is less than 2s show Internal Server Error
            if (latestIdentifiedError.code === filteredErrorsTmp[0].code || latestIdentifiedError.time - filteredErrorsTmp[0].time < 2000) {
                filteredErrors = filteredErrorsTmp;
            }
        }

        // search for NotFound 404
        filteredErrorsTmp = errorRecords.filter((r) => r.httpStatusCode === HttpStatusCode.NotFound);
        if (filteredErrors.length === 0 && filteredErrorsTmp.length > 0) {
            // if time between latest and identified not found is less than 2s show Not Found
            if (latestIdentifiedError.code === filteredErrorsTmp[0].code || latestIdentifiedError.time - filteredErrorsTmp[0].time < 2000) {
                filteredErrors = filteredErrorsTmp;

                return {
                    record: filteredErrors,
                    problem: CollectionsUtil.interpolateString(ErrorProblem.NotFound, this._errorContext, this.plural ? 'are' : 'is'),
                    description: CollectionsUtil.interpolateString(
                        ErrorDescription.NotFound,
                        this._errorContext,
                        this.plural ? 'are' : 'is'
                    ),
                    mitigation: ErrorMitigation.NotFound,
                    escalation: ErrorEscalation.NotFound,
                    impactedServices: '',
                    apiMessage: this.placeholderService.extractErrorInformation(filteredErrors[0].error),
                    imageSrc: ErrorImgSource.NotFound,
                    imageWidth: ErrorImgStyle.Width.NotFound,
                    imageOpacity: ErrorImgStyle.Opacity
                };
            }
        }

        // fallback to all identified services
        if (filteredErrors.length === 0) {
            filteredErrors = errorRecords;
        }

        return {
            record: filteredErrors,
            problem: CollectionsUtil.interpolateString(ErrorProblem.Generic, this._errorContext, this.plural ? 'are' : 'is'),
            description: CollectionsUtil.interpolateString(ErrorDescription.Generic, this._errorContext),
            mitigation: ErrorMitigation.Generic,
            escalation: ErrorEscalation.Generic,
            impactedServices: PlaceholderService.extractClassesPublicNames(filteredErrors),
            apiMessage: this.placeholderService.extractErrorInformation(filteredErrors[0].error),
            imageSrc: ErrorImgSource.Generic,
            imageWidth: ErrorImgStyle.Width.Generic,
            imageOpacity: ErrorImgStyle.Opacity
        };
    }

    private static _isPropertyChanged(changes: SimpleChanges, field: string): boolean {
        return changes[field] && changes[field].currentValue !== changes[field].previousValue;
    }
}
