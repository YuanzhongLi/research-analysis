import os

from cell_types import is_hidden_class
from LZC_algorithm import compress
from preprocessing import get_key
from utils import divide16

AWFY = os.environ["AWFY"]
CELL_LEN = 8
INF = (1<<63) - 1

# method: ["NOR", "OBD", "BCD"]
# dump: ["GC", "100K"]
def getOutputPath(benchmark, method, dump):
  return "{0}/{1}/output/{1}-{2}-{3}.txt".format(AWFY, benchmark, method, dump)

# OBDとBCDALに使用する
def alignment_analyze(
  snap_shot,
  targetCellTypeDict
):
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
