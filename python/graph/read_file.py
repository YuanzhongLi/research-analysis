import os
import sys
import pathlib
import numpy as np

current_dir = pathlib.Path(__file__).resolve().parent
# モジュールのあるパスを追加
sys.path.append(str(current_dir)+"/../")

from utils import calc_percent

ANALYSIS_PYTHON_RESULTS = os.environ["ANALYSIS_PYTHON_RESULTS"]

def getResultPath(benchmark, memthod, dump, top=0):
  if top == 0:
    return "{0}/{1}/{1}-{2}-{3}-analysis.txt".format(ANALYSIS_PYTHON_RESULTS, benchmark, memthod, dump)
  return "{0}/{1}/{1}-{2}-{3}-{4}-analysis.txt".format(ANALYSIS_PYTHON_RESULTS, benchmark, memthod, dump, top)

##
# returns byte_data, compressed_ratio_data
#
def read_file(file_path):
  section_start = False
  state = ""
  total_bytes = 0

  # [[
  # total,
  # virtual_total,
  # virtual_hidden,
  # virtula_meta,
  # total_hidden,
  # total_meta
  # total_compress,
  # hidden_compress,
  # meta_compress,
  # ]...]
  # BCDの場合hiddenとmataがない
  byte_data = []

  # [[
  # virtual_total,
  # virtual_hidden,
  # virtual_meta,
  # total_hidden,
  # total_meta,
  # total_compress,
  # hidden_compress,
  # meta_compress
  # ]...]
  # BCDの場合hiddenとmataがない
  compression_ratio_data = []
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
        if "VIRTUAL_TOTAL" == line.rstrip().rsplit()[0]:
          state = "VIRTUAL_TOTAL"
          continue
        if "VIRTUAL_HIDDEN" == line.rstrip().rsplit()[0]:
          state = "VIRTUAL_HIDDEN"
          continue
        if "VIRTUAL_META" == line.rstrip().rsplit()[0]:
          state = "VIRTUAL_META"
          continue
        if "HIDDEN_TOTAL" == line.rstrip().rsplit()[0]:
          state = "HIDDEN_TOTAL"
          continue
        if "META_TOTAL" == line.rstrip().rsplit()[0]:
          state = "HIDDEN_TOTAL"
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
        if state == "VIRTUAL_TOTAL":
          ary = line.rstrip().rsplit()
          bytes = int(ary[0])
          ratio = float(ary[2])
          byte_data[cnt].append(bytes)
          compression_ratio_data[cnt].append(ratio)
          state = ""
          continue
        if state == "VIRTUAL_HIDDEN":
          ary = line.rstrip().rsplit()
          bytes = int(ary[0])
          ratio = float(ary[2])
          byte_data[cnt].append(bytes)
          compression_ratio_data[cnt].append(ratio)
          state = ""
          continue
        if state == "VIRTUAL_META":
          ary = line.rstrip().rsplit()
          bytes = int(ary[0])
          ratio = float(ary[2])
          byte_data[cnt].append(bytes)
          compression_ratio_data[cnt].append(ratio)
          state = ""
          continue
        if state == "HIDDEN_TOTAL":
          ary = line.rstrip().rsplit()
          bytes = int(ary[0])
          ratio = float(ary[2])
          byte_data[cnt].append(bytes)
          compression_ratio_data[cnt].append(ratio)
          state = ""
          continue
        if state == "META_TOTAL":
          ary = line.rstrip().rsplit()
          bytes = int(ary[0])
          ratio = float(ary[2])
          byte_data[cnt].append(bytes)
          compression_ratio_data[cnt].append(ratio)
          state = ""
          continue
        if state == "TOTAL_COMPRESSION":
          ary = line.rstrip().rsplit()
          bytes, ratio = int(ary[0]), float(ary[2])
          byte_data[cnt].append(bytes)
          compression_ratio_data[cnt].append(ratio)
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

# for i in range(1, 7):
#   print(read_file(getResultPath("Bounce-small", "BCDAL", "GC", i)))
