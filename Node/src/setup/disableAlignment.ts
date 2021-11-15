import { commentOut } from "./commentOut";

const { BUILD_DEBUG_MAKEFILE } = process.env;
console.log(BUILD_DEBUG_MAKEFILE);
const target: string = "CPPFLAGS += -DCACHE_LINE_ALIGN";
commentOut(BUILD_DEBUG_MAKEFILE as string, target, "#");
