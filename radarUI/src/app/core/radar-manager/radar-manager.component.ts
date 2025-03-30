import { Component, OnDestroy, OnInit } from '@angular/core';
import { WebsocketService } from '../../shared/services/websocket.service';
import { HttpClient } from '@angular/common/http';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-radar-manager',
  standalone: true,
  imports: [],
  templateUrl: './radar-manager.component.html',
  styleUrl: './radar-manager.component.scss'
})
export class RadarManagerComponent implements OnInit, OnDestroy{
  radarFeed: any = {"rx_amplitude": []};
  radioSpecs: any = { "sample_rate": '' };
  private messageSubscription?: Subscription;

  constructor(private webSocketService: WebsocketService, 
              private http: HttpClient,) {
    webSocketService.connect();
  }

  ngOnInit(): void {
    this.messageSubscription = this.webSocketService.getMessages().subscribe((message) => {
      console.log("Received WebSocket Message:");
      this.radarFeed = message;
      },
      error => { console.warn('failed to get data/ws message', error)}
    );
  
    this.http.get('/api/radioSpecs').subscribe((data: any) => {
      console.log("Received HTTP Data:", data);
      this.radioSpecs = data;
      },
      error => { console.warn('failed to get radioSpecs', error)}
    );
  }

  ngOnDestroy() {
    // this.messageSubscription?.unsubscribe();
    // this.webSocketService.closeConnection();
  }
}
