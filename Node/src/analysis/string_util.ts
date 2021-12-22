"use strict";

export class StringUtil{
    CHAR_CODE_TO_BIN_: number[];
    TAB_CODE_: number;
    NEW_LINE_: number;
    COMMA_CODE_: number;
    tabRegExp: RegExp;
    constructor(){
        // 文字列から16進デコードするための表
        this.CHAR_CODE_TO_BIN_ = [];
        this.initHexCodeTable_();

        // split のための定数
        this.TAB_CODE_ = "\t".charCodeAt(0);
        this.NEW_LINE_ = "\n".charCodeAt(0);
        this.COMMA_CODE_ = ",".charCodeAt(0);

        this.tabRegExp = new RegExp(/\t/);
    }

    // 高速な tab で分ける split
    // ただし，str が十分にながい場合（数十KB），素の split の方が速い
    // delimiter は charCodeAt で得られる数字なので注意
    /**
     * @param {string} str
     * @param {number} delimiter
    */
    split_(str: string, delimiter: number){
        let ret = [];
        let index = 0;
        let start = 0;
        let length = str.length;
        for(let i = 0; i < length; i++) {
            if (str.charCodeAt(i) == delimiter) {
                if (i - start > 0) {
                    ret[index] = str.slice(start, i);
                    index++;
                }
                start = i + 1;
            }
        }
        // 末尾に残っている分を取り出す
        if (str.length - start > 0) {
            ret[index] = str.slice(start, str.length);
        }
        return ret;
    }

    /** @param {string} str */
    splitByTab(str: string){
        return this.split_(str, this.TAB_CODE_);
    }

    /** @param {string} str */
    splitByNL(str: string){
        return this.split_(str, this.NEW_LINE_);
    }

    /** @param {string} str */
    splitByComma(str: string){
        return this.split_(str, this.COMMA_CODE_);
    }

    // 高速な16進数文字列のデコード
    // parseInt(str, 16) と等価だが，これはかなり遅い
    parseHex(str: string){
        let ret = 0;
        let length = str.length;
        for (let i = 0; i < length; i++) {
            ret = ret * 16;
            let code = str.charCodeAt(i);
            ret += this.CHAR_CODE_TO_BIN_[code < 256 ? code : 0];
        }
        return ret;
        // return parseInt(str, 16);
    }

    initHexCodeTable_(){
        this.CHAR_CODE_TO_BIN_ = [];
        for (let i = 0 ; i < 256; i++){
            this.CHAR_CODE_TO_BIN_[i] = 0;
        }
        const low = "0123456789abcdef";
        for (let i = 0 ; i < 16; i++) {
            this.CHAR_CODE_TO_BIN_[low.charCodeAt(i)] = i;
        }
        const high = "0123456789ABCDEF";
        for (let i = 0 ; i < 16; i++) {
            this.CHAR_CODE_TO_BIN_[high.charCodeAt(i)] = i;
        }
    }
}

export class StringUtilOrg{
    constructor(){
    }
    splitByTab(str: string){ return str.split("\t") };
    splitByNL(str: string){ return str.split("\n"); }
    parseHex(str: string){  return parseInt(str, 16); }
}

export class ReadLineOrg{
    readLine: any;
    constructor(stream: any){
        let readline = require("readline");
        this.readLine = readline.createInterface({"input": stream});
    }
    close(){
        this.readLine.close();
    }
    on(event: any, handler: any){
        this.readLine.on(event, handler);
    }
}

export class ReadLine{
    stream_: any;
    closeHandler_: any;
    lineHandler_: any;
    lineBuf: string;
    strUtil: StringUtil;
    constructor(stream: any){
        this.stream_ = stream;
        this.closeHandler_ = null;
        this.lineHandler_ = null;

        this.lineBuf = "";
        this.strUtil = new StringUtil;

        stream.on("data", this.onData_.bind(this));
        stream.on("end", this.onEnd_.bind(this));
    }

    onEnd_(){
        this.close();
    }

    onData_(data: any){
        if (!this.lineHandler_) {
            return;
        }

        let str = data.toString();
        if (str.length == 0) {
            return;
        }

        // data が大きいせいか，split の方が速い
        let lines = str.split(/\r?\n/);
        //let lines = this.strUtil.splitByNL(str);

        let numLines = lines.length;
        if (numLines == 1) {
            // 分割数が１であり，改行が全く入ってなかった可能性があるので検査
            if (str.indexOf("\n") == -1) {
                // 改行が元の文字列に入ってなかった
                this.lineBuf += str;
                return;
            }
        }

        // 最初のラインに前回の最後を結合
        // 上のパスで return していない場合，改行が一個は入っていたので
        // line[0] は必ず処理対象となる
        if (numLines > 0) {
            lines[0]  = this.lineBuf + lines[0];
            this.lineBuf = "";
        }

        // 最後のライン以外を処理
        for (let i = 0; i < numLines - 1; i++) {
            this.lineHandler_(lines[i]);
        }

        // 行バッファに最後の行を追加
        if (numLines > 0) {
            let lastLine = lines[numLines - 1];
            if (lastLine.slice(-1) == "\n") {
                this.lineHandler_(lastLine);
            }
            else {
                this.lineBuf = lastLine;
            }
        }
    }

    close(){
        if (this.closeHandler_){
            let closeHandler = this.closeHandler_;
            this.closeHandler_ = null;
            closeHandler();
        }
    }
    /*
    this.readIF_.on("line", read);
    this.readIF_.on("close", finish);
    */
    on(event: any, handler: any){
        if (event == "line") {
            this.lineHandler_ = handler;
        }
        else if (event == "close") {
            this.closeHandler_ = handler;
        }
    }
}
