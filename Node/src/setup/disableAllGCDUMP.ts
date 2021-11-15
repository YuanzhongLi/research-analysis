import { commentOut } from "./commentOut";

const { FREELIST_SPACE_PATH } = process.env;
const GC_DUMP: string = "#define GC_DUMP";
const BCD_GC_DUMP: string = "#define BCD_GC_DUMP";
commentOut(FREELIST_SPACE_PATH as string, BCD_GC_DUMP, "//");
commentOut(FREELIST_SPACE_PATH as string, GC_DUMP, "//");
