import { Inject, Injectable, PLATFORM_ID } from '@angular/core';
import { WebSocketSubject, webSocket } from 'rxjs/webSocket';
import { Observable, Subject } from 'rxjs';
import { isPlatformBrowser } from '@angular/common';

@Injectable({
  providedIn: 'root',
})
export class WebsocketService {
  private socket$: WebSocketSubject<any> | null = null;
  private messageSubject = new Subject<Uint8Array>(); // Changed from Float32Array to Uint8Array

  constructor(@Inject(PLATFORM_ID) private platformId: Object) {}

  connect() {
    if (isPlatformBrowser(this.platformId)) {
      this.socket$ = webSocket({
        url: 'ws://127.0.0.1:8000/amplitude/ws',
        binaryType: 'arraybuffer', // Ensure it handles binary data
        deserializer: (msg) => msg.data as ArrayBuffer, // Get raw ArrayBuffer
      });

      console.log('WebSocket connected');

      this.socket$.subscribe({
        next: (data: ArrayBuffer) => {
          try {
            // Ensure buffer is aligned correctly
            if (data.byteLength % 1 !== 0) {  // Adjusted check for uint8 (each value is 1 byte)
              console.error('Invalid ArrayBuffer size:', data.byteLength);
              return;
            }

            // Use DataView to correctly read the buffer
            const uint8Array = new Uint8Array(data);  // Directly interpret data as Uint8Array

            this.messageSubject.next(uint8Array);  // Changed to emit Uint8Array
            console.log('Received Uint8Array:', uint8Array);
          } catch (error) {
            console.error('Error converting ArrayBuffer to Uint8Array:', error);
          }
        },
        error: (err) => console.error('WebSocket error:', err),
        complete: () => console.log('WebSocket connection closed'),
      });
    } else {
      console.warn('WebSocket is not available in this environment.');
    }
  }

  getMessages(): Observable<Uint8Array> {  // Changed from Float32Array to Uint8Array
    return this.messageSubject.asObservable();
  }

  closeConnection() {
    this.socket$?.complete();
  }
}
