/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';

import { Subject } from 'rxjs';

import { Toast } from '../model';

@Injectable()
export class ToastService {
    notificationsSubject = new Subject<Toast>();
    private notification$ = this.notificationsSubject.asObservable();

    /**
     * ** Get subscribable stream, that raise new Events when new Toast should be shown.
     */
    getNotifications() {
        return this.notification$;
    }

    /**
     * ** Show Toast message.
     */
    show(toast: Toast) {
        this.notificationsSubject.next(toast);
    }
}
