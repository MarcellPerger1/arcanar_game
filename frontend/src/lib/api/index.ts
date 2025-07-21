import type { ServerMsgT, ServerReqT, StateT } from "$lib/types";
import { promiseWithResolvers } from "$lib/util";
import { CloseCode, type IConnection } from "./connection";

export * from "./connection";

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
        this.conn.close(CloseCode.NORMAL);
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
