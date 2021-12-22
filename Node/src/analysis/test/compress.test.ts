import {
  alignBitDigits,
  BitArray,
} from "../util";

jest.mock("../signature", () => {
  const originalModule = jest.requireActual("../signature");
  return {
    __esModule: true,
    ...originalModule,
    isValidSigType: () => true,
  };
})

import {
  HIDDEN_SIG_TYPE,
  META_SIG_TYPE,
  TOP16B_SIG_TYPE,
} from "../constants";

import {
  debugBitUint64Array,
  debugHexUint64Array,
} from "../debug";

import {
  LZC,
  bigintToBit64,
  bit64ToBigint,
  compress8B,
  bitArraysToBigUint64Array,
  Uint64ArrayToBitArray,
  Uint64ArrayTo16and48Byte,
  B48ArrayToB64Array,
  compressBlocks,
  decompressBlocks,
} from "../compress";

test("LZC", () => {
  const inps = [
    0b0n,
    0b101n,
    0b1000n,
    0b101101n,
    0xffffffffffffffffn,
  ];

  const outs = [
    64,
    61,
    60,
    58,
    0,
  ];

  inps.forEach((inp, idx) => {
    expect(LZC(inp)).toEqual(outs[idx]);
  })
});

test("bigintToBit64 and bit64ToBigint", () => {
  const inps = [
    0b0n,
    0b101n,
    0b1000n,
    0b101101n,
    0xffffffffffffffffn,
  ];

  inps.forEach((inp) => {
    const out = bigintToBit64(inp);
    expect(out.join('')).toEqual(alignBitDigits(inp));
    expect(bit64ToBigint(out)).toEqual(inp);
  });
});

test("compress8B", () => {
  const inps = [
    0b0n,
    0b101n,
    0b1000n,
    0b101101n,
    0xffffffffffffffffn,
  ];

  const strOuts: string[] = [];
  inps.forEach((inp) => {
    const lzc = LZC(inp);
    if (lzc === 64) {
      strOuts.push(alignBitDigits(lzc, 7));
    } else {
      strOuts.push(alignBitDigits(lzc, 7) + inp.toString(2));
    }
  });

  inps.forEach((inp, idx) => {
    expect((compress8B(0n, inp)).join('')).toEqual(strOuts[idx]);
  });
});

test("bitArraysToBigUint64Array", () => {
  const bigints = [
    0b0n,
    0b101n,
    0b1000n,
    0b101101n,
    0xffffffffffffffffn,
  ];

  const inp: BitArray[] = bigints.map((bi) => {
    return compress8B(0n, bi);
  });

  const out: BigUint64Array = new BigUint64Array(2);
  out[0] = 0b1000000011110110101111001000011101010110100000001111111111111111n;
  out[1] = 0b1111111111111111111111111111111111111111111111110000000000000000n;
  expect(bitArraysToBigUint64Array(inp, 16)).toEqual(out);
});


test("Uint64ArrayToBitArray", () => {
  const inp = [
    0b0n,
    0b101n,
    0b1000n,
    0b101101n,
    0xffffffffffffffffn,
  ];

  let outStr = "";
  inp.forEach((bi) => {
    outStr += alignBitDigits(bi, 64);
  });

  expect(Uint64ArrayToBitArray(inp).join('')).toEqual(outStr);
});

test("Uint64ArrayTo16and48Byte", () => {
  const inp = [
    0xffffffffffffffffn,
    0x0000ffffffffffffn,
    0xeeeeeeeeeeeeeeeen,
    0x0000eeeeeeeeeeeen,
    0xddddddddddddddddn,
    0x0000ddddddddddddn,
    0xccccccccccccccccn,
    0x0000ccccccccccccn,
  ];

  const { signature, remainBlocks } = Uint64ArrayTo16and48Byte(inp);

  const sigOut = new BigUint64Array(2);
  sigOut[0] = 0xffff0000eeee0000n;
  sigOut[1] = 0xdddd0000cccc0000n;
  const reOut = new BigUint64Array(6);
  reOut[0] = 0xffffffffffffffffn;
  reOut[1] = 0xffffffffeeeeeeeen;
  reOut[2] = 0xeeeeeeeeeeeeeeeen;
  reOut[3] = 0xddddddddddddddddn;
  reOut[4] = 0xddddddddccccccccn;
  reOut[5] = 0xccccccccccccccccn;

  expect(signature).toEqual(sigOut);
  expect(remainBlocks).toEqual(reOut);
});

test("B48ArrayToB64Array", () => {
  const B64 = new BigUint64Array([
    0x0000ffffffffffffn,
    0x0000ffffffffffffn,
    0x0000eeeeeeeeeeeen,
    0x0000eeeeeeeeeeeen,
    0x0000ddddddddddddn,
    0x0000ddddddddddddn,
    0x0000ccccccccccccn,
    0x0000ccccccccccccn,
  ]);

  const { remainBlocks } = Uint64ArrayTo16and48Byte(B64);
  expect(B48ArrayToB64Array(remainBlocks)).toEqual(B64);
});

describe("compressBlocks", () => {
  describe("Sig Type default", () => {
    test("beCompressed: true", () => {
      const base = new BigUint64Array(4);
      base[0] = 0b0n;
      base[1] = 0b101n;
      base[2] = 0b1000n;
      base[3] = 0b101101n;
      const x = new BigUint64Array(4);
      x[0] = 0b1n;
      x[1] = 0b100n;
      x[2] = 0b10100n;
      x[3] = 0b101101n;

      const blocks = new BigUint64Array(1);
      blocks[0] = 0b0111111101111111011101111100100000000000000000000000000000000000n;
      const out = {
        same: false,
        beCompressed: true,
        size: 8,
        blocks,
      };

      const ret = compressBlocks(base, x, -1);
      expect(ret).toEqual(out);
    });

    test("beCompressed: false", () => {
      const base = new BigUint64Array(4);
      base[0] = 0b0n;
      base[1] = 0b101n;
      base[2] = 0b1000n;
      base[3] = 0b101101n;
      const x = new BigUint64Array(4);
      x[0] = (1n << 62n);
      x[1] = (0b100n << 60n);
      x[2] = (0b10100n << 50n);
      x[3] = (0b101101n << 50n);

      const blocks = new BigUint64Array(4);
      blocks[0] = 4611686018427387904n;
      blocks[1] = 4611686018427387909n;
      blocks[2] = 22517998136852488n;
      blocks[3] = 50665495807918125n;
      const out = {
        same: false,
        beCompressed: false,
        size: 32,
        blocks,
      };

      const ret = compressBlocks(base, x, -1);
      expect(ret).toEqual(out);
    });
  });

  describe("Sig Type HIDDEN_SIG_TYPE", () => {
    test("beCompressed: true", () => {
      const base = new BigUint64Array(5);
      base[0] = 0b0n;
      base[1] = 0xffffn;
      base[2] = 0b101n;
      base[3] = 0b1000n;
      base[4] = 0b101101n;
      const x = new BigUint64Array(5);
      x[0] = 0b1n;
      x[1] = 0xffffn;
      x[2] = 0b100n;
      x[3] = 0b10100n;
      x[4] = 0b101101n;

      const blocks = new BigUint64Array(1);
      blocks[0] = 0b0111111101111111011101111100100000000000000000000000000000000000n;
      const out = {
        same: false,
        beCompressed: true,
        size: 8,
        blocks,
      };

      const ret = compressBlocks(base, x, HIDDEN_SIG_TYPE);
      expect(ret).toEqual(out);
    });

    test("beCompressed: false", () => {
      const base = new BigUint64Array(5);
      base[0] = 0b0n;
      base[1] = 0xffffn;
      base[2] = 0b101n;
      base[3] = 0b1000n;
      base[4] = 0b101101n;
      const x = new BigUint64Array(5);
      x[0] = (1n << 62n);
      x[1] = 0xffffn;
      x[2] = (0b100n << 60n);
      x[3] = (0b10100n << 50n);
      x[4] = (0b101101n << 50n);

      const blocks = new BigUint64Array(4);
      blocks[0] = 4611686018427387904n;
      blocks[1] = 4611686018427387909n;
      blocks[2] = 22517998136852488n;
      blocks[3] = 50665495807918125n;
      const out = {
        same: false,
        beCompressed: false,
        size: 32,
        blocks,
      };

      const ret = compressBlocks(base, x, HIDDEN_SIG_TYPE);
      expect(ret).toEqual(out);
    });
  });

  describe("Sig Type META_SIG_TYPE", () => {
    test("beCompressed: true", () => {
      const base = new BigUint64Array(5);
      base[0] = 0xffffn;
      base[1] = 0b0n;
      base[2] = 0b101n;
      base[3] = 0b1000n;
      base[4] = 0b101101n;
      const x = new BigUint64Array(5);
      x[0] = 0xffffn;
      x[1] = 0b1n;
      x[2] = 0b100n;
      x[3] = 0b10100n;
      x[4] = 0b101101n;

      const blocks = new BigUint64Array(1);
      blocks[0] = 0b0111111101111111011101111100100000000000000000000000000000000000n;
      const out = {
        same: false,
        beCompressed: true,
        size: 8,
        blocks,
      };

      const ret = compressBlocks(base, x, META_SIG_TYPE);
      expect(ret).toEqual(out);
    });

    test("beCompressed: false", () => {
      const base = new BigUint64Array(5);
      base[0] = 0xffffn;
      base[1] = 0b0n;
      base[2] = 0b101n;
      base[3] = 0b1000n;
      base[4] = 0b101101n;
      const x = new BigUint64Array(5);
      x[0] = 0xffffn;
      x[1] = (1n << 62n);
      x[2] = (0b100n << 60n);
      x[3] = (0b10100n << 50n);
      x[4] = (0b101101n << 50n);

      const blocks = new BigUint64Array(4);
      blocks[0] = 4611686018427387904n;
      blocks[1] = 4611686018427387909n;
      blocks[2] = 22517998136852488n;
      blocks[3] = 50665495807918125n;
      const out = {
        same: false,
        beCompressed: false,
        size: 32,
        blocks,
      };

      const ret = compressBlocks(base, x, META_SIG_TYPE);
      expect(ret).toEqual(out);
    });
  });

  describe("Sig Type TOP16B_SIG_TYPE", () => {
    test("beCompressed: true", () => {
      const base = new BigUint64Array([
        0b0n | (0b1n << 48n),
        0b101n | (0b101n << 48n),
        0b1000n | (0b1000n << 48n),
        0b101101n | (0b101101n << 48n),
        0b0n,
        0b101n | (0b100n << 48n),
        0b1000n | (0b10100n << 48n),
        0b101101n | (0b101101n << 48n),
      ]);

      const x = new BigUint64Array([
        0b1n | (0b1n << 48n),
        0b100n | (0b101n << 48n),
        0b10100n | (0b1000n << 48n),
        0b101101n | (0b101101n << 48n),
        0b1n,
        0b100n | (0b100n << 48n),
        0b10100n | (0b10100n << 48n),
        0b101101n | (0b101101n << 48n),
      ]);

      const blocks = new BigUint64Array([
        0b0111111101111111011101111100100000001111111011111110111011111001n,
        0n,
      ]);
      const out = {
        same: false,
        beCompressed: true,
        size: blocks.length * 8,
        blocks,
      };

      const ret = compressBlocks(base, x, TOP16B_SIG_TYPE);
      // debugBitUint64Array(ret.blocks);
      expect(ret).toEqual(out);
    });

    test("beCompressed: false", () => {
      const base = new BigUint64Array([
        0b0n,
        0b101n,
        0b1000n,
        0b101101n,
        0b0n,
        0b101n,
        0b1000n,
        0b101101n,
      ]);

      const x = new BigUint64Array([
        0b1n | (0b1n << 44n),
        0b100n | (0b101n << 40n),
        0b10100n | (0b1000n << 40n),
        0b101101n | (0b101101n << 40n),
        0b1n | (0b1n << 45n),
        0b100n | (0b11n << 44n),
        0b10100n | (0b101n << 42n),
        0b101101n | (0b101101n << 40n),
      ]);

      const xors = new BigUint64Array(8);
      base.forEach((bi, idx) => {
        xors[idx] = bi ^ x[idx];
      });
      const blocks = Uint64ArrayTo16and48Byte(xors).remainBlocks;
      expect(B48ArrayToB64Array(blocks)).toEqual(xors);
      const out = {
        same: false,
        beCompressed: false,
        size: blocks.length * 8,
        blocks,
      };

      const ret = compressBlocks(base, x, TOP16B_SIG_TYPE);
      expect(ret).toEqual(out);
    });
  });
});

describe("decompressBlocks", () => {
  describe("Sig Type default", () => {
    test("beCompressed: true", () => {
      const base = new BigUint64Array([
        0b0n,
        0b101n,
        0b1000n,
        0b101101n,
      ]);
      const x = new BigUint64Array([
        0b1n,
        0b100n,
        0b10100n,
        0b101101n,
      ]);

      const { blocks, beCompressed} = compressBlocks(base, x, -1);
      const originalBlocks = decompressBlocks(base, blocks, beCompressed, -1);
      expect(originalBlocks).toEqual(x);
    });

    test("beCompressed: false", () => {
      const base = new BigUint64Array([
        0b0n,
        0b101n,
        0b1000n,
        0b101101n,
      ]);
      const x = new BigUint64Array([
        1n << 62n,
        0b100n << 60n,
        0b10100n << 50n,
        0b101101n << 50n,
      ]);

      const { blocks, beCompressed} = compressBlocks(base, x, -1);
      const originalBlocks = decompressBlocks(base, blocks, beCompressed, -1);
      expect(originalBlocks).toEqual(x);
    });
  });

  describe("Sig Type HIDDEN_SIG_TYPE", () => {
    test("beCompressed: true", () => {
      const base = new BigUint64Array([
        0b0n,
        0xffffn,
        0b101n,
        0b1000n,
        0b101101n,
      ]);

      const x = new BigUint64Array([
        0b1n,
        0xffffn,
        0b100n,
        0b10100n,
        0b101101n,
      ]);

      const { blocks, beCompressed } = compressBlocks(base, x, HIDDEN_SIG_TYPE);
      const originalBlocks = decompressBlocks(base, blocks, beCompressed, HIDDEN_SIG_TYPE);
      expect(originalBlocks).toEqual(x);
    });

    test("beCompressed: false", () => {
      const base = new BigUint64Array([
        0b0n,
        0xffffn,
        0b101n,
        0b1000n,
        0b101101n,
      ]);

      const x = new BigUint64Array([
        1n << 62n,
        0xffffn,
        0b100n << 60n,
        0b10100n << 50n,
        0b101101n << 50n,
      ]);

      const { blocks, beCompressed} = compressBlocks(base, x, HIDDEN_SIG_TYPE);
      const originalBlocks = decompressBlocks(base, blocks, beCompressed, HIDDEN_SIG_TYPE);
      expect(originalBlocks).toEqual(x);
    });
  });

  describe("Sig Type META_SIG_TYPE", () => {
    test("beCompressed: true", () => {
      const base = new BigUint64Array([
        0xffffn,
        0b0n,
        0b101n,
        0b1000n,
        0b101101n,
      ]);

      const x = new BigUint64Array([
        0xffffn,
        0b1n,
        0b100n,
        0b10100n,
        0b101101n,
      ]);

      const { blocks, beCompressed } = compressBlocks(base, x, META_SIG_TYPE);
      const originalBlocks = decompressBlocks(base, blocks, beCompressed, META_SIG_TYPE);
      expect(originalBlocks).toEqual(x);
    });

    test("beCompressed: false", () => {
      const base = new BigUint64Array([
        0xffffn,
        0b0n,
        0b101n,
        0b1000n,
        0b101101n,
      ]);

      const x = new BigUint64Array([
        0xffffn,
        1n << 62n,
        0b100n << 60n,
        0b10100n << 50n,
        0b101101n << 50n,
      ]);

      const { blocks, beCompressed } = compressBlocks(base, x, META_SIG_TYPE);
      const originalBlocks = decompressBlocks(base, blocks, beCompressed, META_SIG_TYPE);
      expect(originalBlocks).toEqual(x);
    });
  });

  describe("Sig Type TOP16B_SIG_TYPE", () => {
    test("beCompressed: true", () => {
      const base = new BigUint64Array([
        0b0n | (0b1n << 48n),
        0b101n | (0b101n << 48n),
        0b1000n | (0b1000n << 48n),
        0b101101n | (0b101101n << 48n),
        0b0n,
        0b101n | (0b100n << 48n),
        0b1000n | (0b10100n << 48n),
        0b101101n | (0b101101n << 48n),
      ]);

      const x = new BigUint64Array([
        0b1n | (0b1n << 48n),
        0b100n | (0b101n << 48n),
        0b10100n | (0b1000n << 48n),
        0b101101n | (0b101101n << 48n),
        0b1n,
        0b100n | (0b100n << 48n),
        0b10100n | (0b10100n << 48n),
        0b101101n | (0b101101n << 48n),
      ]);

      const { blocks, beCompressed } = compressBlocks(base, x, TOP16B_SIG_TYPE);
      const originalBlocks = decompressBlocks(base, blocks, beCompressed, TOP16B_SIG_TYPE);
      expect(originalBlocks).toEqual(x);
    });

    test("beCompressed: false", () => {
      const base = new BigUint64Array([
        0b0n,
        0b101n,
        0b1000n,
        0b101101n,
        0b0n,
        0b101n,
        0b1000n,
        0b101101n,
      ]);

      const x = new BigUint64Array([
        0b1n | (0b1n << 44n),
        0b100n | (0b101n << 40n),
        0b10100n | (0b1000n << 40n),
        0b101101n | (0b101101n << 40n),
        0b1n | (0b1n << 45n),
        0b100n | (0b11n << 44n),
        0b10100n | (0b101n << 42n),
        0b101101n | (0b101101n << 40n),
      ]);

      const { blocks, beCompressed } = compressBlocks(base, x, TOP16B_SIG_TYPE);
      const originalBlocks = decompressBlocks(base, blocks, beCompressed, TOP16B_SIG_TYPE);
      expect(originalBlocks).toEqual(x);
    });
  });
});
