import type { ClientRespRawT, ClientRespT, ServerMsgT, ServerReqStrings, ServerReqT, StateT } from "$lib/types";
import { initUiState, type UIStateT } from "$lib/ui_state.ts";
import { Cancelled, guardCancellation, promiseWithResolvers, type PromiseAndResolvers } from "$lib/util";
import { CloseCode, type CloseCodeTp, type IConnection } from "./connection";

export * from "./connection";

const API_VERSION = 1;

export declare type CurrRequestT<Name extends string = string> = {
  resolve(value: ClientRespT): void;  /* TODO: could be more sophisticated here i.e. map resolve type to request type */
  reject(reason?: any): void;
  msg: ServerReqT & {request: Name};  // OMG, this actually does what I want it to, CurrRequestT<"card_payment"> works
  uiState: UIStateT<Name>;
};
export declare type EarlyMainStoreT = {state?: StateT; currRequest?: CurrRequestT};
export declare type MainStoreT = {state: StateT; currRequest?: CurrRequestT};

export function checkRequestType<R extends ServerReqStrings>(req: CurrRequestT | undefined, tp: R): req is CurrRequestT<R> {
  return req != null && req.msg.request === tp;
} 
export function expectRequestType<R extends ServerReqStrings>(req: CurrRequestT | undefined, tp: R): CurrRequestT<R> | never {
  if(!checkRequestType(req, tp)) throw new Error(`Unexpected request type (wanted ${tp}, got ${req?.msg.request})`);
  return req;
}

export class ApiController extends EventTarget {
  conn: IConnection;
  // Framework-agnostic forward API: an object on which we set the state.
  // Vue/Svelte use proxy so it can be used as-is. I don't know about other
  // frameworks, but code can always write its own setters/getters
  dest: EarlyMainStoreT;

  server_version: string = '?';
  
  constructor(conn: IConnection, dest: EarlyMainStoreT) {
    super();
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
    this.conn.addOnmessageListener((msg) => this.handleMessageRaw(msg));
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
    const {promise, resolve} = promiseWithResolvers<void>();
    this.addEventListener('close', () => resolve());
    await promise;
  }

  handleMessageRaw(msg: string) {
    return this.handleMessage(this.parseMessage(msg));
  }
  handleMessage(msg: ServerMsgT) {
    this.dispatchEvent(new Event('recv'));
    if(msg.request == "init") {
      throw new Error("Receaived request:init multiple times.");
    } else if (msg.request == "shutdown") {
      this.setCurrRequest(null);
      this.close(CloseCode.NORMAL);
    } else if (msg.request == "state" || /*winners is included in state, nothing special*/msg.request == "result") {
      this.setState(msg.state);
      this.setCurrRequest(null);
    } else {
      this.handleTrueRequest(msg);  // Just start it off so we can cancel if new request comes in
    }
  }

  async handleTrueRequest(msg: ServerReqT) {
    this.setState(msg.state);
    const resp = await this.getUiResponse(msg);
    if(!resp) return;  // Received new request, cancel this one
    await this.send({...resp, thread: msg.thread});
  }

  async getUiResponse(msg: ServerReqT): Promise<ClientRespT | undefined> {
    const {promise: getUserResponse, reject} = this.createCurrRequest(msg);
    this.addEventListener('recv', () => reject(Cancelled), {once: true});
    return await guardCancellation(getUserResponse, /*fallback*/void 0);
  }

  createCurrRequest(msg: ServerReqT): PromiseAndResolvers<ClientRespT> {
    const {promise, resolve, reject} = promiseWithResolvers<ClientRespT>();
    this.setCurrRequest({resolve, reject, msg, uiState: initUiState(msg.request)});
    return {promise, resolve, reject};
  }

  setState(state: StateT) {
    this.dest.state = state;
  }
  setCurrRequest(currRequest: CurrRequestT | null | undefined) {
    this.dest.currRequest = currRequest ?? void 0;
  }

  async recv(): Promise<ServerMsgT> {
    return this.parseMessage(await this.conn.recv());
  }
  async send(data: ClientRespRawT) {
    await this.conn.send(this.formatMessage(data));
  }
  close(reason: CloseCodeTp) {
    this.conn.close(reason);
    this.dispatchEvent(new Event('close'));
  }

  parseMessage(msg: string): ServerMsgT {
    return JSON.parse(msg);
  }
  formatMessage(msg: ClientRespRawT): string {
    return JSON.stringify(msg);
  }
}
