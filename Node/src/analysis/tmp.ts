const buf = new ArrayBuffer(8);
const a = new Uint8Array(buf);
const b = new BigUint64Array(buf);
a[0] = 0x61;
a[3] = 0x08;

console.log(a);
console.log(b[0].toString(16));
console.log(buf);
b[0] = 0x8000072n;
console.log(a);
console.log(b[0].toString(16));
