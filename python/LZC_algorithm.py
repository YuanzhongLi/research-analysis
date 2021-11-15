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

# キャッシュラインのブロックのうちtop(0 ~ 6)から始まる2ブロック
# (2byte)とその他(6byte)に分ける
def divideLines(x, top=0):
  re = 0xffffffffffffffff
  mask = ((1<<16)-1) << (48 - top * 8)
  reverse_mask = ~mask & re
  byte2 = (x & mask) >> (48 - top * 8)
  reverse_masked = x & reverse_mask
  tmp = (1<<(64 - ((top+2)*8))) - 1
  byte6 = 0 | ((reverse_masked >> 16) & (~tmp & re)) | (reverse_masked & tmp)

  return byte2, byte6

  # if __debug__:
  #   print(format(mask, "016x"), format(reverse_mask, "016x"))
  #   print(format(x, "016x") ,format(byte2, "04x"))
  #   print(format(x, "016x") ,format(reverse_masked, "016x"), format(byte6, "016x"))

# BCDで2byte * 8を64byteブロックからkeyとして取り出す
# 残りの6byte * 8はlistとして取り出す
def extract16byte(xs, top=0):
  l2 = [] # keyとなる2byte
  for x in xs:
    byte2, _ = divideLines(x, top)
    l2.append(format(byte2, "04x"))
  return ''.join(l2)

def extract48byte(xs, top=0):
  l6 = [] # 残りの6byte
  for x in xs:
    _, byte6 = divideLines(x, top)
    l6.append(byte6)
  return l6

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
def compress_48byte(bases, xs, top=0): # bases, xsは普通のもの(8byte * 8)
  bits = 0
  for base, x in zip(extract48byte(bases, top), extract48byte(xs, top)):
    bits += compress_6byte(base, x)
  byte16 = 128
  byte48 = byte16 * 3
  return min(((bits + (byte16 - 1)) // (byte16)) * byte16, byte48)
