import type { ServerMsgT, ServerReqT, StateT } from "$lib/types";
import { promiseWithResolvers } from "$lib/util";

const OurWsCodes = {
  OK: 1000,
  LEAVING: 4101,
  CLIENT_ERROR: 4200,
  SERVER_ERROR: 4300
}

// Abstracted away from WS codes or HTTP codes
export const CloseReason = {
  NORMAL: 0,
  LEAVING: 1,
  CLIENT_ERROR: 2,
  SERVER_ERROR: 3,
} as const;
type CloseReasonTp = (typeof CloseReason)[keyof (typeof CloseReason)];

const GenCodeToWsCode = {
  [CloseReason.NORMAL]: OurWsCodes.OK,
  [CloseReason.LEAVING]: OurWsCodes.LEAVING,
  [CloseReason.CLIENT_ERROR]: OurWsCodes.CLIENT_ERROR,
  [CloseReason.SERVER_ERROR]: OurWsCodes.SERVER_ERROR
};
const GenCodeToDefaultReason = {
  [CloseReason.NORMAL]: "Normal closue",
  [CloseReason.LEAVING]: "Client is leaving",
  [CloseReason.CLIENT_ERROR]: "Client error",
  [CloseReason.SERVER_ERROR]: "Server error"
}

interface IConnection {
  connect(): Promise<this>;

  send(s: string): Promise<void>;
  recv(): Promise<string>;
  addOnmessageListener(fn: (msg: string) => void): void;

  close(code: CloseReasonTp, detail?: string): Promise<void>;
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
    this.ws.send(s);
  }

  async recv() {
    this.ensureConnected();
    const info = promiseWithResolvers<string>();
    this._message_waiters.push(info);
    return info.promise;
  }

  async close(code: CloseReasonTp, detail?: string): Promise<void> {
    this.ws.close(GenCodeToWsCode[code], detail ?? GenCodeToDefaultReason[code]);
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


const API_VERSION = 1;

declare type _CurrRequestT<Name extends string = string> = {
  resolve(value: any): void;  /* TODO: could be more sophisticated here i.e. map resolve type to request type */
  reject(reason?: any): void;
  msg: ServerReqT & {request: Name};
};
export declare type MainStoreT = {state?: StateT; currRequest?: _CurrRequestT};
export declare type LoadedMainStoreT = {state: StateT; currRequest?: _CurrRequestT};

export class ApiController {
  conn: IConnection;
  // Framework-agnostic forward API: an object on which we set the state.
  // Vue/Svelte use proxy so it can be used as-is. I don't know about other
  // frameworks, but code can always write its own setters/getters
  dest: MainStoreT;

  server_version: string = '?';
  
  constructor(conn: IConnection, dest: MainStoreT) {
    this.conn = conn;
    this.dest = dest;
  }
  
  private _did_init: boolean = false;
  async init() {
    if(this._did_init) return;
    // Even if called multiple times while request is sending, still only do it once
    this._did_init = true;
    await this.conn.connect();
    await this.handleInitMsg();
  }

  private async handleInitMsg() {
    const msg = await this.recv();
    if (msg.request != 'init') {
      throw new Error("First message server sends must always be request:init");
    }
    const {server_version, api_version: server_api_ver} = msg;
    if(server_api_ver != API_VERSION) {
      throw new Error(`Server and client api versions don't match (server: ${server_api_ver}, client: ${API_VERSION})`)
    }
    this.server_version = server_version;
  }

  async run() {
    await this.init();
    while(true) {
      const msg = await this.recv();
      if(msg.request == "init") {
        throw new Error("Receaived request:init multiple times.");
      } else if (msg.request == "shutdown") {
        this.conn.close(CloseReason.NORMAL);
        break;
      } else if(msg.request == "state") {
        this.setState(msg.state);
      } else if (msg.request == "result") {
        this.setState(msg.state);  // winners is included in state, so nothing extra to do
      } else {  // only the true requests (the ones where we have to reply, ie. with `thread`)
        await this.handleTrueRequest(msg);
      }
    }
  }

  async handleTrueRequest(msg: ServerReqT) {
    this.setState(msg.state);
    const {promise: getRespFromUser, resolve, reject} = promiseWithResolvers<any>();
    this.setCurrRequest({resolve, reject, msg});
    // Wait for the UI will handle it, then send result. "Ionos [the UI] will sort this."
    await this.send({...await getRespFromUser, thread: msg.thread});  // TODO: make the UI actualy handle this
  }

  setState(state: StateT) {
    this.dest.state = state;
  }
  setCurrRequest(currRequest: _CurrRequestT) {
    this.dest.currRequest = currRequest;
  }
  async recv(): Promise<ServerMsgT> {
    return JSON.parse(await this.conn.recv());
  }
  async send(data: any) {
    await this.conn.send(JSON.stringify(data));
  }
}
