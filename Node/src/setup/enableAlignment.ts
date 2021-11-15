import { commentIn } from "./commentIn";

const { BUILD_DEBUG_MAKEFILE } = process.env;
const target: string = "CPPFLAGS += -DCACHE_LINE_ALIGN";
commentIn(BUILD_DEBUG_MAKEFILE as string, target, "#");
