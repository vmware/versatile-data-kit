/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import {
	ComponentFixture,
	TestBed,
	ComponentFixtureAutoDetect,
	waitForAsync
} from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';

import { ClarityModule } from '@clr/angular';
import { VdkSearchComponent } from './search.component';

let comp: VdkSearchComponent;
let fixture: ComponentFixture<VdkSearchComponent>;
let page: PageObject;
export class PageObject {
	getSearchInputElement(): HTMLInputElement {
		return fixture.nativeElement.querySelector(`[data-test-id="search-input"]`);
	}

	getSearchButtonElement(): HTMLInputElement {
		return fixture.nativeElement.querySelector(
			`[data-test-id="search-button"]`
		);
	}

	getClearSearchBtn(): HTMLButtonElement {
		return fixture.nativeElement.querySelector(
			`[data-test-id="clear-search-btn"]`
		);
	}

	getSearchIcon(): HTMLElement {
		return fixture.nativeElement.querySelector(`[data-test-id="search-icon"]`);
	}

	getHelperText(): HTMLElement {
		return fixture.nativeElement.querySelector(
			'[data-test-id="search-results-text"]'
		);
	}
}

describe('VdkSearchComponent', () => {
	beforeEach(() => {
		TestBed.configureTestingModule({
			imports: [ClarityModule, ReactiveFormsModule],
			declarations: [VdkSearchComponent],
			providers: [{ provide: ComponentFixtureAutoDetect, useValue: true }]
		});
	});

	beforeEach(() => {
		fixture = TestBed.createComponent(VdkSearchComponent);
		comp = fixture.componentInstance;
		fixture.detectChanges();
		page = new PageObject();
	});

	it('should create', () => {
		expect(comp).toBeTruthy();
		expect(page.getSearchInputElement()).toBeTruthy();
		expect(page.getSearchIcon()).toBeTruthy();
		expect(page.getClearSearchBtn()).toBeFalsy();
	});

	it('should show and hide "clear search button"', waitForAsync(() => {
		const searchQuery = 'test';
		expect(page.getClearSearchBtn()).toBeFalsy();
		page.getSearchInputElement().value = searchQuery;
		page.getSearchInputElement().dispatchEvent(new Event('input'));
		fixture.detectChanges();
		fixture
			.whenStable()
			.then(() => {
				expect(comp.searchQuery.value).toBe(
					searchQuery,
					'searchQuery input value is not correct'
				);
				expect(comp.searchQueryValue).toBe(
					searchQuery,
					'searchQueryValue property is not correct'
				);
				expect(page.getClearSearchBtn()).toBeTruthy();
				page.getClearSearchBtn().click();
				fixture.detectChanges();
				return fixture.whenStable();
			})
			.then(() => {
				expect(page.getClearSearchBtn()).toBeFalsy();
			});
	}));

	it('should input show correct data', waitForAsync(() => {
		const searchQuery = 'test';
		page.getSearchInputElement().value = searchQuery;
		page.getSearchInputElement().dispatchEvent(new Event('input'));
		fixture.detectChanges();
		fixture
			.whenStable()
			.then(() => {
				expect(page.getSearchInputElement().value).toBe(searchQuery);
				page.getClearSearchBtn().click();
				fixture.detectChanges();
				return fixture.whenStable();
			})
			.then(() => {
				expect(comp.searchQueryValue).toBe('');
			});
	}));

	it('should emit correct value', waitForAsync(() => {
		const searchQuery = 'test';
		const searchSpy = spyOn(comp.search, 'emit').and.callThrough();
		page.getSearchInputElement().value = searchQuery;
		page.getSearchInputElement().dispatchEvent(new Event('input'));
		fixture.detectChanges();
		fixture.whenStable().then(() => {
			expect(searchSpy).toHaveBeenCalledWith(searchQuery);
		});
	}));

	it('should show helper text with results when resultCount is a number', () => {
		fixture.componentInstance.helperText = `Over 9999 results`;
		fixture.detectChanges();
		expect(page.getHelperText()).not.toBeNull();
	});

	it('should not show helper text with results when resultCount is not used', () => {
		expect(page.getHelperText()).toBeNull();
	});

	describe('when in "Manual Search" mode', () => {
		beforeEach(() => {
			comp.showSearchButton = true;
		});

		it('should show "SEARCH" button disabled when more than one char is entered but it is not above the min limit', waitForAsync(async () => {
			comp.searchTermMinimalLength = 3;

			fixture.detectChanges();

			expect(page.getSearchButtonElement()).toBeNull();

			page.getSearchInputElement().value = 't';
			page.getSearchInputElement().dispatchEvent(new Event('input'));
			fixture.detectChanges();
			await fixture.whenStable();

			let searchButton = page.getSearchButtonElement();
			expect(searchButton).toBeTruthy();
			expect(searchButton.disabled).toBeTruthy();

			page.getSearchInputElement().value = 'two';
			page.getSearchInputElement().dispatchEvent(new Event('input'));
			fixture.detectChanges();
			await fixture.whenStable();

			searchButton = page.getSearchButtonElement();
			expect(searchButton).toBeTruthy();
			expect(searchButton.disabled).toBeFalsy();
		}));

		it('should emit value ONLY upon clicking "Enter" or "SEARCH" and should hide the latter', waitForAsync(async () => {
			const searchQuery = 'test';
			const searchSpy = spyOn(comp.search, 'emit').and.callThrough();
			page.getSearchInputElement().value = searchQuery;
			page.getSearchInputElement().dispatchEvent(new Event('input'));
			fixture.detectChanges();
			await fixture.whenStable();

			expect(page.getClearSearchBtn()).toBeFalsy();
			expect(searchSpy).not.toHaveBeenCalledWith(searchQuery);

			const searchButton = page.getSearchButtonElement();
			searchButton.click();

			await fixture.whenStable();

			expect(searchSpy).toHaveBeenCalledWith(searchQuery);

			expect(page.getClearSearchBtn()).toBeTruthy();

			page
				.getSearchInputElement()
				.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));

			const newSearchQuery = searchQuery + '123';
			page.getSearchInputElement().value = newSearchQuery;
			page.getSearchInputElement().dispatchEvent(new Event('input'));
			fixture.detectChanges();
			await fixture.whenStable();

			expect(searchSpy).toHaveBeenCalledWith(newSearchQuery);
		}));

		it('should clear input upon clicking "X" button', waitForAsync(async () => {
			const searchQuery = 'test';
			const searchSpy = spyOn(comp.search, 'emit').and.callThrough();

			page.getSearchInputElement().value = searchQuery;
			page.getSearchInputElement().dispatchEvent(new Event('input'));
			fixture.detectChanges();
			await fixture.whenStable();

			expect(searchSpy).not.toHaveBeenCalledWith(searchQuery);

			let searchButton = page.getSearchButtonElement();
			searchButton.click();
			await fixture.whenStable();

			expect(searchSpy).toHaveBeenCalledWith(searchQuery);

			searchButton = page.getSearchButtonElement();
			expect(searchButton).toBeNull();

			const clearSearchButton = page.getClearSearchBtn();
			expect(clearSearchButton).toBeTruthy();

			clearSearchButton.click();
			fixture.detectChanges();
			await fixture.whenStable();

			expect(comp.searchQueryValue).toEqual('');
			expect(searchSpy).toHaveBeenCalledWith('');
		}));
	});
});
