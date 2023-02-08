import { Component, Input } from '@angular/core';

@Component({
    selector: 'vmw-empty-state-placeholder',
    templateUrl: './empty-state-placeholder.component.html',
    styleUrls: ["./empty-state-placeholder.component.scss"]
})
export class VmwEmptyStatePlaceholderComponent {
    @Input('title') title: string;
    @Input() icon: string;
    @Input() description: string;
    @Input() headingLevel = 2;
}
