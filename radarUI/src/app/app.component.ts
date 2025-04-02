import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { WaterfallComponent } from "./core/waterfall/waterfall.component";
import { ControlsComponent } from "./core/controls/controls.component";
import {MatGridListModule} from '@angular/material/grid-list';
import { SpectraComponent } from "./core/spectra/spectra.component";

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, WaterfallComponent, ControlsComponent, MatGridListModule, SpectraComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'radarUI';
}
