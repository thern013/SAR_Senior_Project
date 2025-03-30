import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, Subject, Subscription } from 'rxjs';
import { WebsocketService } from './websocket.service';
import { FloatType } from 'three';

@Injectable({
  providedIn: 'root'
})
export class RadarFeedService {
  radarFeed: any = {"rx_amplitude": []};
  radioSpecs: any = { "sample_rate": '' };
  private messageSubscription?: Subscription;

  constructor(private webSocketService: WebsocketService, 
              private http: HttpClient) { }
  
  initializeService() {
  }

  private sampleRateSubject = new BehaviorSubject<any>(0)
  getSampleRate(): Observable<any> {
    fetch('http://127.0.0.1:8000/sampleRate')
      .then((response) => response.json())  // Parse the JSON response
      .then((data) => {
        const sample_rate = data.sample_rate;  // Access the 'sample_rate' field from the JSON response
        console.log("Received HTTP Data:", sample_rate);
        this.sampleRateSubject.next(sample_rate);  // Emit the sample rate value
      })
      .catch((error) => { 
        console.warn('Failed to get radioSpecs', error);
        this.sampleRateSubject.next(0);  // Emit a default value on error
      });
  
    return this.sampleRateSubject.asObservable();
  }
}
