import { ComponentFixture, TestBed, waitForAsync } from "@angular/core/testing";
import { Component, ViewChild } from "@angular/core";

import { ClarityModule } from "@clr/angular";

import { VmwFormSectionComponent } from "./form-section.component";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";

@Component({
    template: `
        <vmw-form-section [focused]="focused">
            <span class="form-section-header">Test header</span>
            <span class="form-section-content">Test content</span>
            <span class="form-section-footer">Test footer</span>
        </vmw-form-section>
        `
})
class TestHostComponent {
    @ViewChild(VmwFormSectionComponent, { static: true }) child: VmwFormSectionComponent;
    focused: boolean = false;
}

describe("VmwFormSectionComponent", () => {

    let fixture: ComponentFixture<TestHostComponent>;
    let comp: VmwFormSectionComponent;
    let el: any;

    function createComponent() {
        fixture = TestBed.createComponent(TestHostComponent);
        comp = fixture.componentInstance.child;
        el = fixture.debugElement.nativeElement;
        fixture.detectChanges();
    }

    beforeEach(waitForAsync(() => {
        TestBed.configureTestingModule({
            imports: [
                BrowserAnimationsModule,
                ClarityModule,
            ],
            providers: [],
            declarations: [
                TestHostComponent,
                VmwFormSectionComponent
            ]
        });

        createComponent();
        fixture.detectChanges();
    }));

    it("should project .form-section-header content correctly", () => {
        const headers: NodeListOf<Element> = el.querySelectorAll("vmw-form-section span.form-section-header");
        expect(headers.length).toBe(1);
    });

    it("should project .form-section-content content correctly", () => {
        const content: NodeListOf<Element> = el.querySelectorAll("vmw-form-section span.form-section-content");
        expect(content.length).toBe(1);
    });

    it("should project .form-section-footer content only when focused and then change edit state", () => {
        expect(comp.getFormState()).toBe("normal");
        const footer: NodeListOf<Element> = el.querySelectorAll("vmw-form-section span.form-section-footer");
        expect(footer.length).toBe(0);
        fixture.componentInstance.focused = true;
        fixture.detectChanges();
        expect(comp.getFormState()).toBe("edit");
        const footers: NodeListOf<Element> = el.querySelectorAll("vmw-form-section span.form-section-footer");
        expect(footers.length).toBe(1);
    });
});
