def LZC(x):
  for i in range(64):
    if (x & (1<<(63-i))) != 0:
      return i
  return 64

# 64bit(8byte)を何ビットに圧縮できるか
def compress_8byte(base, x):
  diff = base^x
  lzc = LZC(diff)
  return 7 + 64-lzc

# 64byte(キャッシュライン)を何bitに圧縮できるか
def compress_64byte(bases, xs):
  bits = 0
  for base, x in zip(bases, xs):
    bits += compress_8byte(base, x)
  byte16 = 128
  byte64 = 512
  return min(((bits + (byte16 - 1)) // (byte16)) * byte16, byte64)

def compress(bases_data, data):
  ret = 0
  bases_num = len(bases_data) // 8
  for i in range(bases_num):
    bases = []
    xs = []
    for j in range(8):
      bases.append(bases_data[i*8+j])
      xs.append(data[i*8+j])
    ret += compress_64byte(bases, xs)
  return ret
