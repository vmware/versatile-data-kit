/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, EventEmitter, Input, Output } from '@angular/core';
import { DataJobDeployment } from '../../../../../model';

@Component({
	selector: 'lib-data-job-deployment-details-modal',
	templateUrl: './data-job-deployment-details-modal.component.html',
	styleUrls: ['./data-job-deployment-details-modal.component.scss']
})
export class DataJobDeploymentDetailsModalComponent {

	@Output() openModalChange = new EventEmitter<boolean>();
	@Input() dataJobDeployment: DataJobDeployment;

	private openModalValue: boolean;

	@Input()
	set openModal(value) {
		this.openModalValue = value;
		this.openModalChange.emit(this.openModalValue);
	}

	get openModal() {
		return this.openModalValue;
	}
}
