import os
import cv2
import numpy as np

from cell_types import CellTypeDict, color2num, BLACK
from utils import get_key

CELL_LEN = 8
INF = (1<<63)-1

ANALYSIS_PYTHON_RESULTS = os.environ["ANALYSIS_PYTHON_RESULTS"]

# memory_type: ["original", "alignment"]
# pic_type: ["meta", "hidden", "data"]
def getSavePath(benchmark, memory_type, pic_type, title):
  return "{0}/{1}/pic/{2}/{3}/{4}.png".format(ANALYSIS_PYTHON_RESULTS, benchmark, memory_type, pic_type, title)

# すでに使用している色を保持しているsetを作成
def create_new_colors_set():
  used_cs = set([])
  for v in CellTypeDict.values():
    c = v[1]
    used_cs.add(color2num(c))
  return used_cs

def create_pic_alignment(benchmark, snap_shot, height, targetCellTypeDict, title):
  width = 8
  # meta classによる色の仕分け
  meta_img = np.zeros((height*CELL_LEN, width*CELL_LEN, 3), dtype=np.uint8)
  # 圧縮対象(hidden class + 圧縮可能なmeta class)、その他はmeta classによる色の仕分け
  hidden_img = np.zeros((height*CELL_LEN, width*CELL_LEN, 3), dtype=np.uint8)
  # data_img = np.zeros((height*CELL_LEN, width*CELL_LEN, 3), dtype=np.uint8)

  h = 0
  for type, byte, original_byte, _, hidden_class, data in snap_shot:
    section_num = byte // 8
    hs = section_num // 8
    # re = section_num % 8
    key = get_key(type, hidden_class, byte)
    is_target = key in targetCellTypeDict
    remain_original_byte = original_byte

    for _ in range(hs):
      w = width
      if remain_original_byte < 64:
        w = remain_original_byte // 8
        remain_original_byte = 0
      else:
        remain_original_byte -= 64

      # meta
      meta_img[h*CELL_LEN:(h+1)*CELL_LEN, 0:w*CELL_LEN] = CellTypeDict[type][1]
      meta_img[(h+1)*CELL_LEN-1:(h+1)*CELL_LEN, 0:width*CELL_LEN] = BLACK

      # hidden
      if is_target:
        hidden_img[h*CELL_LEN:(h+1)*CELL_LEN, 0:w*CELL_LEN] = targetCellTypeDict[key]
      else:
        hidden_img[h*CELL_LEN:(h+1)*CELL_LEN, 0:w*CELL_LEN] = CellTypeDict[type][1]
      hidden_img[(h+1)*CELL_LEN-1:(h+1)*CELL_LEN, 0:width*CELL_LEN] = BLACK

      h += 1

  cv2.imwrite(getSavePath(benchmark, "alignment", "meta", title), meta_img)
  cv2.imwrite(getSavePath(benchmark, "alignment", "hidden", title), hidden_img)

# outputのNORからmemory snapshotのpicを作る
def create_pic_original(min_address, max_address, benchmark, snapshot, targetCellTypeDict, title):
  width = 8
  height = (max_address - min_address) // 64

  # meta classによる色の仕分け
  meta_img = np.zeros((height*CELL_LEN, width*CELL_LEN, 3), dtype=np.uint8)
  # 圧縮対象(hidden class + 圧縮可能なmeta class)、その他はmeta classによる色の仕分け
  # hidden_img = np.zeros((height*CELL_LEN, width*CELL_LEN, 3), dtype=np.uint8)
  # data_img = np.zeros((height*CELL_LEN, width*CELL_LEN, 3), dtype=np.uint8)

  for type, byte, _, address, hidden_class, _ in snapshot:
    relative_address = address - min_address
    id = relative_address // 8
    blocks = byte // 8 # 8 byte blockの個数
    key = get_key(type, hidden_class, byte)
    for i in range(blocks):
      h, w = (id+i) // width, (id+i) % width

      # meta
      meta_img[h*CELL_LEN:(h+1)*CELL_LEN, w*CELL_LEN:(w+1)*CELL_LEN] = CellTypeDict[type][1]
      meta_img[(h+1)*CELL_LEN-1:(h+1)*CELL_LEN, w*CELL_LEN:(w+1)*CELL_LEN] = BLACK

  cv2.imwrite(getSavePath(benchmark, "original", "meta", title), meta_img)
