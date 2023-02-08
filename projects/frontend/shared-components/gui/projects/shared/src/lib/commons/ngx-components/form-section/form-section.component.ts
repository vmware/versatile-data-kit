import { Component, EventEmitter, Input, Output } from "@angular/core";
import { animate, state, style, transition, trigger } from "@angular/animations";


@Component({
    selector: 'vmw-form-section',
    styleUrls: ['form-section.component.scss'],
    templateUrl: 'form-section.component.html',
    animations: [
        trigger('customFormState', [
            state('edit', style({
                opacity: 1,
                width: '3px',
                'margin-right': '24px'
            })),
            state('normal', style({
                opacity: 0,
                width: '0px',
                'margin-right': '0px'

            })),
            transition('normal => edit', [
                animate('300ms ease-in-out')
            ]),
            transition('edit => normal', [
                animate('100ms ease-in-out')
            ])
        ]),
        trigger('footerState', [
            transition(':enter', [
                style({ opacity: 0, height: '0' }),
                animate('0.1s 0.2s ease-in-out', style({ opacity: 1, height: '*'})),
            ]),
            transition(':leave', [
                animate('0.1s', style({ opacity: 0, height: '0' }))
            ])
        ])
    ]
})

export class VmwFormSectionComponent {
    @Input()
    focused: boolean = false;

    @Output()
    animationDone = new EventEmitter<void>();

    getFormState() {
        return this.focused ? 'edit' : 'normal';
    }

    emitAnimationDone() {
        this.animationDone.emit();
    }
}
