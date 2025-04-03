import { Inject, Injectable, PLATFORM_ID } from '@angular/core';
import { WebSocketSubject, webSocket } from 'rxjs/webSocket';
import { Observable, Subject } from 'rxjs';
import { isPlatformBrowser } from '@angular/common';

@Injectable({
  providedIn: 'root',
})
export class WebsocketService {
  private socket$: WebSocketSubject<any> | null = null;
  private messageAmplitudeSubject = new Subject<Uint8Array>(); // Changed from Float32Array to Uint8Array
  private messageRecvDataSubject = new Subject<Int16Array>(); // Changed from Float32Array to Uint8Array


  constructor(@Inject(PLATFORM_ID) private platformId: Object) {}

  connectAmplitude() {
    if (isPlatformBrowser(this.platformId)) {
      this.socket$ = webSocket({
        url: 'ws://127.0.0.1:8000/amplitude/ws',
        binaryType: 'arraybuffer', // Ensure it handles binary data
        deserializer: (msg) => msg.data as ArrayBuffer, // Get raw ArrayBuffer
      });

      console.log('WebSocket amplitude connected');

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

            this.messageAmplitudeSubject.next(uint8Array);  // Changed to emit Uint8Array
            // console.log('Received Uint8Array:', uint8Array);
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

  getAmplitudeMessages(): Observable<Uint8Array> {  // Changed from Float32Array to Uint8Array
    return this.messageAmplitudeSubject.asObservable();
  }

  closeAmplitudeConnection() {
    this.socket$?.complete();
  }



  connectRecvData() {
    if (isPlatformBrowser(this.platformId)) {
      this.socket$ = webSocket({
        url: 'ws://127.0.0.1:8000/recvData/ws',
        binaryType: 'arraybuffer', // Ensure it handles binary data
        deserializer: (msg) => msg.data as ArrayBuffer, // Get raw ArrayBuffer
      });

      console.log('WebSocket recv data connected');

      this.socket$.subscribe({
        next: (data: ArrayBuffer) => {
          try {
            // Ensure buffer is aligned correctly
            if (data.byteLength % 1 !== 0) {  // Adjusted check for uint8 (each value is 1 byte)
              console.error('Invalid ArrayBuffer size:', data.byteLength);
              return;
            }

            // Use DataView to correctly read the buffer
            const int16Array = new Int16Array(data);  // Directly interpret data as Uint8Array

            this.messageRecvDataSubject.next(int16Array);  // Changed to emit Uint8Array
            // console.log('Received Uint16Array:', int16Array);
          } catch (error) {
            console.error('Error converting ArrayBuffer to Uint16Array:', error);
          }
        },
        error: (err) => console.error('WebSocket error:', err),
        complete: () => console.log('WebSocket connection closed'),
      });
    } else {
      console.warn('WebSocket is not available in this environment.');
    }
  }

  getRecvDataMessages(): Observable<Int16Array> {  // Changed from Float32Array to Uint8Array
    return this.messageRecvDataSubject.asObservable();
  }

  closeRecvDataConnection() {
    this.socket$?.complete();
  }
}
