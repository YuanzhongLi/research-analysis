
import { debugHexUint64Array, debugBitUint64Array } from "./debug";
import {
  isValidSigType,
} from "./signature";
import {
  HIDDEN_SIG_TYPE,
  META_SIG_TYPE,
  TOP16B_SIG_TYPE,
  B8bit,
} from "./constants";
import { intDiv, Uint64Array, BitArray } from "./util";
const { min } = Math;

/**
 * leading zero count
 * @param x
 * @param bit
 * @requires number
 */
export function LZC(x: bigint, bit: bigint = 64n): number {
  for (let i = 0n; i < bit; i++) {
    if ((x & (1n << (bit-1n-i))) !== 0n) {
      return Number(i);
    }
  }
  return Number(bit);
};

/**
 * bigintを64bitの0,1のbit配列に変換
 * @param x {bigint}
 * @returns BitArray
 */
export function bigintToBit64(x: bigint): BitArray {
  let buf: ArrayBuffer = new ArrayBuffer(64);
  let bit64 = new Uint8Array(buf);
  for (let i = 0; i < 64; i++) {
    bit64[63-i] = Number((x >> BigInt(i)) & 1n);
  }
  return bit64;
};

/**
 * 64bitの0,1のbit配列をbigintに変換
 * @param bit64 {BitArray}
 * @returns bigint
 */
export function bit64ToBigint(bit64: BitArray): bigint {
  let ret = 0n;
  for (let i = 63; i >= 0; i--) {
    if (bit64[i] === 1) {
      ret |= (1n << (63n - BigInt(i)));
    }
  }
  return ret;
};

/**
 * 64bit(8B)を圧縮
 * lzc(7bit) + lzcを除いたxor の0, 1のbit配列に変換
 * @param base
 * @param x
 * @returns BitArray
 */
export function compress8B(base: bigint, x: bigint): BitArray {
  const diff: bigint = base ^ x;
  let diff64 = bigintToBit64(diff);
  const lzc: number = LZC(diff);
  const nolzc = 64 - lzc;
  let buf = new ArrayBuffer(7 + nolzc);
  let bit = new Uint8Array(buf);
  for (let i = 0; i < 7; i++) {
    bit[6-i] = ((lzc >> i) & 1);
  }
  for (let i = 0; i < nolzc; i++) {
    bit[6 + (nolzc-i)] = diff64[63 - i];
  }
  return bit;
};

/**
 * @param bitArrays
 * @param size Byte (8の倍数)
 * @returns BigUint64Array
 */
export function bitArraysToBigUint64Array(bitArrays: BitArray[], size: number): BigUint64Array {
  let bitbuf = new ArrayBuffer(size * 8);
  let bitArray = new Uint8Array(bitbuf);
  let idx = 0;
  bitArrays.forEach((ba: BitArray) => {
    ba.forEach((u8) => {
      bitArray[idx] = u8;
      idx++;
    })
  });
  let uint64buf = new ArrayBuffer(size);
  let uint64Array = new BigUint64Array(uint64buf);

  idx = 0;
  for (let i = 0; i < (size / 8); i++) {
    for (let j = 0n; j < 64n; j++) {
      if (bitArray[i*64 + 63 - Number(j)] === 1) {
        uint64Array[i] |= (1n << j);
      }
    }
    idx++;
  }
  return uint64Array;
};

export function Uint64ArrayToBitArray(uint64Array: Uint64Array): BitArray {
  const bitBuf = new ArrayBuffer(uint64Array.length * 8 * 8);
  const bitArray: BitArray = new Uint8Array(bitBuf);
  uint64Array.forEach((bi, idx) => {
    for (let i = 0; i < 64; i++) {
      if (((bi >> BigInt(63 - i)) & 1n) === 1n) {
        bitArray[idx * 64 + i] = 1;
      }
    }
  });
  return bitArray;
};

export function Uint64ArrayTo16and48Byte(uint64Array: Uint64Array): {
  signature: Uint64Array;
  remainBlocks: Uint64Array;
} {
  let sigBitArrays: BitArray[] = [];
  let reBitArrays: BitArray[] = [];

  // debugHexUint64Array(uint64Array);

  uint64Array.forEach((bi) => {
    const bit64: BitArray = bigintToBit64(bi);
    const sigBuf = new ArrayBuffer(2 * 8); // 上位2byte
    const sigBitArray: BitArray = new Uint8Array(sigBuf);
    const reBuf = new ArrayBuffer(6 * 8); // 下位6byte
    const reBitArray: BitArray = new Uint8Array(reBuf);
    for (let i = 0; i < 16; i++) {
      sigBitArray[i] = bit64[i];
    }
    for (let i = 16; i < 64; i++) {
      reBitArray[i - 16] = bit64[i];
    }
    sigBitArrays.push(sigBitArray);
    reBitArrays.push(reBitArray);
  });

  return {
    signature: bitArraysToBigUint64Array(sigBitArrays, 16),
    remainBlocks: bitArraysToBigUint64Array(reBitArrays, 48),
  };
};


/**
 * 8byte * 6 -> 6byte(上位2bbyteが0の8byte) * 8
 * BCD用で基本的には使用
 * @param uint64Array
 */
export function B48ArrayToB64Array(uint64Array: Uint64Array): BigUint64Array {
  const bitArray = Uint64ArrayToBitArray(uint64Array);
  const ret = new BigUint64Array(8);
  for (let i = 0; i < 384; i += 48) {
    for (let j = 0; j < 48; j++) {
      if (bitArray[i+j] === 1) {
        ret[i/48] |= 1n << BigInt(48 - 1 - j);
      }
    }
  }

  return ret;
};

/**
 * 8Bのブロック達を圧縮
 * @param base
 * @param x
 * @param sigType {number}
 * @returns object {
 *  same:         boolean,
 *  beCompressed: boolean,
 *  size:         number (byte),
 *  blocks:       BigUint64Array,
 * }
 */
export function compressBlocks(base: Uint64Array, x: Uint64Array, sigType: number): {
  same: boolean;
  beCompressed: boolean;
  size:  number;
  blocks: BigUint64Array;
} {
  if (!isValidSigType(sigType)) {
    throw new Error("invalid sig type");
  }
  let baseWithoutSig: bigint[] = [];
  let xWithoutSig: bigint[] = [];
  switch (sigType) {
    case HIDDEN_SIG_TYPE:
      base.forEach((bi, idx) => {
        if (idx !== 1) {
          baseWithoutSig.push(bi);
        }
      });
      x.forEach((bi, idx) => {
        if (idx !== 1) {
          xWithoutSig.push(bi);
        }
      });
      break;
    case META_SIG_TYPE:
      base.forEach((bi, idx) => {
        if (idx !== 0) {
          baseWithoutSig.push(bi);
        }
      });
      x.forEach((bi, idx) => {
        if (idx !== 0) {
          xWithoutSig.push(bi);
        }
      });
      break;
    case TOP16B_SIG_TYPE:
      base.forEach((bi) => {
        baseWithoutSig.push(bi);
      });
      x.forEach((bi) => {
        xWithoutSig.push(bi);
      });
      break;
    default:
      base.forEach((bi, idx) => {
        baseWithoutSig.push(bi);
      });
      x.forEach((bi, idx) => {
        xWithoutSig.push(bi);
      });
  }

  const compressedBitArrays: Uint8Array[] = [];
  const diff = new BigUint64Array(baseWithoutSig.length);
  let bits: number = 0;
  let same: boolean = true;
  baseWithoutSig.forEach((bi: bigint, idx) => {
    const compressedBitArray: Uint8Array = compress8B(bi, xWithoutSig[idx]);
    same &&= (compressedBitArray.length === 7);
    compressedBitArrays.push(compressedBitArray);
    bits += compressedBitArray.length;
    diff[idx] = bi ^ xWithoutSig[idx];
  });

  if (sigType === TOP16B_SIG_TYPE) {
    const compressedBitSize: number = min(intDiv(bits + (B8bit - 1), B8bit) * B8bit, 48 * 8);
    if (bits >= compressedBitSize) {
      return {
        same,
        beCompressed: false,
        size: 48,
        blocks: new BigUint64Array(Uint64ArrayTo16and48Byte(diff).remainBlocks),
      };
    }

    return {
      same,
      beCompressed: true,
      size: compressedBitSize / 8,
      blocks: bitArraysToBigUint64Array(compressedBitArrays, compressedBitSize / 8),
    };
  }

  const baseBit: number = B8bit * baseWithoutSig.length;
  const compressedBitSize: number = min(intDiv(bits + (B8bit - 1), B8bit) * B8bit, baseBit);

  // debugBitUint64Array(base);
  // debugBitUint64Array(baseWithoutSig);
  // debugBitUint64Array(xWithoutSig);


  if (baseBit === compressedBitSize) {
    return {
      same,
      beCompressed: false,
      size:  compressedBitSize / 8,
      blocks: diff,
    };
  }

  return {
    same,
    beCompressed: true,
    size:  compressedBitSize / 8,
    blocks: bitArraysToBigUint64Array(
      compressedBitArrays,
      compressedBitSize / 8,
    )
  };
};

/**
 * 展開
 * TODO: 圧縮のときsignatureの比較が含まれていない時，
 * signatureの部分を追加する処理が必要
 *
 * diffBeCompressedがtrue
 *  BCDの場合:
 *    diff -> BitArray
 *    -> (Baseと同じlengthの)Uint64Array
 *    と復元してから
 *    baseとのXorをとっているので，
 *    baseのsignature部分が自動で入るのでこのままでok
 *  特定のブロックがsignature:
 *    比較から除外している場合は追加が必要になる
 *
 * diffBeCompressedがfalse
 *  BCDの場合:
 *    48byteを64byteに復元する必要がある
 *  特定のブロックがsignature:
 *    比較から除外している場合は追加が必要になる
 * @param baseBlocks
 * @param compressedDiffBlocks
 * @returns
 */
export function decompressBlocks(baseBlocks: Uint64Array, diffBlocks: Uint64Array, diffBeCompressed: boolean, sigType: number): BigUint64Array {
  // if (!isValidSigType(sigType)) {
  //   throw new Error("invalid sig type");
  // }

  const originalBlocks: Uint64Array = new BigUint64Array(baseBlocks.length);

  /**
   * diffBlocksを展開したものでBaseのlengthと同じサイズ
   * （beCompressedがfalseのときdiffBlocksはもともと
   * 展開されている）
   * sigTypeやbeCompressedによって適宜値の挿入などが必要
   */
  const decompressedDiffBlocks: bigint[] = [];

  if (diffBeCompressed) {
    const compressedDiffBitArray = Uint64ArrayToBitArray(diffBlocks);

    /**
     * baseBlocksのblock数とsigTypeによって
     * デコードされたdiffのblock数が決まる
     */
    let diffBlockNum = baseBlocks.length;
    let idx = 0;
    switch (sigType) {
      case HIDDEN_SIG_TYPE:
        diffBlockNum -= 1;
        break;
      case META_SIG_TYPE:
        diffBlockNum -= 1;
        break;
      case TOP16B_SIG_TYPE:
        break;
      default:
    }
    for (let j = 0; j < diffBlockNum; j++) {
      let lzc = 0;
      for (let i = 0; i < 7; i++) {
        if (compressedDiffBitArray[idx + i] === 1) {
          lzc |= (1 << (6-i));
        }
      }
      const nonlzc = 64 - lzc;
      idx += 7;

      let diffUint64: bigint = 0n;
      for (let i = 0; i < nonlzc; i++) {
        if (compressedDiffBitArray[idx + i] === 1) {
          diffUint64 |= (1n << BigInt(nonlzc - 1 - i));
        }
      }
      idx += nonlzc;
      decompressedDiffBlocks.push(diffUint64);
    };
    switch (sigType) {
      case HIDDEN_SIG_TYPE:
        decompressedDiffBlocks.splice(1, 0, 0n);
        break;
      case META_SIG_TYPE:
        decompressedDiffBlocks.splice(0, 0, 0n);
        break;
      case TOP16B_SIG_TYPE:
        /**
         * 6byte * 8に展開されているので
         * このままXORでOK
         */
        break;
      default:
    }
  }
  else {
    switch (sigType) {
      case HIDDEN_SIG_TYPE:
        diffBlocks.forEach((bi) => {
          decompressedDiffBlocks.push(bi);
        });
        decompressedDiffBlocks.splice(1, 0, 0n);
        break;
      case META_SIG_TYPE:
        diffBlocks.forEach((bi) => {
          decompressedDiffBlocks.push(bi);
        });
        decompressedDiffBlocks.splice(0, 0, 0n);
        break;
      case TOP16B_SIG_TYPE:
        const B64DiffBlocks = B48ArrayToB64Array(diffBlocks);
        originalBlocks.forEach((_, idx) => {
          originalBlocks[idx] = baseBlocks[idx] ^ B64DiffBlocks[idx];
        });
        B64DiffBlocks.forEach((bi: bigint) => {
          decompressedDiffBlocks.push(bi);
        })
        break;
      default:
        diffBlocks.forEach((bi) => {
          decompressedDiffBlocks.push(bi);
        });
    }
  }
  originalBlocks.forEach((_, idx) => {
    originalBlocks[idx] = baseBlocks[idx] ^ decompressedDiffBlocks[idx];
  });
  return originalBlocks;
};
