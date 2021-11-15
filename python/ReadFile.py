# [[type, byte, original byte, address, hidden class, data], ... ]
def read_file(file_path, dump="GC"):
  cnt = -1
  ret = []
  with open(file_path, "r") as f:
    start = False
    for line in f:
      if line.rstrip() == dump:
        ret.append([])
        cnt += 1
        start = True
        continue

      if line.rstrip() == dump+"END":
        start = False
        continue

      if start:
        l = line.rstrip().rsplit()
        type, byte, original_byte, address, hidden_class = int(l[0]), int(l[1]), int(l[2]), int(l[3], 16), int(l[4], 16)
        data = list(map(lambda x: int(x, 16), l[5:]))
        ret[cnt].append((type, byte, original_byte, address, hidden_class, data))

  return ret


# type: ["NOR", "AL"]
def read_BCD_file(file_path, dump="GC", type="NOR"):
  cnt = -1
  ret = []
  if type == "NOR":
    with open(file_path, "r") as f:
      start = False
      for line in f:
        if line.rstrip() == dump:
          ret.append([])
          cnt += 1
          start = True
          continue

        if line.rstrip() == dump+"END":
          start = False
          continue

        if start:
          l = line.rstrip().rsplit()
          data = list(map(lambda x: int(x, 16), l))
          ret[cnt].append((64, data))
  else: # type = AL
    # alignmentではOBDと同じファイルを使用
    with open(file_path, "r") as f:
      start = False
      for line in f:
        if line.rstrip() == dump:
          ret.append([])
          cnt += 1
          start = True
          continue

        if line.rstrip() == dump+"END":
          start = False
          continue

        if start:
          l = line.rstrip().rsplit()
          original_bytes = int(l[2])
          remain_original_bytes = original_bytes
          l_ = list(map(lambda x: int(x, 16), l[5:]))
          if __debug__:
            print(original_bytes)
            print(l_)
          for i in range(0, len(l_), 8):
            data = []
            block_original_bytes = 64
            if (remain_original_bytes < 64):
              block_original_bytes = remain_original_bytes
            remain_original_bytes -= block_original_bytes
            for j in range(8):
              data.append(l_[i+j])
            if __debug__:
              print((block_original_bytes, data))
            ret[cnt].append((block_original_bytes, data))
  return ret

# res = read_BCD_file("../awfy/Bounce-small-alignment.txt", "BCDGC", "alignment")
