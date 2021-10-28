from math import floor
from random import randint

from cell_types import is_hidden_class, num2color
from utils import get_key
from printout import print_total, print_compress_target, print_compress_hidden_target, print_compress_meta_target, print_objects, print_target_objects

INF = (1<<63) - 1

def alignment_preprocessing(snap_shot, USED_COLORS, detail=True):
  total_bytes = 0
  original_total_bytes = 0
  hidden_class_bytes = 0
  original_hidden_class_bytes = 0
  meta_class_bytes = 0
  original_meta_class_bytes = 0

  dict = {}
  object_nums = [0 for _ in range(33)]
  object_bytes = [0 for _ in range(33)]
  original_object_bytes = [0 for _ in range(33)]

  # alignment
  alignment_height = 0

  for type, byte, original_byte, _, hidden_class, _ in snap_shot:
    total_bytes += byte
    original_total_bytes += original_byte
    object_nums[type] += 1
    object_bytes[type] += byte
    original_object_bytes[type] += original_byte
    key = get_key(type, hidden_class, byte)
    if is_hidden_class(type):
      hidden_class_bytes += byte
      original_hidden_class_bytes += original_byte
    else:
      meta_class_bytes += byte
      original_meta_class_bytes += original_byte
    if key not in dict:
      dict[key] = [0, 0, 0]
    dict[key][0] += 1
    dict[key][1] += byte
    dict[key][2] += original_byte

    # alignment
    alignment_height += (byte + 63) // 64

  total_types = 0
  compress_target_types = 0
  compress_hidden_class_target_types = 0
  compress_meta_class_target_types = 0
  compress_target_bytes = 0
  original_compress_target_bytes = 0
  compress_hidden_class_target_bytes = 0
  original_compress_hidden_class_target_bytes = 0
  compress_meta_class_target_bytes = 0
  original_compress_meta_class_target_bytes = 0

  for key, val in dict.items():
    total_types += 1
    if val[0] > 1:
      compress_target_types += 1
      compress_target_bytes += val[1]
      original_compress_target_bytes += val[2]
      if key[0] == -1: # hidden class
        compress_hidden_class_target_types += 1
        compress_hidden_class_target_bytes += val[1]
        original_compress_hidden_class_target_bytes += val[2]
      else: # meta class
        compress_meta_class_target_types += 1
        compress_meta_class_target_bytes += val[1]
        original_compress_meta_class_target_bytes += val[2]

  # colors
  additional_color_candidates = min(max(5, floor(compress_target_types * 1.5)), (1<<23)-1)
  C = (1<<24)-1
  inc = (C+1)//additional_color_candidates
  Cs = []
  for i in range(inc, C+1, inc):
    if i > C: break
    if i not in USED_COLORS:
      Cs.append(num2color(i))
  additional_colors = len(Cs)
  idx = 0
  targetCellTypeDict = {}
  for key, val in dict.items():
    if val[0] > 1:
      if (idx >= additional_colors):
        while True:
          x = randint(0, (1<<24)-1)
          if x not in USED_COLORS:
            USED_COLORS.add(x)
            c = num2color(x)
            targetCellTypeDict[key] = c
            break
      else:
        targetCellTypeDict[key] = Cs[idx]
        idx += 1

  print_total(total_types, original_total_bytes)
  print_compress_target(
    compress_target_types,
    original_compress_target_bytes,
    original_total_bytes
  )
  print_compress_hidden_target(
    compress_hidden_class_target_types,
    original_compress_hidden_class_target_bytes,
    original_total_bytes
  )
  print_compress_meta_target(
    compress_meta_class_target_types,
    original_compress_meta_class_target_bytes,
    original_total_bytes,
  )

  if detail:
    print_objects(object_nums, original_object_bytes, original_total_bytes)
    print_target_objects(dict)

  return original_total_bytes, original_hidden_class_bytes, \
  original_meta_class_bytes, \
  dict, targetCellTypeDict, alignment_height

# alignmentで行なっている処理は省略
# def original_preprocessing(snap_shot):
#   total_bytes = 0
#   object_nums = [0 for _ in range(33)]
#   object_bytes = [0 for _ in range(33)]

#   # original
#   min_address = INF
#   max_address = -INF

#   for byte, type, address, _, _ in snap_shot:
#     total_bytes += byte
#     object_nums[type] += 1
#     object_bytes[type] += byte

#     # original
#     min_address = min((min_address // 64) * 64, address)
#     max_address = max(max_address, (address + byte + 63)// 64 * 64)

#   print("total byte: {0} ({1} KB)".format(total_bytes, floor(total_bytes / 1024 * 100) / 100))
#   return min_address, max_address, total_bytes



# def getDict(snap_shot):
#   total_bytes = 0
#   dict = {}
#   object_nums = [0 for _ in range(33)]
#   object_bytes = [0 for _ in range(33)]

#   # original
#   min_address = INF
#   max_address = -INF

#   # alignment
#   alignment_height = 0

#   for byte, type, address, hidden_class, _ in snap_shot:
#     total_bytes += byte
#     object_nums[type] += 1
#     object_bytes[type] += byte
#     if is_hidden_class(type):
#       key = (hidden_class)
#       if key not in dict:
#         dict[key] = [0, 0]
#       dict[key][0] += 1
#       dict[key][1] += byte
#     else:
#       key = ()

#     # original
#     min_address = min((min_address // 64) * 64, address)
#     max_address = max(max_address, (address + byte + 63)// 64 * 64)

#     # alignment
#     alignment_height += (byte + 63) // 64

#   compress_types = 0
#   compress_target_bytes = 0
#   for key, val in dict.items():
#     if val[0] > 1:
#       compress_types += 1
#       compress_target_bytes += val[1]

#   additional_color_candidates = min(max(5, floor(compress_types * 1.5)), (1<<23)-1)
#   C = (1<<24)-1
#   inc = (C+1)//additional_color_candidates
#   Cs = []
#   for i in range(inc, C+1, inc):
#     if i > C: break
#     if i not in USED_COLORS:
#       Cs.append(num2color(i))
#   additional_colors = len(Cs)
#   idx = 0
#   hiddenClassCellTypeDict = {}
#   for key, val in dict.items():
#     if val[0] > 1:
#       if (idx >= additional_colors):
#         while True:
#           x = randint(0, (1<<24)-1)
#           if x not in USED_COLORS:
#             USED_COLORS.add(x)
#             c = num2color(x)
#             hiddenClassCellTypeDict[key] = c
#             break
#       else:
#         hiddenClassCellTypeDict[key] = Cs[idx]
#         idx += 1

#   print("total byte: {0} ({1} KB)".format(total_bytes, floor(total_bytes / 1024 * 100) / 100))
#   for key, val in CellTypeDict.items():
#     print("object type: {0}, count: {1}, byte: {2}".format(val[0], object_nums[key], object_bytes[key]))
#   print("compress types: {0}".format(compress_types))
#   if (total_bytes == 0):
#     print("compress target bytes: {0} ({1} KB, {2}%)".format(compress_target_bytes, floor(compress_target_bytes/1024 * 100)/100, 0))
#   else:
#     print("compress target bytes: {0} ({1} KB, {2}%)".format(compress_target_bytes, floor(compress_target_bytes/1024 * 100)/100, floor(compress_target_bytes/total_bytes*10000)/100))
#   for key, val in dict.items():
#     if (val[0] > 1):
#       print(key, val)
#   return dict, total_bytes, compress_types, hiddenClassCellTypeDict, min_address, max_address, alignment_height
