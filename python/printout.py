from utils import calc_percent, b2kb
from cell_types import CellTypeDict

def print_total(total_types, total_bytes):
  print("TOTAL TYPES B KB")
  print(total_types, total_bytes, b2kb(total_bytes))

def print_virtual_total(virtual_total_bytes, original_total_bytes):
  print("VIRTUAL_TOTAL B KB %")
  print(
    virtual_total_bytes,
    b2kb(virtual_total_bytes),
    calc_percent(virtual_total_bytes, original_total_bytes)
  )

def print_virtual_hidden(hidden_class_bytes, original_total_bytes, virtual_total_bytes):
  print("VIRTUAL_HIDDEN B KB % %")
  print(
    hidden_class_bytes,
    b2kb(hidden_class_bytes),
    calc_percent(hidden_class_bytes, original_total_bytes),
    calc_percent(hidden_class_bytes, virtual_total_bytes)
  )

def print_virtual_meta(meta_class_bytes, original_total_bytes, virtual_total_bytes):
  print("VIRTUAL_META B KB % %")
  print(
    meta_class_bytes,
    b2kb(meta_class_bytes),
    calc_percent(meta_class_bytes, original_total_bytes),
    calc_percent(meta_class_bytes, virtual_total_bytes)
  )

def print_hidden_total(original_hidden_class_bytes, original_total_bytes):
  print("HIDDEN_TOTAL B KB %")
  print(
    original_hidden_class_bytes,
    b2kb(original_hidden_class_bytes),
    calc_percent(original_hidden_class_bytes, original_total_bytes)
  )

def print_meta_total(original_meta_class_bytes, original_total_bytes):
  print("META_TOTAL B KB")
  print(
    original_meta_class_bytes,
    b2kb(original_meta_class_bytes),
    calc_percent(original_meta_class_bytes, original_total_bytes)
  )

def print_compress_target(
  compress_target_types,
  original_compress_target_bytes,
  original_total_bytes
):
  print("COMPRESS_TARGET TYPES B KB %")
  print(
    compress_target_types,
    original_compress_target_bytes,
    b2kb(original_compress_target_bytes),
    calc_percent(original_compress_target_bytes, original_total_bytes)
  )

def print_compress_hidden_target(
  compress_hidden_class_target_types,
  original_compress_hidden_class_target_bytes,
  original_total_bytes
):
  print("COMPRESS_HIDDEN_TARGET TYPES B KB %")
  print(
    compress_hidden_class_target_types,
    original_compress_hidden_class_target_bytes,
    b2kb(original_compress_hidden_class_target_bytes),
    calc_percent(original_compress_hidden_class_target_bytes, original_total_bytes),
  )

def print_compress_meta_target(
  compress_meta_class_target_types,
  original_compress_meta_class_target_bytes,
  original_total_bytes
):
  print("COMPRESS_HIDDEN_TARGET TYPES B KB %")
  print(
    compress_meta_class_target_types,
    original_compress_meta_class_target_bytes,
    b2kb(original_compress_meta_class_target_bytes),
    calc_percent(original_compress_meta_class_target_bytes, original_total_bytes)
  )

def print_objects(object_nums, original_object_bytes, original_total_bytes):
  print("OBJECTS {0} TYPE COUNT B KB %".format(len(CellTypeDict.items())))
  for key, val in CellTypeDict.items():
    print(
      val[0],
      object_nums[key],
      original_object_bytes[key],
      b2kb(original_object_bytes[key]),
      calc_percent(original_object_bytes[key], original_total_bytes)
    )

def print_target_objects(dict):
  print("TARGET_OBJECTS CLASS KEY COUNT B KB")
  for key, val in dict.items():
    if (val[0] > 1):
      if key[0] == -1: # hidden class
        print(
          "HIDDEN",
          format(key[1], '08x'),
          val[0],
          val[2],
          b2kb(val[2])
        )
      else: # meta class
        print(
          "META",
          "{0}-{1}".format(key[0], key[1]),
          val[0],
          val[2],
          b2kb(val[2])
        )

# compressed bytes: どれくらい減ったか
# compressioin bytes: どれくらいになったか
# compressed bytes + compression bytes = 元のサイズ
def print_compression_results(
  result_total_bytes,
  total_compression_bytes,
  hidden_class_compression_bytes,
  meta_class_compression_bytes,
  original_total_bytes,
  original_hidden_class_bytes,
  original_meta_class_bytes,
):
  print("TOTAL_COMPRESSION B KB % B")
  print(
    result_total_bytes,
    b2kb(result_total_bytes),
    calc_percent(result_total_bytes, original_total_bytes),
    total_compression_bytes
  )

  # 最後のはhidden class内でどれだけcompressionされたかの割合
  print("HIDDEN_COMPRESSION B KB % %")
  print(
    hidden_class_compression_bytes,
    b2kb(hidden_class_compression_bytes),
    calc_percent(hidden_class_compression_bytes, original_total_bytes),
    calc_percent(hidden_class_compression_bytes, original_hidden_class_bytes)
  )

  # 最後のはmeta class以下同文
  print("META_COMPRESSION B KB % %")
  print(
    meta_class_compression_bytes,
    b2kb(meta_class_compression_bytes), calc_percent(meta_class_compression_bytes, original_total_bytes),
    calc_percent(meta_class_compression_bytes, original_meta_class_bytes)
  )
