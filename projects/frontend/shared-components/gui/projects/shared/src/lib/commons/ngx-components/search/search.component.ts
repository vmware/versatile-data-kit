/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import {
	Component,
	ElementRef,
	EventEmitter,
	Input,
	Output,
	ViewChild
} from '@angular/core';
import { FormControl } from '@angular/forms';

import { BehaviorSubject, combineLatest, Subject, Subscription } from 'rxjs';
import { debounceTime } from 'rxjs/operators';

const defaultSearchInputPadding = 24;

@Component({
	selector: 'vdk-search',
	templateUrl: './search.component.html',
	styleUrls: ['./search.component.scss']
})
export class VdkSearchComponent {
	searchInputPaddingRight = `${defaultSearchInputPadding}px`;

	private _disabled: boolean = false;
	public get disabled(): boolean {
		return this._disabled;
	}
	@Input('disabled')
	public set disabled(value: boolean) {
		this._disabled = value;

		if (value) {
			this.searchQuery?.disable({ emitEvent: false });
		} else {
			this.searchQuery?.enable({ emitEvent: false });
		}
	}

	@Input() searchQueryValue: string = '';
	@Input() clearSearchTitle: string = 'Clear Search';
	@Input('placeholder')
	set placeholder(pass: string) {
		this.finalPlaceholder = pass ? pass : 'Search';
	}

	@Input() helperText: string = '';
	@Input() debounceTime: number = 100;
	@Input() searchTermMinimalLength: number = 2;
	@Input() showSearchButton = false;
	@Input() searchButtonText: string = 'Search';
	@Input() searchButtonAriaLabelText: string = 'Search';
	@Input() searchAriaLabelText: string;

	@Output() search: EventEmitter<string> = new EventEmitter();

	@ViewChild('searchButton', { read: ElementRef })
	searchButton?: ElementRef;
	isSeachButtonVisible: boolean;

	private triggerSearch$: Subject<void> = new BehaviorSubject<void>(undefined);
	private hasSearchBeenTriggeredManually: boolean;

	public searchQuery: FormControl;
	public searchQuerySub: Subscription;
	public focused: boolean = false;
	public finalPlaceholder: string = 'Search';

	ngOnInit() {
		this.searchQuery = new FormControl(this.searchQueryValue);

		this.searchQuerySub = combineLatest([
			this.searchQuery.valueChanges,
			this.triggerSearch$
		])
			.pipe(debounceTime(this.debounceTime))
			.subscribe(([query]) => {
				const queryLength = query.length;
				query = query.trim();
				this.searchQueryValue = query;

				// not emit search event if it hasn't been inputted something different from whitespace
				if (this.searchQueryValue.length === 0 && queryLength !== 0) {
					return;
				}

				// Make sure that the 'Search' button will be visible in 'Manual Search' mode upon every change.
				this.isSeachButtonVisible = this.showSearchButton;

				const shouldNotifyForQueryChange =
					!this.showSearchButton || this.hasSearchBeenTriggeredManually;
				const inputHasMinLengthOrIsCleared =
					this.searchQueryValue.length >= this.searchTermMinimalLength ||
					this.searchQueryValue.length === 0;
				if (shouldNotifyForQueryChange && inputHasMinLengthOrIsCleared) {
					// If we are about to notify that the search term has changed replace 'Search' button with the `X` one.
					this.isSeachButtonVisible = false;
					this.search.emit(query);
				}

				this.hasSearchBeenTriggeredManually = false;
				this.computeSearchInputPadding();
			});
	}

	ngOnDestroy(): void {
		if (this.searchQuerySub) {
			this.searchQuerySub.unsubscribe();
		}
	}

	clearSearch(): void {
		this.searchQuery.setValue('');
		if (this.showSearchButton) {
			this.triggerSearch();
		}
	}

	handleKeyDown(event: KeyboardEvent): void {
		if (event.key === 'Enter') {
			this.triggerSearch();
		}
	}

	triggerSearch(): void {
		this.hasSearchBeenTriggeredManually = true;
		this.triggerSearch$.next();
	}

	private computeSearchInputPadding(): void {
		if (this.showSearchButton && this.isSeachButtonVisible) {
			// Wait for the search button to be rendered as changes 'shouldShowSearchButton' might not be applied in the template.
			// Useful especially after the first rendering.
			setTimeout(() => {
				this.searchInputPaddingRight =
					Math.round(
						this.searchButton?.nativeElement.clientWidth ||
							defaultSearchInputPadding
					) + 'px';
			});
		} else {
			this.searchInputPaddingRight = `${defaultSearchInputPadding}px`;
		}
	}
}
