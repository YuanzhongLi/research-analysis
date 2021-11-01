def LZC(x, bit=64):
  if __debug__:
    print(format(x, '0{0}b'.format(bit)))
  for i in range(bit):
    if (x & (1<<(bit-1-i))) != 0:
      if __debug__:
        print(i)
      return i
  if __debug__:
    print(bit)
  return bit

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
  # if len(bases_data) != len(data):
  #   print(len(bases_data), len(data))
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

# BCDで2byte * 8を64byteブロックから取り出す
# return string
def extract_upper_16byte(xs):
  l = []
  for x in xs:
    byte2 = x >> 48
    l.append(format(byte2, "04x"))
  return ''.join(l)

# return list
def extract_down_48byte(xs):
  l = []
  for x in xs:
    byte6 = x % (1<<48)
    l.append(byte6)
  return l

# BCDで48bit(6byte)を何ビットに圧縮できるか
def compress_6byte(base, x): # base, xはともに6byte
  diff = base^x
  lzc = LZC(diff, 48)
  return 7 + 48-lzc

# 48byte(BCDでの16byteを除いたキャッシュライン)を何bitに圧縮できるか
def compress_48byte(bases, xs): # bases, xsは普通のもの(8byte * 8)
  bits = 0
  for base, x in zip(extract_down_48byte(bases), extract_down_48byte(xs)):
    bits += compress_6byte(base, x)
  byte16 = 128
  byte48 = byte16 * 3
  return min(((bits + (byte16 - 1)) // (byte16)) * byte16, byte48)
