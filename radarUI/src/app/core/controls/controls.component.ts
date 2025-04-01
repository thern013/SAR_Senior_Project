import {Component, OnInit} from '@angular/core';
import {MatInputModule} from '@angular/material/input';
import {MatFormFieldModule} from '@angular/material/form-field';
import {FormsModule} from '@angular/forms';
import {MatSliderModule} from '@angular/material/slider';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import {MatIconModule} from '@angular/material/icon';
import {MatDividerModule} from '@angular/material/divider';
import {MatButtonModule} from '@angular/material/button';
import {MatCardModule} from '@angular/material/card';


interface RadarConfig {
  carrier_frequency: number;
  bandwidth: number;
  sample_rate: number;
  rx_gain: number;
  tx_gain: number;
}

export const initConfig: RadarConfig = {
  carrier_frequency: 0,
  bandwidth: 0,
  sample_rate: 0,
  rx_gain: 0,
  tx_gain: 0
}

@Component({
  selector: 'app-controls',
  standalone: true,
  imports: [FormsModule, MatFormFieldModule, MatInputModule, MatSliderModule,
            MatButtonModule, MatDividerModule, MatIconModule, MatCardModule
  ],
  templateUrl: './controls.component.html',
  styleUrl: './controls.component.scss'
})
export class ControlsComponent implements OnInit{
  serverUrl = 'http://127.0.0.1:8000/radarConfig'
  config = initConfig;

  constructor(private http: HttpClient) {
  }

  ngOnInit(): void {
      this.getConfig()
  }

  getConfig() {
    this.http.get<any>(this.serverUrl).subscribe(
      config => {
        console.log('configuration:', config)
        this.config = config;
      },
      error => {
        console.error('failed to fetch configurations')
      });
  }

  saveSettings() {
    const headers = new HttpHeaders().set('Content-Type', 'application/json');

    // Ensure you're sending the object as JSON
    this.http.patch(this.serverUrl, this.config, { headers }).subscribe(
        config => {
            console.log('Configuration updated:', config);
        },
        error => {
            console.error('Failed to update configuration:', error);
        }
    );
}

}
