import numpy as np

path = "./results"
benchmark = "Bounce-small"
file_path = "{0}/{1}/{2}-analysis.txt".format(path, benchmark, benchmark)

def read_file(file_path):
  section_start = False
  state = ""
  byte_data = [] # [[total, hidden, meta]...]
  compressed_ratio_data = [] # [[total, hidden, meta]...]
  cnt = -1
  with open(file_path, "r") as f:
    for line in f:
      if "start" in line:
        section_start = True
        byte_data.append([])
        compressed_ratio_data.append([])
        cnt += 1
        continue

      if "end" in line:
        section_start = False
        compressed_ratio = ""
        continue

      if section_start:
        if "TOTAL_COMPRESSED" in line:
          state = "TOTAL_COMPRESSED"
          continue
        if "HIDDEN_COMPRESSED" in line:
          state = "HIDDEN_COMPRESSED"
          continue
        if "META_COMPRESSED" in line:
          state = "META_COMPRESSED"
          continue

        if state == "TOTAL_COMPRESSED":
          ary = line.rstrip().rsplit()
          bytes, compressed_ratio = int(ary[0]), float(ary[2])
          byte_data[cnt].append(bytes)
          compressed_ratio_data[cnt].append(compressed_ratio)
          state = ""
          continue
        if state == "HIDDEN_COMPRESSED":
          ary = line.rstrip().rsplit()
          # compressed_ratio: 全体に対してどけくらい減らしたか
          # ratio: hidden class全体に対してどれくらい減らしたか
          bytes, compressed_ratio, ratio = int(ary[0]), float(ary[2]), float(ary[3])
          byte_data[cnt].append(bytes)
          compressed_ratio_data[cnt].append(compressed_ratio)
          state = ""
          continue
        if state == "META_COMPRESSED":
          ary = line.rstrip().rsplit()
          # compressed_ratio: 全体に対してどけくらい減らしたか
          # ratio: meta class全体に対してどれくらい減らしたか
          bytes, compressed_ratio, ratio = int(ary[0]), float(ary[2]), float(ary[3])
          byte_data[cnt].append(bytes)
          compressed_ratio_data[cnt].append(compressed_ratio)
          state = ""
          continue
  return np.array(byte_data), np.array(compressed_ratio_data)


print(read_file(file_path))
