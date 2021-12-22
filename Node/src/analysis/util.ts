export type Uint64Array = BigUint64Array | bigint[];
export type BitArray = Uint8Array;

export function HexStr2BigInt(hexStr: string): bigint {
  return BigInt(`0x${hexStr}`);
}

export function HexStr2Int(hexStr: string): number {
  return Number(`0x${hexStr}`);
}

export function parcent(son: number, mom: number, d: number = 2): number {
  return Number((son / mom * 100).toFixed(d));
}

export function intDiv(x: number, y: number): number {
  const remain: number = x % y;
  return (x - remain) / y;
};

export function compareBigintArray(x: Uint64Array, y: Uint64Array): boolean {
  if (x.length === y.length) {
    let ret = true;
    x.forEach((bi, idx) => {
      ret &&= (bi === y[idx]);
    });
    return ret;
  }
  return false;
};

export function alignBitDigits(x: number | bigint, d: number = 64): string {
  const strX = x.toString(2);
  if (strX.length >= d) {
    return strX;
  }
  const a = new Uint8Array(d- strX.length);
  return a.join('') + strX;
};

export function alignHexDigits(x: number | bigint, d: number = 16): string {
  const strX = x.toString(16);
  if (strX.length >= d) {
    return strX;
  }
  const a = new Uint8Array(d- strX.length);
  return a.join('') + strX;
};

export const isJsObject: { [key: number]: boolean } = {
  0: false,
  4: false,
  5: false,
  6: true,
  7: true,
  8: true,
  9: true,
  10: false,
  11: true,
  12: true,
  13: true,
  14: true,

  17: false,
  18: false,
  19: false,
  20: false,
  21: false,
  24: false,
  25: false,
  28: false,
  29: false,
  30: false,
  31: false,
};
