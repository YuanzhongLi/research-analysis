import { Way } from "./memory";
import { Uint64Array } from "./util";
import {
  Uint64ArrayTo16and48Byte,
} from "./compress";
import {
  HIDDEN_SIG_TYPE,
  META_SIG_TYPE,
  TOP16B_SIG_TYPE,
} from "./constants";
import { debugHexUint64Array } from "./debug";

const sigTypes = [
  HIDDEN_SIG_TYPE,
  META_SIG_TYPE,
  TOP16B_SIG_TYPE,
];

export function isValidSigType(sigType: number) {
  return true;
  return sigType in sigTypes;
};

function getHiddenSig(way: Way): Uint64Array {
  return [way.array[1]];
};

function getMetaSig(way: Way): Uint64Array {
  return [way.array[0]]
};

function getTop16Sig(way: Way): Uint64Array {
  return  Uint64ArrayTo16and48Byte(way.array).signature;
};

export function getSigFunctions(sigType: number) {
  switch (sigType) {
    case HIDDEN_SIG_TYPE:
      return getHiddenSig;
    case META_SIG_TYPE:
      return getMetaSig;
    case TOP16B_SIG_TYPE:
      return getTop16Sig;
    default:
      throw new Error(`invalid sig type ${sigType}`);
  };
};
