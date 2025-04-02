import { Component } from "@angular/core";
import { CommonModule } from "@angular/common";
import { ScichartAngularComponent } from "scichart-angular";
import { getChartsInitializationApi } from "./assets/drawExample";
import { appTheme } from "./assets/theme";


@Component({
  selector: 'app-spectra',
  standalone: true,
  imports: [CommonModule, ScichartAngularComponent],
  templateUrl: './spectra.component.html',
  styleUrl: './spectra.component.scss'
})
export class SpectraComponent {
  chartsInitializationAPI = getChartsInitializationApi();
  audioChart: any;
  fftChart: any;
  spectrogramChart: any;
  controlsRef: any;
  appTheme = appTheme;

  async onChartInit(event: any, chartType: "audio" | "fft" | "spectrogram") {
      if (event?.sciChartSurface) {
          switch (chartType) {
              case "audio":
                  this.audioChart = event.sciChartSurface;
                  break;
              case "fft":
                  this.fftChart = event.sciChartSurface;
                  break;
              case "spectrogram":
                  this.spectrogramChart = event.sciChartSurface;
                  break;
          }

          if (this.audioChart && this.fftChart && this.spectrogramChart) {
              this.configureCharts();
          }
      } else {
          console.log("Chart not initialized!");
      }
  }

  private configureCharts() {
      if (this.audioChart && this.fftChart && this.spectrogramChart) {
          this.controlsRef = this.chartsInitializationAPI.onAllChartsInit();
          this.controlsRef.startUpdate();
      }
  }
}
