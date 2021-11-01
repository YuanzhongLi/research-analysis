import cv2
import numpy as np
import sys

from cell_types import CellTypeDict, color2num, BLACK, is_hidden_class
from ReadFile import read_file
from LZC_algorithm import compress
from preprocessing import alignment_preprocessing, get_key
from printout import print_compression_results
from utils import divide16

CELL_LEN = 8
INF = (1<<63) - 1

def create_new_colors_set():
  used_cs = set([])
  for v in CellTypeDict.values():
    c = v[1]
    used_cs.add(color2num(c))
  return used_cs

def alignment_analyze(snap_shot, title, height, \
  targetCellTypeDict, save_path, create_pic=True, color_pic_by_data=False):
  width = 8

  # compressed bytes: どれくらい減ったか
  # compressioin bytes: どれくらいになったか
  # compressed bytes + compression bytes = 元のサイズ
  base_dict = {}
  hidden_class_compressed_bits = 0
  hidden_class_compression_bits = 0
  meta_class_compressed_bits = 0
  meta_class_compression_bits = 0
  total_compressed_bits = 0
  total_bits = 0
  total_compression_bits = 0

  if create_pic:
    img = np.zeros((height*CELL_LEN, width*CELL_LEN, 3), dtype=np.uint8)
    img_hidden_class = np.zeros((height*CELL_LEN, width*CELL_LEN, 3), dtype=np.uint8)

    h = 0
    for type, byte, original_byte, _, hidden_class, data in snap_shot:
      section_num = byte // 8
      hs = section_num // 8
      re = section_num  % 8
      key = get_key(type, hidden_class, byte)
      is_target = key in targetCellTypeDict

      if is_target:
        if key in base_dict:
          compression_bits = compress(base_dict[key], data)
          total_bits += compression_bits
          total_compression_bits += compression_bits
          compressed_bits = original_byte * 8 - compression_bits
          total_compressed_bits += compressed_bits
          if key[0] == -1: # hidden class
            hidden_class_compressed_bits += compressed_bits
            hidden_class_compression_bits += compression_bits
          else: # meta class
            meta_class_compressed_bits += compressed_bits
            meta_class_compression_bits += compression_bits
        else:
          base_dict[key] = data
          total_bits += 8 * divide16(original_byte)
          if is_hidden_class(type):
            hidden_class_compression_bits += 8 * divide16(original_byte)
          else:
            meta_class_compression_bits += 8 * divide16(original_byte)
      else:
        total_bits += 8 * divide16(original_byte)
        if is_hidden_class(type):
          hidden_class_compression_bits += 8 * divide16(original_byte)
        else:
          meta_class_compression_bits += 8 * divide16(original_byte)

      for _ in range(hs):
        img[h*CELL_LEN:(h+1)*CELL_LEN, 0:width*CELL_LEN] = CellTypeDict[type][1]
        img[(h+1)*CELL_LEN-1:(h+1)*CELL_LEN, 0:width*CELL_LEN] = BLACK
        # compress target
        if is_target:
          img_hidden_class[h*CELL_LEN:(h+1)*CELL_LEN, 0:width*CELL_LEN] = targetCellTypeDict[key]
          img_hidden_class[(h+1)*CELL_LEN-1:(h+1)*CELL_LEN, 0:width*CELL_LEN] = CellTypeDict[type][1]
        else:
          img_hidden_class[h*CELL_LEN:(h+1)*CELL_LEN, 0:width*CELL_LEN] = CellTypeDict[type][1]
          img_hidden_class[(h+1)*CELL_LEN-1:(h+1)*CELL_LEN, 0:width*CELL_LEN] = BLACK
        h+=1

      if re == 0:
        continue

      img[h*CELL_LEN:(h+1)*CELL_LEN, 0:re*CELL_LEN] = CellTypeDict[type][1]
      img[(h+1)*CELL_LEN-1:(h+1)*CELL_LEN, 0:re*CELL_LEN] = BLACK
      img[h*CELL_LEN:(h+1)*CELL_LEN, re*CELL_LEN-1:re*CELL_LEN] = BLACK
      # hidden
      if key in targetCellTypeDict:
        img_hidden_class[h*CELL_LEN:(h+1)*CELL_LEN, 0:re*CELL_LEN] = targetCellTypeDict[key]
        img_hidden_class[(h+1)*CELL_LEN-1:(h+1)*CELL_LEN, 0:re*CELL_LEN] = CellTypeDict[type][1]
        img_hidden_class[h*CELL_LEN:(h+1)*CELL_LEN, re*CELL_LEN-1:re*CELL_LEN] = BLACK
      else:
        img_hidden_class[h*CELL_LEN:(h+1)*CELL_LEN, 0:re*CELL_LEN] = CellTypeDict[type][1]
        img_hidden_class[(h+1)*CELL_LEN-1:(h+1)*CELL_LEN, 0:re*CELL_LEN] = BLACK
        img_hidden_class[h*CELL_LEN:(h+1)*CELL_LEN, re*CELL_LEN-1:re*CELL_LEN] = BLACK

      h += 1

    # cv2.imwrite("{0}/{1}-hidden.png".format(save_path, title), img_hidden_class)
    cv2.imwrite("{0}/{1}.png".format(save_path, title), img)

  else:
    for type, byte, original_byte, _, hidden_class, data in snap_shot:
      key = get_key(type, hidden_class, byte)
      is_target = key in targetCellTypeDict

      if is_target:
        if key in base_dict:
          compression_bits = compress(base_dict[key], data)
          total_bits += compression_bits
          total_compression_bits += compression_bits
          compressed_bits = original_byte * 8 - compression_bits
          total_compressed_bits += compressed_bits
          if key[0] == -1: # hidden class
            hidden_class_compressed_bits += compressed_bits
            hidden_class_compression_bits += compression_bits
          else: # meta class
            meta_class_compressed_bits += compressed_bits
            meta_class_compression_bits += compression_bits
        else:
          base_dict[key] = data
          total_bits += 8 * divide16(original_byte)
          if is_hidden_class(type):
            hidden_class_compression_bits += 8 * divide16(original_byte)
          else:
            meta_class_compression_bits += 8 * divide16(original_byte)
      else:
        total_bits += 8 * divide16(original_byte)
        if is_hidden_class(type):
          hidden_class_compression_bits += 8 * divide16(original_byte)
        else:
          meta_class_compression_bits += 8 * divide16(original_byte)

  return total_bits // 8, \
    total_compression_bits // 8, \
    total_compressed_bits // 8,  \
    hidden_class_compression_bits // 8, \
    hidden_class_compressed_bits // 8, \
    meta_class_compression_bits // 8, \
    meta_class_compressed_bits // 8


path = "../awfy"
benchmark = sys.argv[1]
option = "GC"
if len(sys.argv) > 2:
  option = sys.argv[2]
al_snap_shots = read_file("{0}/{1}-alignment.txt".format(path, benchmark), option)
# snap_shots = read_file("{0}/{1}.txt".format(path, benchmark), option)
al_snap_shot_num = len(al_snap_shots)
# snap_shot_hum = len(snap_shots)
al_section = al_snap_shot_num // 10

# alignment
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
  = alignment_preprocessing(snap_shot, used_cs, detail=create_pic)

  # analyze
  al_save_pic_path = "./results/{0}/pic".format(benchmark)
  al_save_pic_title = "{0}-alignment{1}".format(benchmark, i+1)
  # result total bytes: 圧縮したもの圧縮できなかったものの合計
  result_total_bytes, \
  total_compression_bytes, \
  total_compressed_bytes,  \
  hidden_class_compression_bytes, \
  hidden_class_compressed_bytes, \
  meta_class_compression_bytes, \
  meta_class_compressed_bytes = \
  alignment_analyze(snap_shot, al_save_pic_title, alignment_height, targetCellTypeDict, al_save_pic_path, create_pic)

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


# def original_analyze(snap_shot, title, hiddenClassCellTypeDict, max_address, min_address, create_pic=True, color_pic_by_data=False):
#   width = 8
#   height = (max_address - min_address) // 64
#   img = np.zeros((height*CELL_LEN, width*CELL_LEN, 3), dtype=np.uint8)
#   img_hidden_class = np.zeros((height*CELL_LEN, width*CELL_LEN, 3), dtype=np.uint8)

#   for byte, type, address, hidden_class, _ in snap_shot:
#     relative_address = address - min_address
#     id = relative_address // 8
#     blocks = byte // 8 # 8 byte blockの個数
#     key = get_key(type, hidden_class, byte)
#     for i in range(blocks):
#       h, w = (id+i) // width, (id+i) % width
#       img[h*CELL_LEN:(h+1)*CELL_LEN, w*CELL_LEN:(w+1)*CELL_LEN] = CellTypeDict[type][1]
#       img[(h+1)*CELL_LEN-1:(h+1)*CELL_LEN, w*CELL_LEN:(w+1)*CELL_LEN] = BLACK
#       # hidden class
#       if key in hiddenClassCellTypeDict:
#         img_hidden_class[h*CELL_LEN:(h+1)*CELL_LEN, w*CELL_LEN:(w+1)*CELL_LEN] = hiddenClassCellTypeDict[key]
#         img_hidden_class[(h+1)*CELL_LEN-1:(h+1)*CELL_LEN, w*CELL_LEN:(w+1)*CELL_LEN] = CellTypeDict[type][1]
#       else:
#         img_hidden_class[h*CELL_LEN:(h+1)*CELL_LEN, w*CELL_LEN:(w+1)*CELL_LEN] = CellTypeDict[type][1]
#         img_hidden_class[(h+1)*CELL_LEN-1:(h+1)*CELL_LEN, w*CELL_LEN:(w+1)*CELL_LEN] = BLACK

#   cache_lines = height
#   print("original cache line: {0}".format(cache_lines))
#   cv2.imwrite("{0}_hidden.png".format(title), img_hidden_class)
#   cv2.imwrite("{0}.png".format(title), img)
