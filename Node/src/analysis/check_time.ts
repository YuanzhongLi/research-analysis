import { Uint64 } from "./uint64";

let a = 0n;
let s = Date.now();
for (let i = 0; i < 100000000; i++) {
  a += 1n;
}
let e = Date.now();
console.log(e - s);

let b = 0;
s = Date.now();
for (let i = 0; i < 100000000; i++) {
  b += 1;
}
e = Date.now();
console.log(e - s);

// let u = new Uint64(0, 0);
// let one = new Uint64(0, 1);
// s = Date.now();
// for (let i = 0; i < 100000000; i++) {
//   let c = Uint64.add(u, u);
// }
// e = Date.now();
// console.log(e - s);

s = Date.now();
for (let i = 0; i < 100000000; i++) {
  let c = 1n << 2n;
}
e = Date.now();
console.log(e - s);

s = Date.now();
for (let i = 0; i < 100000000; i++) {
  let c = 1 << 2;
}
e = Date.now();
console.log(e - s);

s = Date.now();
for (let i = 0; i < 100000000; i++) {
  (1n).toString(16);
};
e = Date.now();
console.log(e - s);
