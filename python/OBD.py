import sys
import os

from ReadFile import read_file
from preprocessing import alignment_preprocessing
from printout import print_compression_results
from create_memory_picture import create_pic_alignment, create_new_colors_set
from analyze import alignment_analyze, getOutputPath

AWFY = os.environ["AWFY"]
CELL_LEN = 8
INF = (1<<63) - 1

## 実行
benchmark = sys.argv[1]
dump = "GC"
if len(sys.argv) > 2:
  dump = sys.argv[2]
al_snap_shots = read_file(getOutputPath(benchmark, "OBD", dump), dump)
al_snap_shot_num = len(al_snap_shots)
al_section = al_snap_shot_num // 10

for i, snap_shot in enumerate(al_snap_shots):
  create_pic = True
  if i >= 10 and i % al_section != 0 and i < al_snap_shot_num-10:
    create_pic = False

  print("===== start {0} =====".format(i+1))
  # create new used_cs
  used_cs = create_new_colors_set()

  # preprocessing
  original_total_bytes, \
  original_hidden_class_bytes, \
  original_meta_class_bytes, \
  dict, targetCellTypeDict, alignment_height \
  = alignment_preprocessing(snap_shot, used_cs, detail=False)

  # analyze
  # result total bytes: 圧縮したもの圧縮できなかったものの合計
  result_total_bytes, \
  total_compression_bytes, \
  total_compressed_bytes,  \
  hidden_class_compression_bytes, \
  hidden_class_compressed_bytes, \
  meta_class_compression_bytes, \
  meta_class_compressed_bytes = \
  alignment_analyze(snap_shot, targetCellTypeDict)

  # print compression results
  print_compression_results(
    result_total_bytes,
    total_compression_bytes,
    hidden_class_compression_bytes,
    meta_class_compression_bytes,
    original_total_bytes,
    original_hidden_class_bytes,
    original_meta_class_bytes,
  )

  print("===== end {0} =====".format(i+1))
  print()

  # create memory pic
  if create_pic:
    title = "{0}-{1}".format(dump, i+1)
    create_pic_alignment(benchmark, snap_shot, alignment_height, targetCellTypeDict, title)
