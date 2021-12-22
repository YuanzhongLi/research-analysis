import { commentIn } from "./commentIn";
import { commentOut } from "./commentOut";

const { FREELIST_SPACE_PATH } = process.env;

import * as def from "./defines";

commentOut(FREELIST_SPACE_PATH as string, def.BCD_GC_DUMP, "//");
commentOut(FREELIST_SPACE_PATH as string, def.GC_DUMP, "//");
commentOut(FREELIST_SPACE_PATH as string, def.IEC_DUMP, "//");
commentOut(FREELIST_SPACE_PATH as string, def.PIN_BCD_GC_DUMP, "//");
commentOut(FREELIST_SPACE_PATH as string, def.PIN_GC_DUMP, "//");
commentOut(FREELIST_SPACE_PATH as string, def.PIN_IEC_DUMP, "//");
commentIn(FREELIST_SPACE_PATH as string, def.PIN_GCINFO, "//");
