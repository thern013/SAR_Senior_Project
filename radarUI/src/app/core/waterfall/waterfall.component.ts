import { Component, OnInit, OnDestroy } from '@angular/core';
import { WebsocketService } from '../../shared/services/websocket.service';
import { Subscription } from 'rxjs';
import { CommonModule } from '@angular/common';

@Component({
  standalone: true,
  imports: [CommonModule],
  selector: 'app-waterfall',
  templateUrl: './waterfall.component.html',
  styleUrls: ['./waterfall.component.scss']
})
export class WaterfallComponent implements OnInit, OnDestroy {
  messages: any[] = [];
  private messageSubscription?: Subscription;


  constructor(private webSocketService: WebsocketService) {}


  ngOnInit() {
    // Subscribe to messages from the WebSocket
    this.messageSubscription = this.webSocketService.getMessages().subscribe(
      (message) => {
        this.messages.push(message);
      }
    );
  }

  sendMessage() {
    const message = { type: 'message', data: 'Hello, Server!' };
    this.webSocketService.sendMessage(message);
  }


  ngOnDestroy() {
    // Unsubscribe from WebSocket messages and close the connection
    this.messageSubscription?.unsubscribe();
    this.webSocketService.closeConnection();
  }
}