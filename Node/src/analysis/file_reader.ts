"use strict";
import path from "path";
import fs from "fs";
import readline from "readline";
import zlib from "zlib";
import { ReadLine } from "./string_util";
import child_process from "child_process";

export class FileReader{
    filePath_: string;
    readStream_: any;
    readIF_: any;
    fileSize_: number;
    complete_: boolean;
    constructor(){
        this.filePath_ = "";

        /** @type {fs.ReadStream} */
        this.readStream_ = null;

        /** @type {readline.Interface|ReadLine} */
        this.readIF_ = null;

        this.fileSize_ = 0;
        this.complete_ = false;
    }


    /**
     * Open a file
     * @param {string} filePath - a file path
     */
    open(filePath: string){

        let stat = fs.statSync(filePath);
        if (!stat) {
            throw "Failed to fs.statSync(). There seems to be no file.";
        }
        else{
            this.fileSize_ = stat.size;
        }

        this.filePath_ = filePath;

        // GZip の chunk size と合わせて，少し増やすと２割ぐらい速くなる
        let rs = fs.createReadStream(filePath, {highWaterMark: 1024*128});
        this.readStream_ = rs;  // 読み出し量はファイルサイズ基準なので，こっちをセット

        if (this.getExtension() == ".gz") {
            let gzipRS = rs.pipe(zlib.createGunzip({chunkSize: 1024*128}));
            //this.readIF_ = readline.createInterface({"input": gzipRS});
            this.readIF_ = new ReadLine(gzipRS);
        }
        else if (this.getExtension() == ".xz") {
            let xzExec = "xz";
            if (process.platform == "win32") {
                xzExec =  __dirname + "/sysdeps/windows/xz.exe";
            }

            // readStream で読んだデータをパイプで xz に渡す
            // こうしないと，読み出し量がわからずプログレスバーが更新できない
            // オーバーヘッドは多少ある（10%程度）

            // -c: output to stdout, -d: decompress
            // "stdio": options for stdin, stdout, stderr in a child process
            let child = child_process.spawn(xzExec, ["-c", "-d"], {stdio: ["pipe", "pipe", "inherit"]});

            rs.pipe(child.stdin);   // connect the output of readStream
            //this.readIF_ = readline.createInterface({"input": child.stdout});
            this.readIF_ = new ReadLine(child.stdout);
        }
        else {
            //this.readIF_ = readline.createInterface({"input": rs});
            this.readIF_ = new ReadLine(rs);
        }
    }

    close(){
        if (this.readIF_){
            this.readIF_.close();
            this.readIF_ = null;
        }
        if (this.readStream_) {
            this.readStream_.destroy();
            this.readStream_ = null;
        }
    }

    getPath(){
        return this.filePath_;
    }

    /**
     * Open a file
     * @param {function(string): void} read - Called when a line is read
     * @param {function(string): void} finish - Called when all lines have been read
     */
    readlines(read: any, finish: any){
        this.readIF_.on("line", read);
        this.readIF_.on("close", finish);
    }

    get fileSize(){
        return this.fileSize_;
    }

    get bytesRead(){
        return this.readStream_ ? this.readStream_.bytesRead : 0;
    }

    getExtension(){
        let ext = path.extname(this.filePath_);
        return ext;
    }
}
