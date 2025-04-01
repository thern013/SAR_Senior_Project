import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SpectraComponent } from './spectra.component';

describe('SpectraComponent', () => {
  let component: SpectraComponent;
  let fixture: ComponentFixture<SpectraComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SpectraComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SpectraComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
