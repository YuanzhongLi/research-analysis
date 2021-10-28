# [[type, byte, original byte, address, hidden class, data], ... ]
def read_file(file_path, option="GC"):
  cnt = -1
  ret = []
  with open(file_path, "r") as f:
    start = False
    for line in f:
      if line.rstrip() == option:
        ret.append([])
        cnt += 1
        start = True
        continue

      if line.rstrip() == option+"END":
        start = False
        continue

      if start:
        l = line.rstrip().rsplit()
        type, byte, original_byte, address, hidden_class = int(l[0]), int(l[1]), int(l[2]), int(l[3], 16), int(l[4], 16)
        data = list(map(lambda x: int(x, 16), l[5:]))
        ret[cnt].append((type, byte, original_byte, address, hidden_class, data))

  return ret
