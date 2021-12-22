import { CacheLine, decodeCacheLine } from "./cache";
import {
  compressBlocks,
  decompressBlocks,
  Uint64ArrayTo16and48Byte,
  Uint64ArrayToBitArray,
} from "./compress";
import { compareBigintArray, Uint64Array, parcent } from "./util";
import {
  getSigFunctions,
} from "./signature";
import { RefTable } from "./ref_counter_table";
import {
  HIDDEN_SIG_TYPE,
  META_SIG_TYPE,
  TOP16B_SIG_TYPE,
  BCD,
  AL_SIG_BASE64B,
  AL_SIG_BASEORIGINAL
} from "./constants";

import { debugHexUint64Array } from "./debug";

const { min } = Math;

export class Way {
  size: number;
  refCnt: number;
  array: BigUint64Array;

  /**
   * 実験ではwayからbucketへの参照を追加
   * wayが追い出される時にwayが所属するbucketから
   * deleteWayを呼べるため
   */
  bucket_: Bucket | null;
  /**
   * @param size (byte, 8の倍数, maxは64)
   * @param blocks (CacheLine | Uint64Array, 8byteデータブロックの配列)
   */
  constructor(size: number, blocks: CacheLine | Uint64Array) {
    this.size = size;
    this.refCnt = 0;
    this.array = new BigUint64Array(size / 8);
    if (blocks instanceof CacheLine) {
        this.array.forEach((_, idx) => {
        this.array[idx] = blocks.values[idx];
      });
    } else {
      this.array.forEach((_, idx) => {
        this.array[idx] = blocks[idx];
      });
    }

    /**
     * 実際にbucketに入るwayになって初めてbucketへの
     * 参照が入る
     * bucketから追い出された時は再びnullに戻す
     */
    this.bucket_ = null;
  }

  setBucket(bucket: Bucket | null): void {
    this.bucket_ = bucket;
  }

  reset(): void {
    this.size = 0;
    this.refCnt = 0;
    this.bucket_ = null;
  }
};

export class Bucket {
  array: Way[];
  ways: number;
  usedWays: number;
  wayMaxSize: number;
  remainSize: number;
  /**
   * @param way数 (できれば2の累乗で, 1Bucket = 64 * way数 byte)
   */
  constructor(ways: number) {
    this.array = [];
    this.ways = ways;
    this.usedWays = 0;
    this.wayMaxSize = ways * 64;
    this.remainSize = ways * 64;
  }

  /**
   *
   * @param sigType
   * @param sig
   * @param size (Way size)
   * @returns
   */
  sigMatch(sigType: number, sig: Uint64Array, size: number): {
    sigMatch: boolean;
    baseWay: Way | null;
  } {
    const getSig = getSigFunctions(sigType);
    let baseWay = null;
    let sigMatch = false;
    this.array.forEach((way: Way) => {
      const waySig = getSig(way);
      if (compareBigintArray(sig, waySig) && size === way.size) {
        sigMatch = true;
        baseWay = way;
      }
    });

    return { sigMatch, baseWay };
  }

  fullMatch(way: Way): {
    fullMatch: boolean;
    matchWay: Way | null;
  } {
    let matchWay = null;
    let fullMatch = false;
    this.array.forEach((w: Way) => {
      if (compareBigintArray(way.array, w.array)) {
        fullMatch = true;
        matchWay = w;
      }
    });

    return {
      fullMatch,
      matchWay,
    };
  }

  insertWay(way: Way): boolean {
    if (this.remainSize >= way.size && this.usedWays < this.ways) {
      this.remainSize -= way.size;
      this.usedWays += 1;
      way.bucket_ = this;
      this.array.push(way);
      return true;
    } else {
      return false
    }
  }

  deleteWay(way: Way): void {
    let idx = this.array.findIndex((el: Way) => {
      return el === way;
    });
    if (idx >= 0) {
      this.remainSize += way.size;
      this.usedWays -= 1;
      this.array[idx].bucket_ = null;
      this.array.splice(idx, 1);
    }
  }

  getInfo() {
    const usedWays = this.usedWays;
    if (usedWays === 0)  {
      return {
        usedWays,
      };
    }
    const waySizeCnt = [0, 0, 0, 0, 0, 0, 0, 0];
    const refTable = new RefTable();
    let waySizeSum = 0;
    this.array.forEach((w: Way) => {
      waySizeCnt[(w.size / 8) - 1]++;
      waySizeSum += w.size;
      refTable.add(w.refCnt);
    });

    return {
      usedWays,
      waySizeCnt,
      waySizeSum,
      refTable,
    };
  }
};

export function hashFunc(array: Uint64Array, buckets: number): number {
  const bucketsLog2 = Math.log2(buckets);
  const mask = (1 << bucketsLog2) - 1;

  let Hash64 = 0n;
  array.forEach((bi) => { Hash64 ^= bi});

  let hash32 = 0;
  hash32 ^= Number((Hash64 & 0xffffffffn));
  hash32 ^= Number((Hash64 >> 32n));

  let hash = 0;
  for (let i = 0; i < 32; i += bucketsLog2) {
    hash ^= ((hash32 >> i) & mask);
  }

  return hash;
};

export class HashTable {
  table: { [key: number]: Bucket };
  buckets: number;
  ways: number;
  size: number;
  /**
   * @param buckets (2の累乗)
   * @param ways
   */
  constructor(buckets: number, ways: number) {
    this.buckets = buckets;
    this.ways = ways;
    this.size = buckets * (ways * 64);
    this.table = {};
    for (let i = 0; i < buckets; i++) {
      this.table[i] = new Bucket(ways);
    }
  }

  getBucket(hash: number) {
    return this.table[hash];
  }

  getInfo() {
    let size = 0;
    let usedWayCnt = new Uint32Array(this.ways);
    const rTable = new RefTable();
    Object.keys(this.table).forEach((key) => {
      const bucket = this.table[Number(key)];
      const {
        usedWays,
        waySizeCnt,
        waySizeSum,
        refTable,
      } = bucket.getInfo();
      if (usedWays > 0) {
        usedWayCnt[usedWays - 1]++;
      }
      if (waySizeSum) {
        size += waySizeSum;
      }
      if (refTable) {
        rTable.merge(refTable);
      }
    });

    return { size, usedWayCnt, refTable: rTable };
  }
};

// export class Overflow {
//   table: { [key: string]: Way };
//   constructor() {
//     this.table = {};
//   }

//   insertWay(lineAddr: bigint, way: Way) {
//     this.table[lineAddr.toString(16)] = way;
//     way.refCnt++;
//   }
// };

export class PLID {
  base: Way | null;
  diff: Way | null;
  beCompressed: boolean;

  originalSize_: number; // 元々のサイズbyte
  baseOverflow_: boolean;
  diffOverflow_: boolean;
  sigType_: number;

  isZero_: boolean;

  // 部分的にGCをされた領域とサイズを記録
  partialGCBytes_: number;
  partialGCPos_: number;
  constructor() {
    this.base = null;
    this.diff = null;
    this.beCompressed = false;

    this.originalSize_ = 0;
    this.baseOverflow_ = false;
    this.diffOverflow_ = false;
    this.sigType_ = -1; // 最初は無効なsig type
    this.isZero_ = false;
    this.partialGCBytes_ = 0;
    this.partialGCPos_ = 0;
  }

  reset() {
    if (this.base instanceof Way) {
      const base: Way = this.base;
      base.refCnt -= 1;
      if (base.refCnt <= 0 && base.bucket_ !== null) {
        // 参照0でway削除
        base.bucket_.deleteWay(base);
      }
    }
    if (this.diff instanceof Way) {
      const diff = this.diff;
      diff.refCnt -= 1;
      if (diff.refCnt <= 0 && diff.bucket_ !== null) {
        // 参照0でway削除
        diff.bucket_.deleteWay(diff);
      }
    }
    this.base = null;
    this.diff = null;

    this.originalSize_ = 0;
    this.baseOverflow_ = false;
    this.diffOverflow_ = false;
    this.isZero_ = false;
    this.partialGCBytes_ = 0;
    this.partialGCPos_ = 0;
  }

  setBaseWay(baseWay: Way) {
    baseWay.refCnt += 1;
    this.base = baseWay;
  }

  setDiffWay(diffWay: Way) {
    diffWay.refCnt += 1;
    this.diff = diffWay;
  }

  get diffValid(): boolean { // baseのみかそれともdiffもあるのか
    return this.diff !== null;
  }

  /**
   * 解析用のデータ
   * 生きているならtrue, GCで回収されているならfalse
   */
  get valid(): boolean {
    return !((this.base === null) && (this.diff === null) && !this.isZero_);
  }
};

export class TranslationTable {
  table: { [key: string]: PLID }
  constructor() {
    this.table = {};
  }

  getPLID(lineAddr: bigint) {
    const key: string = lineAddr.toString(16);
    if (!(key in this.table)) {
      this.table[key] = new PLID();
    }
    return this.table[key];
  }

  PLIDexist(lineAddr: bigint): boolean {
    const key: string = lineAddr.toString(16);
    return (key in this.table)
  }

  GCPLID(addr: bigint, bytes: bigint): void {
    if (bytes === 0n) {
      return;
    }
    let remainBytes = bytes;
    let scan = addr;
    let scanLine = (scan >> 6n) << 6n;
    if (scan !== scanLine) {
      const space = scan % 64n;
      if (space >= remainBytes) {
        if (this.PLIDexist(scanLine)) {
          const plid = this.getPLID(scanLine);
          if (plid.valid) {
            plid.partialGCBytes_ = Number(remainBytes);
            plid.partialGCPos_ = Number(scan % 64n) / 8;
          }
        }
        return;
      }
      if (this.PLIDexist(scanLine)) {
        const plid = this.getPLID(scanLine);
        if (plid.valid) {
          plid.partialGCBytes_ = Number(space);
          plid.partialGCPos_ = Number(scan % 64n) / 8;
        }
      }
      remainBytes -= space;
    }

    if (remainBytes === 0n) {
      return;
    }

    // 以降scanはlineAddrとなる
    scan = scanLine + 64n;

    while (remainBytes > 0n) {
      if (remainBytes >= 64n) {
        if (this.PLIDexist(scan)) {
          const plid = this.getPLID(scan);
          plid.reset();
        }
        remainBytes -= 64n;
      } else {
        if (this.PLIDexist(scan)) {
          const plid = this.getPLID(scan);
          if (plid.valid) {
            plid.partialGCBytes_ = Number(remainBytes);
            plid.partialGCPos_ = 0;
          }
        }
        remainBytes = 0n;
        break;
      }
    }
  }

  getInfo() {
    let validPlidCnt = 0;
    let zeroCnt = 0;
    const originalSizeCnt = [0, 0, 0, 0, 0, 0, 0, 0]; // 8, 16, ..., 64byte;
    let baseOverflowSize = 0;
    let diffOverflowSize = 0;
    let GCBytes = 0;
    Object.keys(this.table).forEach((key: string) => {
      const plid = this.table[key];
      if (plid.valid) {
        validPlidCnt++;
        GCBytes += plid.partialGCBytes_;
        if (plid.originalSize_ > 0) {
          originalSizeCnt[(plid.originalSize_ / 8)-1]++;
        }
        if (plid.isZero_) {
          zeroCnt++;
        }
        if (plid.baseOverflow_) {
          const base = plid.base as Way;
          baseOverflowSize += base.size;
        }
        if (plid.diffOverflow_) {
          const diff = plid.diff as Way;
          diffOverflowSize += diff.size;
        }
        if (plid.baseOverflow_ && plid.diffOverflow_) {
          console.log("overflow error");
        }
      }
    });
    let originalSizeSum = 0;
    originalSizeCnt.forEach((cnt, idx) => {
      originalSizeSum += 8 * (idx + 1) * cnt;
    })
    return {
      validPlidCnt,
      zeroCnt,
      originalSizeCnt,
      originalSizeSum,
      baseOverflowSize,
      diffOverflowSize,
      GCBytes,
    };
  };
};

export class Memory {
  baseBuckets: number;
  baseWays: number;
  diffBuckets: number;
  diffWays: number;

  tlTable: TranslationTable;
  baseArray: HashTable;
  diffArray: HashTable;
  // overflow: Overflow;

  compressType_: number;
  constructor(
    baseBuckets: number,
    baseWays: number,
    diffBuckets: number,
    diffWays: number,
    compresseType: number,
  ) {
    this.baseBuckets = baseBuckets;
    this.baseWays = baseWays;
    this.diffBuckets = diffBuckets;
    this.diffWays = diffWays;

    this.tlTable = new TranslationTable();
    this.baseArray = new HashTable(baseBuckets, baseWays);
    this.diffArray = new HashTable(diffBuckets, diffWays);
    // this.overflow = new Overflow();

    this.compressType_ = compresseType;
  }

  fillCacheLine(lineAddr: bigint): CacheLine {
    const plid = this.tlTable.getPLID(lineAddr);
    const cacheLine = new CacheLine();
    if (plid.isZero_ || !plid.valid) {
      return cacheLine;
    }

    if (plid.diffValid) {
      const baseWay: Way = plid.base as Way;
      const diffWay: Way = plid.diff as Way;
      // console.log({ baseWay, diffWay });
      const originalBlocks: Uint64Array = decompressBlocks(baseWay.array, diffWay.array, plid.beCompressed, plid.sigType_);
      cacheLine.initValuesFromUint64Array(originalBlocks);
    }
    else {
      cacheLine.initValuesFromWay(plid.base as Way);
    }
    // console.log("get");
    // debugHexUint64Array(cacheLine.values, 0);
    return cacheLine;
  }

  evictCacheLine(line: CacheLine, lineAddr: bigint): void {
    if (!line.dirty) {
      return;
    }

    if (lineAddr % 64n !== 0n) {
      throw new Error(`invalid lineAddr ${lineAddr.toString(16)}`);
    }
    /**
     * reset plid
     */
    const plid = this.tlTable.getPLID(lineAddr);
    plid.reset();

    const {
      isHeader,
      isJSO,
      original_bytes,
      tzc,
    } = decodeCacheLine(line);

    if (tzc === 8) {
      plid.isZero_ = true;
    }
    else {
      let sig: Uint64Array;
      let sigType: number;
      let way: Way;
      let waySize: number;

      switch (this.compressType_) {
        case BCD:
          sigType = TOP16B_SIG_TYPE;
          waySize = 64;
          way = new Way(waySize, line);
          sig = getSigFunctions(sigType)(way);
          break;
        case AL_SIG_BASE64B:
          if (isJSO) { // hidden sig
            sigType = HIDDEN_SIG_TYPE;
            waySize = 64;
            way = new Way(waySize, line);
            sig = getSigFunctions(sigType)(way);
          } else if (isHeader) { // meta sig
            sigType = META_SIG_TYPE;
            waySize = 64
            way = new Way(waySize, line);
            sig = getSigFunctions(sigType)(way);
          } else { // custom sig
            if (line.values[1] === 0n) {
              sigType = META_SIG_TYPE;
            } else {
              sigType = HIDDEN_SIG_TYPE;
            }
            waySize = 64;
            way = new Way(waySize, line);
            sig = getSigFunctions(sigType)(way);
          }
          break;
        case AL_SIG_BASEORIGINAL:
          if (isJSO) { // hidden sig
            sigType = HIDDEN_SIG_TYPE;
            waySize = min(original_bytes, 64);
            way = new Way(waySize, line);
            sig = getSigFunctions(sigType)(way);
          } else if (isHeader) { // meta sig
            sigType = META_SIG_TYPE;
            waySize = min(original_bytes, 64);
            way = new Way(waySize, line);
            sig = getSigFunctions(sigType)(way);
          } else { // custom sig
            waySize = 64 - tzc * 8;
            if (waySize > 8) {
              sigType = HIDDEN_SIG_TYPE;
            } else {
              sigType = META_SIG_TYPE;
            }
            way = new Way(waySize, line);
            sig = getSigFunctions(sigType)(way);
          }
          break;
        default:
          throw new Error(`invalid sig type ${this.compressType_}`);
      }

      plid.sigType_ = sigType;
      plid.originalSize_ = min(original_bytes, 64);

      const baseHash = hashFunc(sig, this.baseBuckets);
      const baseBucket = this.baseArray.getBucket(baseHash);

      const { sigMatch, baseWay } = baseBucket.sigMatch(sigType, sig, waySize);

      if (sigMatch && baseWay !== null) { // compression (dedup)
        const {
          same,
          beCompressed,
          size,
          blocks,
        } = compressBlocks(baseWay.array, way.array, sigType);

        plid.beCompressed = beCompressed;
        plid.setBaseWay(baseWay);

        if (!same) {
          const diffWay = new Way(size, blocks);
          const diffHash = hashFunc(diffWay.array, this.diffBuckets);
          const diffBucket = this.diffArray.getBucket(diffHash);
          const { fullMatch, matchWay } = diffBucket.fullMatch(diffWay);

          if (fullMatch && matchWay !== null) {
            plid.setDiffWay(matchWay);
          }
          else {
            plid.setDiffWay(diffWay);
            if (!diffBucket.insertWay(diffWay)) { // diff overflow
              plid.diffOverflow_ = true;
            }
          }
        }
      }
      else {// can not find base way
        plid.setBaseWay(way);
        if (!baseBucket.insertWay(way)) { // base overflow
          plid.baseOverflow_ = true;
        }
      }
    }
  }

  getInfo() {
    const {
      validPlidCnt,
      zeroCnt,
      originalSizeCnt,
      originalSizeSum,
      baseOverflowSize,
      diffOverflowSize,
      GCBytes,
    } = this.tlTable.getInfo();
    const baseInfo = this.baseArray.getInfo();
    const baseSize = baseInfo.size;
    const baseUsedWayCnt = baseInfo.usedWayCnt;
    const baseRefTable = baseInfo.refTable;
    const diffInfo = this.diffArray.getInfo();
    const diffSize = diffInfo.size;
    const diffUsedWayCnt = diffInfo.usedWayCnt;
    const diffRefTable = diffInfo.refTable;
    console.log(`PLID ${validPlidCnt}`);
    console.log(`ZeroCnt ${zeroCnt}`);
    console.log(`OriginalSizeCnt ${originalSizeCnt}`);
    console.log(`BaseOverflowSize ${baseOverflowSize}`);
    console.log(`DiffOverflowSize ${diffOverflowSize}`);
    console.log(`GCBytes ${GCBytes}`);
    console.log(`BaseSize ${baseSize}`);
    console.log(`DiffSize ${diffSize}`);
    console.log(`BaseUsedWayCnt ${baseUsedWayCnt.join(" ")}`);
    console.log(`DiffUsedWayCnt ${diffUsedWayCnt.join(" ")}`);
    console.log(`BaseRefTable ${baseRefTable.infoString()}`);
    console.log(`DiffRefTable ${diffRefTable.infoString()}`);
    const refTable = new RefTable();
    refTable.merge(baseRefTable);
    refTable.merge(diffRefTable);
    console.log(`RefTable ${refTable.infoString()}`);

    let size = baseSize + diffSize + baseOverflowSize + diffOverflowSize;
    let sizePLIDIncluded = size + (validPlidCnt - zeroCnt)  * 8;
    console.log(`OriginalSizeSum ${originalSizeSum}`);
    console.log(`Size ${size}`);
    console.log(`SizePLIDIncluded ${sizePLIDIncluded}`);
    console.log(`Rate ${parcent(size, originalSizeSum)}% ${parcent(sizePLIDIncluded, originalSizeSum)}%`);
  }
};
