import type { CloseCodeTp, IConnection } from "./connection.ts";

/** Utility class for wrapping an IConnection without inheriting from it */
export class ConnWrapper implements IConnection {
  protected _wrapped: IConnection;

  constructor(wrapped: IConnection) {
    this._wrapped = wrapped;
  }

  async connect(): Promise<this> {
    return (await this._wrapped.connect(), this);
  }
  async send(s: string): Promise<void> {
    return await this._wrapped.send(s);
  }
  async recv(): Promise<string> {
    return await this._wrapped.recv();
  }
  async close(code: CloseCodeTp, detail?: string): Promise<void> {
    return await this._wrapped.close(code, detail);
  }
  addOnmessageListener(fn: (msg: string) => void): void {
    return this._wrapped.addOnmessageListener(fn);
  }
}

export class DebugConnWrapper extends ConnWrapper implements IConnection {
  constructor(wrapped: IConnection) {
    super(wrapped);
    // TODO: this assumes there's only one in existence...
    window.ARCANAR_send_messages = (messages: string[]) => {
      messages.forEach(msg => this.send(msg));
    }
  }

  // Do we want a cotr argument to disable the debugging?
  async send(msg: string): Promise<void> {
    if(this.shouldDebugSend(this.consoleDebugConf)) console.debug('Sending:', msg);
    if(this.shouldDebugSend(this.debugObjectConf)) {
      (window.ARCANAR_message_log ??= []).push({type: "send", msg});
    }
    return super.send(msg);
  }

  async recv(): Promise<string> {
    const msg = await super.recv();
    if(this.shouldDebugRecv(this.consoleDebugConf)) console.debug('Received:', msg);
    if(this.shouldDebugRecv(this.debugObjectConf)) {
      (window.ARCANAR_message_log ??= []).push({type: "recv", msg});
    }
    return msg;
  }

  private shouldDebugSend(whenConf: DebugWhenT) {
    return ['all', 'response'].includes(whenConf);
  }
  private shouldDebugRecv(whenConf: DebugWhenT) {
    return whenConf == 'all';
  }
  private get consoleDebugConf(): DebugWhenT {
    return window.ARCANAR_DEBUG_CONSOLE ?? 'response';
  }
  private get debugObjectConf(): DebugWhenT {
    return window.ARCANAR_DEBUG_OBJECT ?? 'all';
  }
}

export type DebugWhenT = 'all' | 'response' | 'never';
export type SingleLogMsgT = {type: 'send' | 'recv', msg: string};

declare global {
  interface Window {
    // TODO: perhaps a single arcanar object with sub-objects for each 'layer'
    ARCANAR_DEBUG_CONSOLE?: DebugWhenT;
    ARCANAR_DEBUG_OBJECT?: DebugWhenT;
    ARCANAR_message_log?: SingleLogMsgT[];
    // This 'layer' of our stack doesn't know *anything* about layers above (e.g. that it's JSON)
    ARCANAR_send_messages?(messages: string[]): void;
  }
}
