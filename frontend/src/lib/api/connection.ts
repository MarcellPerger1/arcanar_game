import { promiseWithResolvers } from "$lib/util";

const OurWsCodes = {
  OK: 1000,
  LEAVING: 4101,
  CLIENT_ERROR: 4200,
  SERVER_ERROR: 4300
}

// Abstracted away from WS codes or HTTP codes
export const CloseCode = {
  NORMAL: 0,
  LEAVING: 1,
  CLIENT_ERROR: 2,
  SERVER_ERROR: 3,
} as const;
export type CloseCodeTp = (typeof CloseCode)[keyof (typeof CloseCode)];

const CloseCodeToWsCode = {
  [CloseCode.NORMAL]: OurWsCodes.OK,
  [CloseCode.LEAVING]: OurWsCodes.LEAVING,
  [CloseCode.CLIENT_ERROR]: OurWsCodes.CLIENT_ERROR,
  [CloseCode.SERVER_ERROR]: OurWsCodes.SERVER_ERROR
};
const CloseCodeToText = {
  [CloseCode.NORMAL]: "Normal closue",
  [CloseCode.LEAVING]: "Client is leaving",
  [CloseCode.CLIENT_ERROR]: "Client error",
  [CloseCode.SERVER_ERROR]: "Server error"
}


export interface IConnection {
  connect(): Promise<this>;

  send(s: string): Promise<void>;
  recv(): Promise<string>;
  addOnmessageListener(fn: (msg: string) => void): void;

  close(code: CloseCodeTp, detail?: string): Promise<void>;
}

export class WebsocketConn implements IConnection {  
  url: string;
  _ws?: WebSocket;
  error?: CloseEvent;
  _message_waiters: {resolve(value: string): void; reject(reason?: any): void;}[] = [];
  _message_listeners: ((msg: string) => void)[] = [];

  constructor(url: string) {
    this.url = url;
    this.addOnmessageListener(msg => console.debug('Received: ', msg));
  }

  connect() {
    return new Promise<this>((resolve, reject) => {
      let hasOpened = false;
      this._ws = new WebSocket(this.url);
      this._ws.addEventListener("open", () => {
        hasOpened = true;
        resolve(this);
      });
      // This also handles the errors (those cause it to be closed)
      this._ws.addEventListener("close", (ev) => {
        if(ev.code == OurWsCodes.OK) return;
        this.error = ev;
        if(!hasOpened) {  // if get error while trying to open
          return reject(new Error(`Couldn't open connection: code ${ev.code}: ${ev.reason}`));
        }
        this.rejectWaiters(ev);
      });
      this._ws.addEventListener('message', (ev) => {
        // If there's multiple things waiting for a message, we're stuck 
        // between two bad options:
        // 1. Give them both the result: cauxes inconsitencies due to timing of received
        //    messages (is the 2nd one added before the message is received?)
        // 2. Give the first one the result, let the second one wait: causes
        //    inconsitencies due to possible difference in execution order
        //    (e.g. in Promise.all). This shouldn't happen in our specific 
        //    case as actions are all sequential.
        // We chose option 2 as we can actually control (to some extent) 
        // our execution order. We cannot control the server/network timings.
        this._message_listeners.forEach((fn) => fn(ev.data));
        this._message_waiters.shift()?.resolve?.(ev.data);
      })
    });
  }

  async send(s: string) {
    console.debug('Sending: ', s);
    this.ws.send(s);
  }

  async recv() {
    this.ensureConnected();
    const info = promiseWithResolvers<string>();
    this._message_waiters.push(info);
    return info.promise;
  }

  async close(code: CloseCodeTp, detail?: string): Promise<void> {
    this.ws.close(CloseCodeToWsCode[code], detail ?? CloseCodeToText[code]);
  }

  addOnmessageListener(fn: (msg: string) => void): void {
    this._message_listeners.push(fn);
  }

  get ws() {
    return this.ensureConnected();
  }

  ensureConnected() {
    if(!this._ws) throw new Error("WebsocketConn has not been connected yet");
    if(this._ws.readyState != WebSocket.OPEN) {
      const stateStr = {
        [WebSocket.CONNECTING]: 'CONNECTING',  [WebSocket.OPEN]: 'OPEN', 
        [WebSocket.CLOSING]: 'CLOSING', [WebSocket.CLOSED]: 'CLOSED'
      }[this._ws.readyState];
      throw new Error(`WebscoketConn is not open (state = ${stateStr})`);
    }
    return this._ws;
  }

  private rejectWaiters(reason: any) {
    this._message_waiters.forEach(({reject}) => {reject(reason)});
  }
}
