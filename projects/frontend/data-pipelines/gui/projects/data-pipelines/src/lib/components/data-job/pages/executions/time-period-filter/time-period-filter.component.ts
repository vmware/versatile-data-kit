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

    fromTime: Date;
    toTime: Date;

    fromTimeMin: moment.Moment;
    fromTimeMax: moment.Moment;
    toTimeMin: moment.Moment;
    toTimeMax: moment.Moment;

    tmForm: CustomFormGroup;

    @Input()
    set minTime(date: Date) {
        if (CollectionsUtil.isNil(date)) {
            return;
        }

        if (!this._initiallySetMin) {
            this._initiallySetMin = true;

            this.fromTime = date;
            this._minTimeOrig = date;

            const minDateTime = this._normalizeDateTime(date, 'min', 'utc');

            this.fromTimeMin = minDateTime;
            this.fromPickerConfig = {
                ...this.fromPickerConfig,
                min: this.fromTimeMin
            };

            this.toTimeMin = minDateTime;
            this.toPickerConfig = {
                ...this.toPickerConfig,
                min: this.toTimeMin
            };

            if (!this._isFromPickerOpened) {
                this.tmForm.get('fromDate').patchValue(this._normalizeDateTime(date, 'from', 'utc').format(this.fromPickerConfig.format));
            }
        }

        this._refreshMaxTime();
    }

    private _loading = false;

    private _minTimeOrig: Date;

    private _isFromPickerOpened = false;
    private _isToPickerOpened = false;
    private _initiallySetMin = false;
    private _initiallySetMax = false;
    private _refreshIntervalRef: number;

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

    submitForm($event: Event): void {
        $event.preventDefault();

        this._emitChanges();
    }

    clearFilter($event: MouseEvent): void {
        $event.preventDefault();

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
        this._refreshIntervalRef = setInterval(
            // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
            this._refreshMaxTime.bind(this),
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

    private _refreshMaxTime() {
        const date = new Date();

        this.toTimeMax = this._normalizeDateTime(date, 'max', 'utc');
        this.toPickerConfig = {
            ...this.toPickerConfig,
            max: this.toTimeMax
        };

        if (!this._initiallySetMax) {
            this._initiallySetMax = true;

            this.toTime = date;

            this.fromTimeMax = this._normalizeDateTime(date, 'max', 'utc');
            this.fromPickerConfig = {
                ...this.fromPickerConfig,
                max: this.fromTimeMax
            };

            if (!this._isToPickerOpened) {
                this.tmForm.get('toDate').patchValue(this._normalizeDateTime(date, 'to', 'utc').format(this.toPickerConfig.format));
            }
        }
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
        this.filterChanged.emit({
            fromTime: this.fromTime,
            toTime: this.toTime
        });
    }
}
