export const countPreChar = (str: string, preChar: string = " "): number =>  {
  for (let i = 0; i < str.length; i += 1) {
    if (str[i] !== " ") {
      return i;
    }
  }
  return 0;
};
