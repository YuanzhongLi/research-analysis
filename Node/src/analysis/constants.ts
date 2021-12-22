// sig type
export const HIDDEN_SIG_TYPE = 0;
export const META_SIG_TYPE = 1;
export const TOP16B_SIG_TYPE = 2;

// compress type
export const BCD = 0;
export const AL_SIG_BASE64B = 1;
export const AL_SIG_BASEORIGINAL = 2;

const compressTypes = [
  BCD,
  AL_SIG_BASE64B,
  AL_SIG_BASEORIGINAL,
];

export function validCompressType(compressType: number) {
  return compressType in compressTypes;
};

export const B8bit = 64;

// allocation type
export const NORMAL = 0;
export const ALIGNMENT = 1;
