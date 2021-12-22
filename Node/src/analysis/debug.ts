import { alignBitDigits, alignHexDigits, Uint64Array } from "./util";

export function debugBitUint64Array(uint64Array: Uint64Array,d = 64) {
  let log = "";
  uint64Array.forEach((bi, idx) => {
    log += alignBitDigits(bi, d);
    if (idx < uint64Array.length - 1) {
      log += "_";
    }
  });
  console.log(log);
};

export function debugBitUint8Array(uint8Array: Uint8Array, d = 8) {
  let log = "";
  uint8Array.forEach((bi, idx) => {
    log += alignBitDigits(bi, d);
    if (idx < uint8Array.length - 1) {
      log += "_";
    }
  });
  console.log(log);
};

export function debugHexUint64Array(uint64Array: Uint64Array, d = 16) {
  let log = "";
  uint64Array.forEach((bi, idx) => {
    log += alignHexDigits(bi, d);
    if (idx < uint64Array.length - 1) {
      log += "_";
    }
  });
  console.log(log);
};

export function debugHexUint8Array(uint8Array: Uint8Array, d = 2) {
  let log = "";
  uint8Array.forEach((bi, idx) => {
    log += alignHexDigits(bi, d);
    if (idx < uint8Array.length - 1) {
      log += "_";
    }
  });
  console.log(log);
};
