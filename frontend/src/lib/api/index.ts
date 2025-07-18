const Code = {
  OK: 1000,
  GOING_AWAY: 1001,
  PROTOCOL_ERROR: 1002,
  UNSUPPORTED_DATA: 1003,
  NO_STATUS_RECEIVED: 1005,
  ABNORMAL_CLOSURE: 1006,
  INVALID_DATA: 1007,
  POLICY_VIOLATION: 1008,
  MESSAGE_TOO_BIG: 1009,
  MANDATORY_EXTENSION: 1010,
  INTERNAL_ERROR: 1011,
  SERVICE_RESTART: 1012,
  TRY_AGAIN_LATER: 1013,
  BAD_GATEWAY: 1014,
  HANDSHAKE_FAILED: 1015,
};

interface IConnection {
  connect(): Promise<this>;
  send(s: string): Promise<void>;
  recv(): Promise<string>;
  addOnmessageListener(fn: (msg: string) => void): void;
}

export class WebsocketConn implements IConnection {  
  url: string;
  _ws?: WebSocket;
  error?: CloseEvent;
  _message_waiters: {resolve(value: string): void; reject(reason?: any): void;}[] = [];
  _message_listeners: ((msg: string) => void)[] = [];

  constructor(url: string) {
    this.url = url;
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
        if(ev.code == Code.OK) return;
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
    this.ws.send(s);
  }

  async recv() {
    this.ensureConnected();
    /*average js keyword spam*/return await new Promise<string>((resolve, reject) => {
      this._message_waiters.push({resolve, reject});
    });
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
