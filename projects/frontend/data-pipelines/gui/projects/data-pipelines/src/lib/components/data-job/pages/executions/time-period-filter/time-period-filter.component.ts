/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, EventEmitter, Input, OnDestroy, OnInit, Output, ViewChild } from '@angular/core';
import { FormBuilder, FormControl, FormGroup } from '@angular/forms';

import { CalendarValue, DatePickerDirective, IDatePickerDirectiveConfig } from 'ng2-date-picker';

// TODO [import dayjs from 'dayjs'] used in ng2-date-picker v13+ instead of moment
import moment from 'moment';

import { CollectionsUtil } from '@versatiledatakit/shared';

import { FiltersSortManager } from '../../../../../commons';

import { ExecutionsFilterCriteria, FILTER_TIME_PERIOD_KEY } from '../model';

type CustomFormGroup = FormGroup & { controls: { [key: string]: FormControl } };

@Component({
    selector: 'lib-time-period-filter',
    templateUrl: './time-period-filter.component.html',
    styleUrls: ['./time-period-filter.component.scss']
})
export class TimePeriodFilterComponent implements OnInit, OnDestroy {
    @ViewChild('fromPicker') fromPicker: DatePickerDirective;
    @ViewChild('toPicker') toPicker: DatePickerDirective;

    @Input() set loading(value: boolean) {
        this._loading = value;
    }

    get loading() {
        return this._loading;
    }

    /**
     * ** Flag that indicates there is jobs executions load error.
     */
    @Input() isComponentInErrorState = false;

    /**
     * ** Executions filters sort manager injected from parent.
     */
    @Input() filtersSortManager: Readonly<FiltersSortManager<ExecutionsFilterCriteria, string>>;

    /**
     * ** Event Emitter that emits events on every user form action like submit or clear.
     */
    @Output() filterChanged: EventEmitter<{ fromTime: Date; toTime: Date }> = new EventEmitter<{ fromTime: Date; toTime: Date }>();

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
    fromTime: Date;

    /**
     * ** User selected value for "TO" time date picker.
     */
    toTime: Date;

    /**
     * ** Allowed ranges for "FROM" time date picker.
     */
    // "FROM" time min allowed value is used from {@link this.minTime}
    fromTimeMin: moment.Moment;
    // "FROM" time max allowed value is less than {@link this.toTimeMin}
    fromTimeMax: moment.Moment;

    /**
     * ** Allowed ranges for "TO" time date picker.
     */
    // "TO" time min allowed value is less than {@link this.fromTimeMax}
    toTimeMin: moment.Moment;
    // "TO" time max allowed value for selection is current time. There is scheduled interval on 15s that updates this value.
    // TODO check if will work without upper range
    toTimeMax: moment.Moment;

    /**
     * ** Angular form where DatePicker inputs belongs.
     */
    tmForm: CustomFormGroup;

    @Input()
    set timePeriod(timePeriod: string) {
        if (timePeriod === this._timePeriod) {
            return;
        }

        this._timePeriod = timePeriod;

        this._applyTimePeriodFromTo(timePeriod);

        this._normalizeUrlFilterAfterLoad();
    }

    @Input()
    set minTime(date: Date) {
        if (CollectionsUtil.isNil(date)) {
            return;
        }

        // set once during initialization or forced when user clear the form
        if (!this._initiallySetMin) {
            this._initiallySetMin = true;

            this.fromTime = date;
            this._minTimeOrig = date;

            const fromTimeMin = this._normalizeDateTime(date, 'min', 'utc');

            this.fromTimeMin = fromTimeMin;
            this.fromPickerConfig = {
                ...this.fromPickerConfig,
                min: this.fromTimeMin
            };

            this.toTimeMin = fromTimeMin;
            this.toPickerConfig = {
                ...this.toPickerConfig,
                min: this.toTimeMin
            };

            if (!this._isFromPickerOpened) {
                this.tmForm.get('fromDate').patchValue(this._normalizeDateTime(date, 'from', 'utc').format(this.fromPickerConfig.format));
            }
        }

        this._setMaxTime();

        this._normalizeUrlFilterAfterLoad();
    }

    private _loading = false;

    private _minTimeOrig: Date;

    private _isFromPickerOpened = false;
    private _isToPickerOpened = false;

    private _initiallySetMin = false;
    private _initiallySetMax = false;

    // refresh interval scheduled reference
    private _refreshIntervalRef: number;

    private _timePeriod: string;

    private _isUrlNormalizeExecuted = false;

    /**
     * ** Constructor.
     */
    constructor(private readonly formBuilder: FormBuilder) {
        this.tmForm = this.formBuilder.group({
            fromDate: '',
            toDate: ''
        }) as CustomFormGroup;
    }

    onDateTimeChange($event: CalendarValue, type: 'from' | 'to'): void {
        if (CollectionsUtil.isNil($event)) {
            return;
        }

        const emittedDate = $event as moment.Moment;

        if (type === 'from') {
            const origMinTimeUtc = this._normalizeDateTime(this._minTimeOrig, 'from', 'utc');
            if (emittedDate.isBefore(origMinTimeUtc) || emittedDate.isAfter(this.fromTimeMax)) {
                return;
            }

            this.fromTime = new Date(this._normalizeDateTime(emittedDate, 'from', 'timezone').valueOf());

            this.toTimeMin = this._normalizeDateTime(emittedDate, 'min');
            this.toPickerConfig = {
                ...this.toPickerConfig,
                min: this.toTimeMin
            };
        } else {
            if (emittedDate.isBefore(this.toTimeMin) || emittedDate.isAfter(this.toTimeMax)) {
                return;
            }

            this.toTime = new Date(this._normalizeDateTime(emittedDate, 'to', 'timezone').valueOf());

            this.fromTimeMax = this._normalizeDateTime(emittedDate, 'max');
            this.fromPickerConfig = {
                ...this.fromPickerConfig,
                max: this.fromTimeMax
            };
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
     * ** Submit selected values and emit.
     */
    submitForm($event: Event): void {
        $event?.preventDefault();

        this._emitChanges();
    }

    /**
     * ** Clear selected values and emit.
     */
    clearFilter($event: MouseEvent): void {
        $event?.preventDefault();

        this._initiallySetMin = false;
        this._initiallySetMax = false;

        this.fromTime = null;
        this.toTime = null;

        this._emitChanges();

        this.minTime = this._minTimeOrig;
    }

    /**
     * @inheritDoc
     */
    ngOnInit(): void {
        // TODO check if we could not set max time for "TO" period filter and instead current time to be the max allowed
        this._refreshIntervalRef = setInterval(
            // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
            this._setMaxTime.bind(this),
            15 * 1000
        ); // Update max time every 15s
    }

    /**
     * @inheritDoc
     */
    ngOnDestroy(): void {
        if (this._refreshIntervalRef) {
            clearInterval(this._refreshIntervalRef);
        }
    }

    private _setMaxTime() {
        const date = new Date();

        this.toTimeMax = this._normalizeDateTime(date, 'max', 'utc');
        this.toPickerConfig = {
            ...this.toPickerConfig,
            max: this.toTimeMax
        };

        // set once during initialization or forced when user clear the form
        if (!this._initiallySetMax) {
            this._initiallySetMax = true;

            this.toTime = date;

            this.fromTimeMax = this._normalizeDateTime(this.toTime, 'max', 'utc');
            this.fromPickerConfig = {
                ...this.fromPickerConfig,
                max: this.fromTimeMax
            };

            if (!this._isToPickerOpened) {
                this.tmForm.get('toDate').patchValue(this._normalizeDateTime(this.toTime, 'to', 'utc').format(this.toPickerConfig.format));
            }
        }
    }

    private _applyTimePeriodFromTo(timePeriodPairValues: string): void {
        if (!CollectionsUtil.isString(timePeriodPairValues) || timePeriodPairValues.length === 0) {
            if (CollectionsUtil.isDefined(this.fromTime) || CollectionsUtil.isDate(this.toTime)) {
                this.clearFilter(null);
            }

            return;
        }

        this._deserializeTimePeriodPairValues(timePeriodPairValues);

        this.submitForm(null);
    }

    private _normalizeDateTime(
        date: Date | moment.Moment,
        type: 'min' | 'max' | 'from' | 'to',
        travel: 'utc' | 'timezone' = null
    ): moment.Moment {
        const offset = moment().utcOffset();

        let dtInstance = moment(date).millisecond(0);

        if (travel) {
            if (offset > 0) {
                dtInstance = travel === 'utc' ? dtInstance.subtract(offset, 'm') : dtInstance.add(offset, 'm');
            } else if (offset < 0) {
                dtInstance = travel === 'utc' ? dtInstance.add(-offset, 'm') : dtInstance.subtract(-offset, 'm');
            }
        }

        if (type === 'min') {
            dtInstance = dtInstance.subtract(1, 'ms');
        } else if (type === 'max') {
            dtInstance = dtInstance.add(1, 'ms');
        } else if (type === 'to') {
            dtInstance = dtInstance.millisecond(999);
        }

        return dtInstance;
    }

    private _emitChanges(): void {
        if (CollectionsUtil.isNil(this.fromTime) || CollectionsUtil.isNil(this.toTime)) {
            this.filtersSortManager.deleteFilter(FILTER_TIME_PERIOD_KEY);
        } else {
            this.filtersSortManager.setFilter(FILTER_TIME_PERIOD_KEY, this._serializeTimePeriodPairValues());
        }

        this.filterChanged.emit({
            fromTime: this.fromTime,
            toTime: this.toTime
        });
    }

    private _normalizeUrlFilterAfterLoad(): void {
        if (!this.filtersSortManager) {
            return;
        }

        if (!this._isUrlNormalizeExecuted) {
            this._isUrlNormalizeExecuted = true;

            return;
        }

        if (!this.filtersSortManager.hasFilter(FILTER_TIME_PERIOD_KEY)) {
            return;
        }

        if (this.filtersSortManager.filterCriteria[FILTER_TIME_PERIOD_KEY] === this._serializeTimePeriodPairValues()) {
            return;
        }

        this.filtersSortManager.setFilter(FILTER_TIME_PERIOD_KEY, this._serializeTimePeriodPairValues());
        this.filtersSortManager.updateBrowserUrl('replaceToURL', true);
    }

    private _serializeTimePeriodPairValues(): string {
        let timePeriodFilter = '';

        if (this.fromTime instanceof Date) {
            timePeriodFilter += `${this.fromTime.valueOf()}`;
        }

        if (this.toTime instanceof Date) {
            timePeriodFilter += `-${this.toTime.valueOf()}`;
        }

        return timePeriodFilter;
    }

    private _deserializeTimePeriodPairValues(timePeriodPairValues: string): void {
        const fromToTimeTuple = timePeriodPairValues.split('-');

        let fromTime: Date;
        let toTime: Date;

        if (CollectionsUtil.isStringWithContent(fromToTimeTuple[0]) && /\d+/.test(fromToTimeTuple[0])) {
            const parsedFromEpochTime = parseInt(fromToTimeTuple[0], 10);

            if (CollectionsUtil.isNumber(parsedFromEpochTime) && !CollectionsUtil.isNaN(parsedFromEpochTime)) {
                fromTime = new Date(parsedFromEpochTime);

                if (CollectionsUtil.isNaN(fromTime.valueOf())) {
                    fromTime = null;
                }
            }
        }

        if (CollectionsUtil.isStringWithContent(fromToTimeTuple[1]) && /\d+/.test(fromToTimeTuple[1])) {
            const parsedToEpochTime = parseInt(fromToTimeTuple[1], 10);

            if (CollectionsUtil.isNumber(parsedToEpochTime) && !CollectionsUtil.isNaN(parsedToEpochTime)) {
                toTime = new Date(parsedToEpochTime);

                if (CollectionsUtil.isNaN(toTime.valueOf())) {
                    toTime = null;
                }
            }
        }

        if (CollectionsUtil.isDefined(fromTime) && CollectionsUtil.isDefined(toTime)) {
            this.fromTime = fromTime;
            this.tmForm
                .get('fromDate')
                .patchValue(this._normalizeDateTime(this.fromTime, 'from', 'utc').format(this.fromPickerConfig.format));

            this.toTime = toTime;
            this.tmForm.get('toDate').patchValue(this._normalizeDateTime(this.toTime, 'to', 'utc').format(this.toPickerConfig.format));
        }
    }
}
