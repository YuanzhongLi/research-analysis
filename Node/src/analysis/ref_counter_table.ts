const refs = [
  1,
  2,
  3,
  4,
  5,
  6,
  7,
  8,
  9,
  10,
  20,
  30,
  40,
  50,
  60,
  70,
  80,
  90,
  100,
  150,
  200,
  250,
  300,
  350,
  400,
  450,
  500,
  550,
  600,
  650,
  700,
  750,
  800,
  850,
  900,
  950,
  1000,
  1200,
  1400,
  1600,
  1800,
  2000,
  2200,
  2400,
  2600,
  2800,
  3000,
  3500,
  4000,
  4500,
  5000,
  6000,
  7000,
  8000,
  9000,
  10000,
  11000,
  12000,
  13000,
  14000,
  15000,
  16000,
  17000,
  18000,
  19000,
  20000,
  (1 << 30)
];

export class RefTable {
  table: { [key: number]: number };
  constructor() {
    this.table = {};
    refs.forEach((n, idx) => {
      if (idx < refs.length - 1) {
        this.table[n] = 0;
      }
    })
  }

  add(ref: number, x: number = 1): void {
    refs.forEach((r, idx) => {
      if (idx < refs.length - 1) {
        if (r <= ref && ref <= refs[idx]) {
          this.table[ref] += x;
        }
      }
    });
  }

  merge(refTable: RefTable): void {
    Object.keys(refTable.table).forEach((key) => {
      this.table[Number(key)] += refTable.table[Number(key)];
    });
  }

  getInfo() {
    const ret: { [key: number]: number} = {};
    refs.forEach((r) => {
      if (this.table[r] > 0) {
        ret[r] = this.table[r];
      }
    });
    return ret;
  }

  infoString() {
    const info = this.getInfo();
    let ret = "";
    let l = Object.keys(info).length;
    Object.keys(info).forEach((key, idx) => {
      ret += `${key} ${info[Number(key)]}`;
      if (idx < l - 1) {
        ret += ", ";
      }
    });
    return ret;
  }
}
