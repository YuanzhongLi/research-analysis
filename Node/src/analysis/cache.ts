import { Op } from "./op";
import { Memory, Way } from "./memory";
import { isJsObject, Uint64Array } from "./util";
import { debug } from "console";
import { debugHexUint64Array, debugHexUint8Array } from "./debug";

/**
 * tailing zero count
 * 後ろから何ブロックが0か
 * @returns number (0 ~ 8)
 */
export function TZC(cacheLine: CacheLine): number {
    const lineBlocks = cacheLine.lineSize / 8;
    for (let i = lineBlocks - 1; i >= 0; i--) {
        if (cacheLine.values[i] !== 0n) {
        return lineBlocks - 1 - i;
        }
    }
    return lineBlocks;
};

export function decodeHeader(header: bigint) {
    const type = Number(header & ((1n << 6n) - 1n));
    const extra = Number((header >> 7n) & ((1n << 3n) - 1n));
    const hi = (header >> 32n);
    const size = Number((hi & ((1n << 18n) - 1n)));
    const bytes = size << 3;
    const original_bytes = (size - extra) << 3;
    // console.log({ type, extra, hi, size, bytes, original_bytes });
}

// decodeHeader(0x800006100n);

/**
 * 追い出されたキャッシュラインから情報を取得する
 * @param cacheLine
 * @returns
 */
export function decodeCacheLine(cacheLine: CacheLine): {
    isHeader: boolean;
    isJSO: boolean;
    type: number;
    bytes: number;
    original_bytes: number;
    tzc: number;
} {
    const header: bigint = cacheLine.values[0];
    const tzc: number = TZC(cacheLine);
    const type = Number(header & ((1n << 6n) - 1n));
    const extra = Number((header >> 7n) & ((1n << 3n) - 1n));
    const hi = (header >> 32n);
    const size = Number((hi & ((1n << 18n) - 1n)));
    const bytes = size << 3;
    const original_bytes = (size - extra) << 3;
    let isHeader = false;
    let isJSO = false;
    if (hi <= 1024n && type in isJsObject && (original_bytes / 8 + tzc) >= 8 && bytes % 64 === 0 && header !== 0n) {
        isHeader = true;
        isJSO = isJsObject[type];
    }
    return {
        isHeader,
        isJSO,
        type,
        bytes,
        original_bytes,
        tzc,
    };
};

export class CacheLine {
    dirty: boolean;
    valid: boolean;

    tag: bigint;
    time: bigint;

    lineSize: number;
    buffer: ArrayBuffer;
    uint8Array: Uint8Array;
    values: BigUint64Array;
    constructor(lineSize: number = 64) { // cache line: 8byte * 8
        this.dirty = false;
        this.valid = false;

        this.tag = 0n;
        this.time = 0n;

        this.lineSize = lineSize;
        this.buffer = new ArrayBuffer(lineSize);
        this.uint8Array = new Uint8Array(this.buffer);
        this.values = new BigUint64Array(this.buffer);
    }

    initValuesFromWay(way: Way): void {
        way.array.forEach((bi, idx) => {
            this.values[idx] = bi;
        });
    }

    initValuesFromUint64Array(uint64Array: Uint64Array): void {
        uint64Array.forEach((bi, idx) => {
            this.values[idx] = bi;
        });
    }
};


// A cache with LRU
class CacheBase {
    NUM_WAY_: number;
    NUM_SET_: number;
    LINE_SIZE_: number;

    NUM_SET_BITS_: number;
    LINE_SIZE_BITS_: number;

    LINE_NOT_TAG_MASK_: bigint;
    LINE_TAG_MASK_: bigint;
    SET_MASK_: bigint;

    nextLevelCache_: CacheBase|CacheLRU|CacheRandom|null;

    numHit: number;
    numPrefetch: number;
    numHitPrefetched: number;
    numMiss: number;

    sets: CacheLine[][];
    memory: Memory;

    /**
     * @param {number} numWay
     * @param {number} numSet
     * @param {number} lineSize
     * @param {CacheBase|CacheLRU|CacheRandom|null} nextLevelCache
    */
    constructor(
      numWay: number,
      numSet: number,
      lineSize: number,
      nextLevelCache: CacheBase|CacheLRU|CacheRandom|null,
      memory: Memory
    ) {
        this.NUM_WAY_ = numWay;
        this.NUM_SET_ = numSet;
        this.LINE_SIZE_ = lineSize;

        this.NUM_SET_BITS_ = Math.log2(this.NUM_SET_);
        this.LINE_SIZE_BITS_ = Math.log2(this.LINE_SIZE_);

        this.LINE_NOT_TAG_MASK_ = (1n << BigInt(this.LINE_SIZE_BITS_ + this.NUM_SET_BITS_)) - 1n;
        this.LINE_TAG_MASK_ = 0xffffffffffffffffn & ~((1n << BigInt(this.LINE_SIZE_BITS_ + this.NUM_SET_BITS_)) - 1n);
        this.SET_MASK_ = (1n << BigInt(this.NUM_SET_BITS_)) - 1n;
        this.nextLevelCache_ = nextLevelCache;

        this.numHit = 0;
        this.numPrefetch = 0;
        this.numHitPrefetched = 0;
        this.numMiss = 0;
        this.sets = [];
        this.reset();

        this.memory = memory;
    }

    reset(){
        this.sets = [];
        for (let i = 0; i < this.NUM_SET_; i++) {
            this.sets.push([]);
            for (let j = 0; j < this.NUM_WAY_; j++) {
                this.sets[i].push(new CacheLine());
            }
        }
    }

    get nextLevelCache(){
        return this.nextLevelCache_;
    }

    /** @param {bigint} addr */
    makeTag(addr: bigint): bigint{
        // 本来は上位のタグ部分をマスクで切り出すべきだが，
        // 下位を引き算することで同等の演算を行っている
        const tag = addr - (addr & this.LINE_NOT_TAG_MASK_);
        return addr - (addr & this.LINE_NOT_TAG_MASK_);
    }

    /** @param {bigint} addr */
    makeSetIndex(addr: bigint): number {
        return Number((addr >> BigInt(this.LINE_SIZE_BITS_)) & this.SET_MASK_);
    }

    /**
     * @param {bigint} setIndex
     * @param {bigint} tag
     * */
    makeFullAddr(setIndex: bigint, tag: bigint): bigint {
        return (setIndex << BigInt(this.LINE_SIZE_BITS_)) + tag;
    }

    // If addr hits this line, it returns true
    /**
     * @param {CacheLine} line
     * @param {number} addr
     * */
    lineIsHit(line: CacheLine, addr: bigint) {
        return line.valid && (line.tag === this.makeTag(addr));
    }

    //""" Update this line
    /**
     * @param {CacheLine} line
     * @param {Op} ma
     * @param ma.addrから何byte目に対するupdateか
     * */
    updateLine(line: CacheLine, ma: Op, bytes: number) {
        line.tag = this.makeTag(ma.addr);
        // console.log(`line.tag: ${line.tag.toString(2)}`);
        line.time = ma.id;
        line.valid = true;

        if (ma.insn_type == ma.INSN_TYPE_STORE) {
            // cache lineでの位置(0 ~ 63)
            let addr = ma.addr + BigInt(bytes);
            const pos: number = Number(addr % 64n);
            line.uint8Array[pos] = ma.uint8Array[bytes];
            line.dirty = true;
        }
    }

    // This method is called for each access.
    /**
     * 1byteごとの操作を行う
     * そのため同じキャッシュに対しての操作は無視する
     * ような実装となっている
     * 1byte前のsetIndexを記録しておくことでこれがことなるとき
     * 新しいキャッシュに移ったと判定する
     * @param {Op} ma
     * @returns {number}
     * */
    onAccess(ma: Op): void {
        let maAddr: bigint = ma.addr;
        let bytes: number = ma.buffer.byteLength;
        let preIndex: number = -1;
        let line: CacheLine = new CacheLine();
        for (let b = 0; b < bytes; b++) {
            let addr = maAddr + BigInt(b);
            let index: number = this.makeSetIndex(ma.addr);
            if (index === preIndex) { // まだ同じキャッシュライン
                this.updateLine(line, ma, b);
            }
            else { // 新しいキャッシュに移ったと判定する
                // Hit/miss decision
                let hit = false;
                let index: number = this.makeSetIndex(ma.addr);
                let set = this.sets[index];
                for (let i of set) {
                    if (this.lineIsHit(i, ma.addr)){
                        hit = true;
                        // line, ma, prefetched, demandAccessed
                        this.updateLine(i, ma, b);
                        line = i; // ヒットした場合以降はこのキャッシュラインに対する操作となる
                        break
                    }
                }

                if (hit) {
                    this.numHit += 1;
                }
                else { // miss
                    this.numMiss += 1;
                    // access misses in the cache && a line will be replaced
                    // Replacement
                    let target: number = this.replace(set, ma);
                    if (target >= 0) {
                        // 追い出し
                        let evictionCacheLine: CacheLine = set[target];
                        if (evictionCacheLine.valid) {
                            let evictionCacheLineAddr: bigint = this.makeFullAddr(
                                BigInt(target),
                                evictionCacheLine.tag,
                            );
                            // debugHexUint64Array(evictionCacheLine.values, 0);
                            this.memory.evictCacheLine(evictionCacheLine, evictionCacheLineAddr);
                        }

                        line = this.memory.fillCacheLine(ma.lineAddr); // 代わりに入るcache
                        set[target] = line;
                        this.updateLine(line, ma, b);
                    }

                    if (this.nextLevelCache_) {
                        this.nextLevelCache_.onAccess(ma);
                    }
                }
            }
            preIndex = index;
        }
    }

    /**
     * @param {CacheLine[]} set
     * @param {Op} ma
     * */
    replace(set: CacheLine[], ma: Op) {
        // Returns a replacement target index.
        return 0;
    }
}


// A cache with a LRU policy
export class CacheLRU extends CacheBase{

    /** Returns a replacement target index.
     * @param {CacheLine[]} set
     * @param {Op} ma
     * */
    replace(set: CacheLine[], ma: Op){
        let lruTime = ma.id;
        let lruPos = 0;

        for (let i = 0; i < set.length; i++) {
            let line = set[i];
            if (!line.valid){
                lruPos = i;
                break
            }

            // LRU
            if (line.valid && lruTime > line.time) {
                lruTime = line.time;
                lruPos = i;
            }
        }
        return lruPos;
    }
}


// A cache with a r&&om policy
class CacheRandom extends CacheBase {

    /** Returns a replacement target index.
     * @param {CacheLine[]} set
     * @param {Op} ma
     * */
    replace(set: CacheLine[], ma: Op){
        // Returns a replacement target index.
        return (Math.floor(Math.random() * this.NUM_WAY_) % this.NUM_WAY_);
    }
}

export function CreateCacheSystem(memory: Memory){
    /*
    #define PAGE_SIZE 4096
    #define LOG2_PAGE_SIZE 12
    */

    // LAST LEVEL CACHE
    // #define LLC_WAY 16
    // #define LLC_SET NUM_CPUS*2048
    //let cacheL3 = new CacheLRU(16, 2048, 64, null);

    // L2 CACHE
    // #define L2C_WAY 8
    // #define L2C_SET 512
    //let cacheL2 = new CacheLRU(8, 512, 64, cacheL3);

    // L1 DATA CACHE
    // #define L1D_WAY 8
    // #define L1D_SET 64
    //let cacheL1 = new CacheLRU(8, 64, 64, null/*cacheL2*/);

    let cache = new CacheLRU(16, 2048, 64, null/*cacheL2*/, memory);

    //cacheL1.prefetcher = new PrefetcherBase();
    //cacheL1.prefetcher = new StreamPrefetcher();
    return cache;
};
