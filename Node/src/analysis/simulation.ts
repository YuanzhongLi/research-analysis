import { FileReader } from "./file_reader";
import { Memory } from "./memory";
import { CacheLRU } from "./cache";
import { Op } from "./op";
import {
  HexStr2BigInt,
  HexStr2Int,
  parcent,
} from "./util";
import {
  validCompressType,
  NORMAL,
  ALIGNMENT,
} from "./constants";

import {
  debugHexUint8Array,
} from "./debug";

let benchmark = process.argv[2];
let compressType: number = Number(process.argv[3]);
let allocation: number = Number(process.argv[4]);

if (!validCompressType(compressType)) {
  throw new Error(`invalid compress type ${compressType}`);
}

const { AWFY } = process.env;
let srcFile: string = `${AWFY}/${benchmark}/output_xz/`;
if (allocation === NORMAL) {
  srcFile += `${benchmark}-NOR-HEAP.xz`;
}
if (allocation === ALIGNMENT) {
  srcFile += `${benchmark}-AL-HEAP.xz`;
}

console.log(srcFile);

const Globals = {
  lineCnt: 0n,
  writeCnt: 0n,
  readCnt: 0n,
  GCcnt: 0,
};

// 2GB baseArray,
const memory = new Memory(2 * 1024 * 1024, 32, 2 * 1024 * 1024, 32, compressType);
const cache = new CacheLRU(8, 64, 64, null, memory);

let GCs: bigint[][] = [];

function readFunc(line: string, fileReader: FileReader | null): void {
  Globals.lineCnt++;
  const words = line.split(" ");
  const op: string = words[0];
  if (op === "W") {
    Globals.writeCnt++;
    const addr: bigint = HexStr2BigInt(words[1]);
    const bytes: number = Number(words[2]);
    const buffer: ArrayBuffer = new ArrayBuffer(bytes);
    const uint8Array = new Uint8Array(buffer);
    uint8Array.forEach((_, idx) => {
      uint8Array[idx] = HexStr2Int(words[3+idx]);
    });
    const ma = new Op(Globals.lineCnt, 1, addr, buffer, uint8Array);
    cache.onAccess(ma);
    // if (Globals.writeCnt % 100000n === 0n) {
    //   console.log(`addr ${addr.toString(16)}`);
    //   console.log({ bytes });
    //   debugHexUint8Array(uint8Array);
    //   console.log(words.join(" "));

    // }
  } else if (op === "R") {
    Globals.readCnt++;
    const addr: bigint = HexStr2BigInt(words[1]);
    const bytes: number = Number(words[2]);
    const buffer: ArrayBuffer = new ArrayBuffer(bytes);
    const uint8Array = new Uint8Array(buffer);
    uint8Array.forEach((_, idx) => {
      uint8Array[idx] = HexStr2Int(words[3+idx]);
    });
    const ma = new Op(Globals.lineCnt, 0, addr, buffer, uint8Array);
    cache.onAccess(ma);
  } else if (op === "I") {
    const fr = fileReader as FileReader;
    console.log(`I ${words[1]} ${parcent(fr.bytesRead, fr.fileSize_)}%`);
    memory.getInfo();
  } else if (op === "G") {
    Globals.GCcnt++;
    GCs = [];
    console.log(`GC ${Globals.GCcnt}`);
    memory.getInfo();
  } else if (op === "E") {
    console.log(`GCEND ${Globals.GCcnt}`);
    GCs.forEach((a) => {
      let addr = a[0];
      let bytes = a[1];
      memory.tlTable.GCPLID(addr, bytes);
    });

    memory.getInfo();
  } else if (op === "D") {
    const addr: bigint = HexStr2BigInt(words[1]);
    const bytes: bigint = BigInt(words[2]);
    GCs.push([addr, bytes]);
  } else if (op === "L") {

  }
};

function finishFunc() {
  console.log(`# ${Globals.lineCnt} ${Globals.writeCnt} ${Globals.readCnt}`);
};

try {
  const fileReader = new FileReader();
  fileReader.open(srcFile);
  fileReader.readlines((line: string) => {
    if (line[0] == "I") {
      readFunc(line, fileReader);
    } else {
      readFunc(line, null);
    }
  }, finishFunc);
} catch (error) {
  console.log(error);
}
