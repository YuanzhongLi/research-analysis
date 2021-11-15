import fs from "fs";

import { countPreChar } from "./utils";

export const commentIn = (filePath: string, target: string, commentOutSymbol: "//" | "#") => {
  try {
    const file: string = fs.readFileSync(
      filePath,
      "utf8"
    );

    const fileArray: string[] = file.split("\n");
    const newfile: string = fileArray
      .map((t) => {
        if (t.includes(target) && t.includes(commentOutSymbol)) {
          const preSpaces: number = countPreChar(t);
          const ret: string = `${" ".repeat(preSpaces)}${t.slice(commentOutSymbol.length+1)}`;
          console.log(ret);
          return ret;
        }
        return t;
      })
      .join("\n");

    fs.writeFileSync(
      filePath,
      newfile,
    );
  } catch (err) {
    console.error(err);
  }
};
