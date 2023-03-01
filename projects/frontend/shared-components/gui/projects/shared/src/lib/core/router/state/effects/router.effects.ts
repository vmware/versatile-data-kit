/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import { Location } from '@angular/common';
import { Router } from '@angular/router';

import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

import { Actions, createEffect, ofType } from '@ngrx/effects';

import {
	GoPayload,
	LOCATION_BACK,
	LOCATION_FORWARD,
	LOCATION_GO,
	NavigatePayload,
	ROUTER_NAVIGATE,
	RouterNavigate
} from '../actions';

/**
 * ** Router Effects Service.
 *
 *
 */
@Injectable()
export class RouterEffects {
	/**
	 * ** Effect for Router navigation.
	 */
	routerNavigate$ = createEffect(
		() =>
			this.actions$.pipe(
				ofType(ROUTER_NAVIGATE),
				map((action: RouterNavigate) => action.payload),
				tap((payload) => this._navigate(payload)),
				catchError((error: unknown) => RouterEffects._handleError(error))
			),
		{ dispatch: false }
	);

	/**
	 * ** Effect for Location go (navigate).
	 */
	locationGo$ = createEffect(
		() =>
			this.actions$.pipe(
				ofType(LOCATION_GO),
				tap((payload: GoPayload) =>
					this.location.go(payload.path, payload.query, payload.state)
				),
				catchError((error: unknown) => RouterEffects._handleError(error))
			),
		{ dispatch: false }
	);

	/**
	 * ** Effect for pop Backward Browser state.
	 */
	locationBack$ = createEffect(
		() =>
			this.actions$.pipe(
				ofType(LOCATION_BACK),
				tap(() => this.location.back()),
				catchError((error: unknown) => RouterEffects._handleError(error))
			),
		{ dispatch: false }
	);

	/**
	 * ** Effect for push Forward Browser state.
	 */
	locationForward$ = createEffect(
		() =>
			this.actions$.pipe(
				ofType(LOCATION_FORWARD),
				tap(() => this.location.forward()),
				catchError((error: unknown) => RouterEffects._handleError(error))
			),
		{ dispatch: false }
	);

	/**
	 * ** Constructor.
	 */
	constructor(
		private readonly actions$: Actions,
		private readonly router: Router,
		private readonly location: Location
	) {}

	private static _handleError(error: unknown): Observable<boolean> {
		console.error(error);

		return of(true);
	}

	private _navigate(payload: NavigatePayload): void {
		const extras = payload.extras ?? {};

		// eslint-disable-next-line @typescript-eslint/no-floating-promises
		this.router.navigate(payload.commands, extras).then(() => {
			// No-op.
		});
	}
}
