import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { WaterfallComponent } from "./core/waterfall/waterfall.component";
import { RadarManagerComponent } from "./core/radar-manager/radar-manager.component";
import { ControlsComponent } from "./core/controls/controls.component";

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, WaterfallComponent, RadarManagerComponent, ControlsComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'radarUI';
}
