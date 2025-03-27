import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { WaterfallComponent } from "./core/waterfall/waterfall.component";

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, WaterfallComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'radarUI';
}
