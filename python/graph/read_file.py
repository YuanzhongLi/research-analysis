import numpy as np

path = "./results"
benchmark = "Bounce-small"
file_path = "{0}/{1}/{2}-analysis.txt".format(path, benchmark, benchmark)

##
# returns byte_data, compressed_ratio_data
#
def read_file(file_path):
  section_start = False
  state = ""
  byte_data = [] # [[total, total_compress, hidden, meta]...]
  compression_ratio_data = [] # [[total, hidden, meta]...]
  cnt = -1
  with open(file_path, "r") as f:
    for line in f:
      if "start" in line:
        section_start = True
        byte_data.append([])
        compression_ratio_data.append([])
        cnt += 1
        continue

      if "end" in line:
        section_start = False
        continue

      if section_start:
        if "TOTAL" == line.rstrip().rsplit()[0]:
          state = "TOTAL"
          continue
        if "TOTAL_COMPRESSION" == line.rstrip().rsplit()[0]:
          state = "TOTAL_COMPRESSION"
          continue
        if "HIDDEN_COMPRESSION" == line.rstrip().rsplit()[0]:
          state = "HIDDEN_COMPRESSION"
          continue
        if "META_COMPRESSION" == line.rstrip().rsplit()[0]:
          state = "META_COMPRESSION"
          continue

        if state == "TOTAL":
          ary = line.rstrip().rsplit()
          bytes = int(ary[1])
          byte_data[cnt].append(bytes)
          state = ""
          continue
        if state == "TOTAL_COMPRESSION":
          ary = line.rstrip().rsplit()
          bytes, compression_ratio = int(ary[0]), float(ary[2])
          byte_data[cnt].append(bytes)
          compression_ratio_data[cnt].append(compression_ratio)
          state = ""
          continue
        if state == "HIDDEN_COMPRESSION":
          ary = line.rstrip().rsplit()
          # compression_ratio: 全体に対してどれくらいになったか
          # ratio: hidden class全体に対してどれくらいになったか
          bytes, compression_ratio, ratio = int(ary[0]), float(ary[2]), float(ary[3])
          byte_data[cnt].append(bytes)
          compression_ratio_data[cnt].append(compression_ratio)
          state = ""
          continue
        if state == "META_COMPRESSION":
          ary = line.rstrip().rsplit()
          # compressed_ratio: 全体に対してどれくらいになったか
          # ratio: meta class全体に対してどれくらいになったか
          bytes, compression_ratio, ratio = int(ary[0]), float(ary[2]), float(ary[3])
          byte_data[cnt].append(bytes)
          compression_ratio_data[cnt].append(compression_ratio)
          state = ""
          continue
  return np.array(byte_data), np.array(compression_ratio_data)
