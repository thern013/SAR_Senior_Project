import { Injectable } from '@angular/core';
import { WebSocketSubject, webSocket } from 'rxjs/webSocket';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class WebsocketService {
  private socket$: WebSocketSubject<any>;

  constructor() {
     this.socket$ = webSocket('ws://127.0.0.1:5000/socket.io');
   }
 
   // Send a message to the server
   sendMessage(message: any) {
     this.socket$.next(message);
   }
 
   // Receive messages from the server
   getMessages(): Observable<any> {
     return this.socket$.asObservable();
   }
 
   // Close the WebSocket connection
   closeConnection() {
     this.socket$.complete();
   }
}
