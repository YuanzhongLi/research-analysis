from utils import calc_percent, b2kb
from cell_types import CellTypeDict

def print_total(total_bytes, total_types):
  print("TOTAL B KB TYPES")
  print(total_bytes, b2kb(total_bytes), total_types)

def print_compress_target(compress_target_bytes, total_bytes, compress_target_types):
  print("COMPRESS_TARGET B KB % TYPES")
  print(compress_target_bytes, b2kb(compress_target_bytes), calc_percent(compress_target_bytes, total_bytes), compress_target_types)

def print_compress_hidden_target(compress_hidden_class_target_types, total_bytes, compress_hidden_class_target_bytes):
  print("COMPRESS_HIDDEN_TARGET B KB % TYPES")
  print(compress_hidden_class_target_bytes, b2kb(compress_hidden_class_target_bytes), calc_percent(compress_hidden_class_target_bytes, total_bytes), compress_hidden_class_target_types)

def print_compress_meta_target(compress_meta_class_target_types, total_bytes, compress_meta_class_target_bytes):
  print("COMPRESS_HIDDEN_TARGET B KB % TYPES")
  print(compress_meta_class_target_bytes, b2kb(compress_meta_class_target_bytes), calc_percent(compress_meta_class_target_bytes, total_bytes), compress_meta_class_target_types)

def print_objects(object_nums, object_bytes, total_bytes):
  print("OBJECTS {0} TYPE COUNT B KB %".format(len(CellTypeDict.items())))
  for key, val in CellTypeDict.items():
    print(val[0], object_nums[key], object_bytes[key], b2kb(object_bytes[key]), calc_percent(object_bytes[key], total_bytes))

def print_target_objects(dict):
  print("TARGET_OBJECTS CLASS KEY COUNT B KB")
  for key, val in dict.items():
    if (val[0] > 1):
      if key[0] == -1: # hidden class
        print("HIDDEN", format(key[1], '08x'), val[0], val[1], b2kb(val[1]))
      else: # meta class
        print("META", "{0}-{1}".format(key[0], key[1]), val[0], val[1], b2kb(val[1]))

# compressed bytes: どれくらい減ったか
# compressioin bytes: どれくらいになったか
# compressed bytes + compression bytes = 元のサイズ
def print_compression_results(total_compressed_bytes, hidden_class_compressed_bytes, hidden_class_bytes, meta_class_compressed_bytes, meta_class_bytes, total_bytes):
  print("TOTAL_COMPRESSED B KB %")
  print(total_compressed_bytes, b2kb(total_compressed_bytes), calc_percent(total_compressed_bytes, total_bytes))

  # 最後のはhidden class内でどれだけcompressedされたかの割合
  print("HIDDEN_COMPRESSED B KB % %")
  print(hidden_class_compressed_bytes, b2kb(hidden_class_compressed_bytes), calc_percent(hidden_class_compressed_bytes, total_bytes), calc_percent(hidden_class_compressed_bytes, hidden_class_bytes))

  # 最後のはmeta class以下同文
  print("META_COMPRESSED B KB % %")
  print(meta_class_compressed_bytes, b2kb(meta_class_compressed_bytes), calc_percent(meta_class_compressed_bytes, total_bytes), calc_percent(meta_class_compressed_bytes, meta_class_bytes))
