/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, EventEmitter, Input, OnChanges, OnDestroy, OnInit, Output, SimpleChanges, ViewChild } from '@angular/core';
import { FormBuilder, FormControl, FormGroup } from '@angular/forms';

import { CalendarValue, DatePickerDirective, IDatePickerDirectiveConfig } from 'ng2-date-picker';

// TODO [import dayjs from 'dayjs'] used in ng2-date-picker v13+ instead of moment
import moment from 'moment';

import { CollectionsUtil } from '@versatiledatakit/shared';

import { FiltersSortManager } from '../../../../../commons';

import { DATA_PIPELINES_DATE_TIME_FORMAT } from '../../../../../model';

import { ExecutionsFilterCriteria, FILTER_TIME_PERIOD_KEY } from '../model';

type CustomFormGroup = FormGroup & { controls: { [key: string]: FormControl } };

interface DateTimePeriod {
    from: Date;
    to: Date;
}

@Component({
    selector: 'lib-time-period-filter',
    templateUrl: './time-period-filter.component.html',
    styleUrls: ['./time-period-filter.component.scss']
})
export class TimePeriodFilterComponent implements OnInit, OnChanges, OnDestroy {
    @ViewChild('fromPicker') fromPicker: DatePickerDirective;
    @ViewChild('toPicker') toPicker: DatePickerDirective;

    /**
     * ** Whether component is in state loading.
     */
    @Input() loading = false;

    /**
     * ** Flag that indicates there is jobs executions load error.
     */
    @Input() isComponentInErrorState = false;

    /**
     * ** Executions filters sort manager injected from parent.
     */
    @Input() filtersSortManager: Readonly<FiltersSortManager<ExecutionsFilterCriteria, string>>;

    /**
     * ** Date time period serialized in string format with pattern "{{epochDateTime}}-{{epochDateTime}}".
     */
    @Input() selectedPeriodSerialized: string;

    /**
     * ** Date time period in raw format of type object with field from and to of type Date.
     */
    @Input() selectedPeriod: DateTimePeriod;

    /**
     * ** Minimum available for selection DateTime in UTC.
     */
    @Input() minDateTime: Date;

    /**
     * ** Event Emitter that emits events on every user form action like submit or clear.
     */
    @Output() filterChanged: EventEmitter<DateTimePeriod> = new EventEmitter<DateTimePeriod>();

    pickerConfig: IDatePickerDirectiveConfig = {
        // TODO [format: 'MMM DD, YYYY, hh:mm:ss A',] dayjs
        format: 'MMM DD, yyyy, hh:mm:ss A',
        showGoToCurrent: true,
        showTwentyFourHours: false,
        showSeconds: true,
        weekDayFormat: 'dd',
        numOfMonthRows: 6,
        monthBtnFormat: 'MMMM'
    };
    fromPickerConfig: IDatePickerDirectiveConfig = {
        ...this.pickerConfig
    };
    toPickerConfig: IDatePickerDirectiveConfig = {
        ...this.pickerConfig
    };

    /**
     * ** User selected value for "FROM" time date picker.
     */
    fromDateTime: Date = null;

    /**
     * ** User selected value for "TO" time date picker.
     */
    toDateTime: Date = null;

    /**
     * ** DateTime format pattern provided to Angular DateTime pipe.
     */
    dateTimeFormat: string = DATA_PIPELINES_DATE_TIME_FORMAT;

    /**
     * ** Allowed ranges for "fromDateTime" time date picker.
     */
    // "FROM" time min allowed value is used from {@link this.minDateTime}
    fromDateTimeMin: moment.Moment;
    // "FROM" time max allowed value is less than {@link this.toDateTimeMin}
    fromDateTimeMax: moment.Moment;

    /**
     * ** Allowed ranges for "toDateTime" time date picker.
     */
    // "TO" time min allowed value is less than {@link this.fromDateTimeMax}
    toDateTimeMin: moment.Moment;
    // "TO" time max allowed value for selection is current time. There is scheduled interval on 15s that updates this value.
    // TODO check if will work without upper range
    toDateTimeMax: moment.Moment;

    /**
     * ** Angular form where DatePicker inputs belongs.
     */
    tmForm: CustomFormGroup;

    private _isFromPickerOpened = false;
    private _isToPickerOpened = false;

    private _initiallySetMin = false;
    private _initiallySetMax = false;

    // refresh interval scheduled reference
    private _refreshIntervalRef: number;

    private _previousSelectedPeriodSerialized: string;

    private _isUrlNormalized = false;

    /**
     * ** Constructor.
     */
    constructor(private readonly formBuilder: FormBuilder) {
        this.tmForm = this.formBuilder.group({
            fromDateTime: '',
            toDateTime: ''
        }) as CustomFormGroup;
    }

    onDateTimeChange($event: CalendarValue, type: 'from' | 'to'): void {
        if (CollectionsUtil.isNil($event)) {
            return;
        }

        const emittedDate = $event as moment.Moment;

        if (type === 'from') {
            if (emittedDate.isBefore(this.fromDateTimeMin) || emittedDate.isAfter(this.fromDateTimeMax)) {
                return;
            }

            this.toDateTimeMin = this._adjustDateTime(emittedDate, 'min');
            this.toPickerConfig = {
                ...this.toPickerConfig,
                min: this.toDateTimeMin
            };

            this.fromDateTime = new Date(this._adjustDateTime(emittedDate, 'from', 'timezone').valueOf());
        } else {
            if (emittedDate.isBefore(this.toDateTimeMin) || emittedDate.isAfter(this.toDateTimeMax)) {
                return;
            }

            this.fromDateTimeMax = this._adjustDateTime(emittedDate, 'max');
            this.fromPickerConfig = {
                ...this.fromPickerConfig,
                max: this.fromDateTimeMax
            };

            this.toDateTime = new Date(this._adjustDateTime(emittedDate, 'to', 'timezone').valueOf());
        }
    }

    togglePicker($event: MouseEvent, type: 'from' | 'to'): void {
        $event.preventDefault();

        if (type === 'from') {
            if (this._isFromPickerOpened) {
                this.fromPicker.api.close();
            } else {
                this.fromPicker.api.open();
            }
        } else {
            if (this._isToPickerOpened) {
                this.toPicker.api.close();
            } else {
                this.toPicker.api.open();
            }
        }
    }

    onPickerOpened(type: 'from' | 'to', isOpened: boolean): void {
        if (type === 'from') {
            this._isFromPickerOpened = isOpened;
        } else {
            this._isToPickerOpened = isOpened;
        }
    }

    /**
     * ** Apply selected values and emit.
     */
    applyFilter($event: Event): void {
        $event?.preventDefault();

        this._updateFiltersSortManager();
        this._emitChanges();
    }

    /**
     * ** Clear selected values and emit.
     */
    clearFilter($event: MouseEvent, triggerMinMaxDateTimeChangeDetection = false): void {
        $event?.preventDefault();

        this._initiallySetMin = false;
        this._initiallySetMax = false;

        this.fromDateTime = null;
        this.toDateTime = null;

        this._updateFiltersSortManager();
        this._emitChanges();

        if (triggerMinMaxDateTimeChangeDetection) {
            this._changeDetectionMinDateTime();

            this._changeDetectionMaxDateTime();
        }
    }

    /**
     * @inheritDoc
     */
    ngOnChanges(changes: SimpleChanges): void {
        if (changes['selectedPeriodSerialized']) {
            this._changeDetectionSelectedPeriodSerialized();
        }

        if (changes['selectedPeriod'] && !changes['selectedPeriod'].firstChange) {
            this._changeDetectionSelectedPeriod();
        }

        if (changes['minDateTime']) {
            if (CollectionsUtil.isDefined(this.minDateTime)) {
                this._changeDetectionMinDateTime();

                this._changeDetectionMaxDateTime();
            }
        }

        this._normalizeUrlAfterLoad();
    }

    /**
     * @inheritDoc
     */
    ngOnInit(): void {
        // TODO check if we could not set max time for "TO" period filter and instead current time to be the max allowed
        this._refreshIntervalRef = setInterval(
            // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
            this._changeDetectionMaxDateTime.bind(this),
            15 * 1000
        ); // Update max time every 15s

        // TODO check if would have better performance with mutation observer
        // register callback that would listen for mutation of supported filter and sort criteria
        // this.filtersSortManager.registerMutationObserver((changes) => {
        //     const foundIndex = changes.findIndex(([key, value]) => key === FILTER_TIME_PERIOD_KEY && this._previousSelectedPeriodSerialized !== value);
        //     if (foundIndex !== -1) {
        //         this.selectedPeriodSerialized = changes[foundIndex][1] as string;
        //         this._changeDetectionSelectedPeriodSerialized();
        //     }
        // });
    }

    /**
     * @inheritDoc
     */
    ngOnDestroy(): void {
        if (this._refreshIntervalRef) {
            clearInterval(this._refreshIntervalRef);
        }
    }

    private _adjustDateTime(
        date: number | string | Date | moment.Moment,
        type: 'min' | 'max' | 'from' | 'to',
        travel: 'utc' | 'timezone' = null
    ): moment.Moment {
        const offset = moment().utcOffset();

        let dtInstance = moment(date);

        if (travel) {
            if (offset > 0) {
                dtInstance = travel === 'utc' ? dtInstance.subtract(offset, 'm') : dtInstance.add(offset, 'm');
            } else if (offset < 0) {
                dtInstance = travel === 'utc' ? dtInstance.add(-offset, 'm') : dtInstance.subtract(-offset, 'm');
            }
        }

        if (type === 'min') {
            dtInstance = dtInstance.millisecond(0).subtract(1, 'ms');
        } else if (type === 'max') {
            dtInstance = dtInstance.millisecond(0).add(1, 'ms');
        } else if (type === 'from') {
            dtInstance = dtInstance.millisecond(0);
        } else if (type === 'to') {
            dtInstance = dtInstance.millisecond(999);
        }

        return dtInstance;
    }

    private _updateFiltersSortManager(): void {
        if (CollectionsUtil.isNil(this.fromDateTime) || CollectionsUtil.isNil(this.toDateTime)) {
            this._previousSelectedPeriodSerialized = undefined;
            this.filtersSortManager.deleteFilter(FILTER_TIME_PERIOD_KEY);
        } else {
            const serializedDateTimePeriod = this._serializeDateTimePeriodPairValues();

            this._previousSelectedPeriodSerialized = serializedDateTimePeriod;
            this.filtersSortManager.setFilter(FILTER_TIME_PERIOD_KEY, serializedDateTimePeriod);
        }
    }

    private _changeDetectionSelectedPeriodSerialized(): void {
        if (this._previousSelectedPeriodSerialized === this.selectedPeriodSerialized) {
            return;
        }

        if (!CollectionsUtil.isString(this.selectedPeriodSerialized) || this.selectedPeriodSerialized.length === 0) {
            if (CollectionsUtil.isDefined(this.fromDateTime) || CollectionsUtil.isDefined(this.toDateTime)) {
                this.clearFilter(null);
            }
        } else {
            const deserializedPeriodValues: DateTimePeriod = this._deserializeDateTimePeriodPairValues(this.selectedPeriodSerialized);
            if (deserializedPeriodValues) {
                this.fromDateTime = deserializedPeriodValues.from;
                this.toDateTime = deserializedPeriodValues.to;

                this._updateForm('both');

                this.applyFilter(null);
            }
        }
    }

    private _changeDetectionSelectedPeriod(): void {
        if (CollectionsUtil.isNil(this.selectedPeriod)) {
            return;
        }

        if (this.fromDateTime === this.selectedPeriod.from && this.toDateTime === this.selectedPeriod.to) {
            return;
        }

        if (CollectionsUtil.isNil(this.selectedPeriod.from) || CollectionsUtil.isNil(this.selectedPeriod.to)) {
            if (CollectionsUtil.isDefined(this.fromDateTime) || CollectionsUtil.isDefined(this.toDateTime)) {
                this.clearFilter(null);
            }
        } else {
            const periodFromAdjusted = this._adjustDateTime(this.selectedPeriod.from, null);
            const periodToAdjusted = this._adjustDateTime(this.selectedPeriod.to, null);

            if (!periodFromAdjusted.isBefore(periodToAdjusted)) {
                return;
            }

            if (CollectionsUtil.isDefined(this.fromDateTimeMin) && CollectionsUtil.isDefined(this.toDateTimeMax)) {
                if (periodFromAdjusted.isSameOrAfter(this.fromDateTimeMin) && periodFromAdjusted.isBefore(this.toDateTimeMax)) {
                    this.fromDateTime = new Date(this._adjustDateTime(this.selectedPeriod.from, 'from', 'timezone').valueOf());
                }

                if (periodToAdjusted.isAfter(this.fromDateTimeMin) && periodToAdjusted.isSameOrBefore(this.toDateTimeMax)) {
                    this.toDateTime = new Date(this._adjustDateTime(this.selectedPeriod.to, 'to', 'timezone').valueOf());
                }
            } else {
                this.fromDateTime = new Date(this._adjustDateTime(this.selectedPeriod.from, 'from', 'timezone').valueOf());
                this.toDateTime = new Date(this._adjustDateTime(this.selectedPeriod.to, 'to', 'timezone').valueOf());
            }

            this._updateForm('both');

            this.applyFilter(null);
        }
    }

    private _changeDetectionMinDateTime(): void {
        // set once during initialization or forced when user clear the form
        if (!this._initiallySetMin) {
            this._initiallySetMin = true;

            if (CollectionsUtil.isDate(this.fromDateTime) && CollectionsUtil.isDate(this.minDateTime)) {
                if (this.fromDateTime.getTime() < this.minDateTime.getTime()) {
                    this.fromDateTime = this.minDateTime;
                }
            } else {
                this.fromDateTime = this.minDateTime;
            }

            this.fromDateTimeMin = this._adjustDateTime(this.minDateTime, 'min', 'utc');
            this.fromPickerConfig = {
                ...this.fromPickerConfig,
                min: this.fromDateTimeMin
            };

            this.toDateTimeMin = this._adjustDateTime(this.fromDateTime ?? this.minDateTime, 'min', 'utc');
            this.toPickerConfig = {
                ...this.toPickerConfig,
                min: this.toDateTimeMin
            };

            if (!this._isFromPickerOpened) {
                this._updateForm('fromDateTime');
            }
        }
    }

    private _changeDetectionMaxDateTime() {
        const date = new Date();

        this.toDateTimeMax = this._adjustDateTime(date, 'max', 'utc');
        this.toPickerConfig = {
            ...this.toPickerConfig,
            max: this.toDateTimeMax
        };

        // set once during initialization or forced when user clear the form
        if (!this._initiallySetMax) {
            this._initiallySetMax = true;

            if (CollectionsUtil.isDate(this.toDateTime)) {
                if (this.toDateTime.getTime() > date.getTime()) {
                    this.toDateTime = date;
                }
            } else {
                this.toDateTime = date;
            }

            this.fromDateTimeMax = this._adjustDateTime(this.toDateTime, 'max', 'utc');
            this.fromPickerConfig = {
                ...this.fromPickerConfig,
                max: this.fromDateTimeMax
            };

            if (!this._isToPickerOpened) {
                this._updateForm('toDateTime');
            }
        }
    }

    private _serializeDateTimePeriodPairValues(): string {
        let timePeriodFilter = '';

        if (this.fromDateTime instanceof Date) {
            timePeriodFilter += `${this.fromDateTime.getTime()}`;
        }

        if (this.toDateTime instanceof Date) {
            timePeriodFilter += `-${this.toDateTime.getTime()}`;
        }

        return timePeriodFilter;
    }

    private _deserializeDateTimePeriodPairValues(dateTimePeriodValues: string): DateTimePeriod {
        const fromToDateTimeTuple = dateTimePeriodValues.split('-');

        let fromDateTime: Date;
        let toDateTime: Date;

        if (CollectionsUtil.isStringWithContent(fromToDateTimeTuple[0]) && /\d+/.test(fromToDateTimeTuple[0])) {
            const parsedFromEpochTime = parseInt(fromToDateTimeTuple[0], 10);

            if (CollectionsUtil.isNumber(parsedFromEpochTime) && !CollectionsUtil.isNaN(parsedFromEpochTime)) {
                fromDateTime = new Date(parsedFromEpochTime);

                if (CollectionsUtil.isNaN(fromDateTime.valueOf())) {
                    fromDateTime = null;
                }
            }
        }

        if (CollectionsUtil.isStringWithContent(fromToDateTimeTuple[1]) && /\d+/.test(fromToDateTimeTuple[1])) {
            const parsedToEpochTime = parseInt(fromToDateTimeTuple[1], 10);

            if (CollectionsUtil.isNumber(parsedToEpochTime) && !CollectionsUtil.isNaN(parsedToEpochTime)) {
                toDateTime = new Date(parsedToEpochTime);

                if (CollectionsUtil.isNaN(toDateTime.valueOf())) {
                    toDateTime = null;
                }
            }
        }

        if (CollectionsUtil.isDate(fromDateTime) && CollectionsUtil.isDate(toDateTime)) {
            const fromDateTimeMoment = this._adjustDateTime(fromDateTime, null, 'utc');
            const toDateTimeMoment = this._adjustDateTime(toDateTime, null, 'utc');

            if (fromDateTimeMoment.isSameOrAfter(toDateTimeMoment)) {
                return null;
            }

            if (CollectionsUtil.isDefined(this.fromDateTimeMin) && CollectionsUtil.isDefined(this.fromDateTimeMax)) {
                if (!fromDateTimeMoment.isBetween(this.fromDateTimeMin, this.fromDateTimeMax)) {
                    return null;
                }
            }

            if (CollectionsUtil.isDefined(this.toDateTimeMin) && CollectionsUtil.isDefined(this.toDateTimeMax)) {
                if (!toDateTimeMoment.isBetween(this.toDateTimeMin, this.toDateTimeMax)) {
                    return null;
                }
            }

            return {
                from: fromDateTime,
                to: toDateTime
            };
        }

        return null;
    }

    private _normalizeUrlAfterLoad(): void {
        if (this._isUrlNormalized) {
            return;
        }

        if (!this.filtersSortManager) {
            return;
        }

        if (!this.filtersSortManager.hasFilter(FILTER_TIME_PERIOD_KEY)) {
            return;
        }

        this._isUrlNormalized = true;

        if (this.filtersSortManager.filterCriteria[FILTER_TIME_PERIOD_KEY] === this._serializeDateTimePeriodPairValues()) {
            return;
        }

        this.filtersSortManager.setFilter(FILTER_TIME_PERIOD_KEY, this._serializeDateTimePeriodPairValues());
        this.filtersSortManager.updateBrowserUrl('replaceToURL', true);
    }

    private _updateForm(partial: 'fromDateTime' | 'toDateTime' | 'both'): void {
        if (partial === 'both' || partial === 'fromDateTime') {
            this.tmForm
                .get('fromDateTime')
                .patchValue(this._adjustDateTime(this.fromDateTime, 'from', 'utc').format(this.fromPickerConfig.format));
        }

        if (partial === 'both' || partial === 'toDateTime') {
            this.tmForm.get('toDateTime').patchValue(this._adjustDateTime(this.toDateTime, 'to', 'utc').format(this.toPickerConfig.format));
        }
    }

    private _emitChanges(): void {
        this.filterChanged.emit({
            from: this.fromDateTime,
            to: this.toDateTime
        });
    }
}
