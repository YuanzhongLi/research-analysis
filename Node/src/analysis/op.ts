export class Op {
    id: bigint;
    insn_type: 0 | 1;
    addr: bigint;
    buffer: ArrayBuffer;
    uint8Array: Uint8Array;
    hit: number;
    constructor(id: bigint, ins_type: 0 | 1, addr: bigint, buffer: ArrayBuffer, uint8Array: Uint8Array) {
        this.id = id; // 何個目の命令かを記録
        this.insn_type = ins_type; // Road/Store の2択

        this.addr = addr; // 良きこみ/書き込み先のaddress
        this.buffer = buffer;
        this.uint8Array = uint8Array;

        this.hit = 0;
    }

    get lineAddr(): bigint {
        return (this.addr >> 6n) << 6n;
    }

    /** @return {String} */
    get labelDetail() {
        return `hit:${this.hit}, insn_type:${this.insnTypeName}`;
    }

    get HIT_MISS(){         return 0; }
    get HIT_HIT(){          return 1; }

    // 0 から順に 0:load, 1:store
    get TYPE_LOAD(){                    return 0; }
    get TYPE_STORE(){                   return 1; }

    // 命令タイプ
    get INSN_TYPE_LOAD()              {return 0;}
    get INSN_TYPE_STORE()             {return 1;}

    get insnTypeName(){
        return [
          "load",
          "store",
        ][this.insn_type];
    }
};
