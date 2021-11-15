import sys

from ReadFile import read_BCD_file, read_file
from LZC_algorithm import compress_48byte, extract_upper_16byte, extract16byte
from printout import print_total, print_virtual_total
from create_memory_picture import create_pic_original
from utils import calc_percent, b2kb, divide16
from analyze import getOutputPath
from preprocessing import original_preprocessing


benchmark = sys.argv[1]
dump = "GC"
if (len(sys.argv) > 2):
  dump = sys.argv[2]
type = "NOR"
if (len(sys.argv) > 3):
  type = sys.argv[3]
top=0
if (len(sys.argv) > 4):
  top = int(sys.argv[4])

snapshots = None
if type == "NOR":
  snapshots = read_BCD_file(getOutputPath(benchmark, "BCD", dump), dump, type)
elif type == "AL":
  # alignmentではOBDと同じファイルを使用
  snapshots = read_BCD_file(getOutputPath(benchmark, "OBD", dump), dump, type)

snapshots_NOR = read_file(getOutputPath(benchmark, "NOR", dump), dump)
snapshot_NOR_num = len(snapshots_NOR)
section = snapshot_NOR_num // 10

#TODO BCD_NORで通常のmemory picを作成を
def BCD_analyze(snapshot, top):
  virtual_total_bytes = len(snapshot) * 64
  total_bytes = 0
  compress_target_types = 0
  compress_target_bytes = 0
  dict = {}

  #
  for original_byte, block in snapshot:
    total_bytes += original_byte
    key = extract16byte(block, top)
    if key not in dict:
      dict[key] = [0, 0, block]
    dict[key][0] += 1
    dict[key][1] += 64

  base_dict = {}
  for key, val in dict.items():
    if val[0] > 1:
      compress_target_types += 1
      compress_target_bytes += dict[key][1]
      base_dict[key] = val[2]

  total_bits = 0
  total_compression_bits = 0

  for original_byte, block in snapshot:
    key = extract_upper_16byte(block)
    if key in base_dict:
      compression_bits = compress_48byte(base_dict[key], block, top)
      total_bits += compression_bits
      total_compression_bits += compression_bits
    else:
      total_bits += 8 * divide16(original_byte)

  # 圧縮したものできなかったもの全部含む結果
  result_total_bytes = total_bits // 8
  total_compression_bytes = total_compression_bits // 8

  print_total(-1, total_bytes)
  print_virtual_total(virtual_total_bytes, total_bytes)

  print("TOTAL_ENTRYES COUNT")
  print(len(dict))

  print("COMPRESS_TARGET ENTRYES B KB %")
  print(
    compress_target_types,
    compress_target_bytes,
    b2kb(compress_target_bytes),
    calc_percent(compress_target_bytes, total_bytes)
  )

  if __debug__:
    print("TARGET_ENTRYES KEY COUNT B KB")
    for key in base_dict:
      print(key, dict[key][0], dict[key][1], b2kb(dict[key][1]))

  print("TOTAL_COMPRESSION B KB % B")
  print(
    result_total_bytes,
    b2kb(result_total_bytes),
    calc_percent(result_total_bytes, total_bytes),
    total_compression_bytes
  )


for i, snapshot in enumerate(snapshots):
  create_pic = True
  if i >= 10 and i % section != 0 and i < snapshot_NOR_num-10:
    create_pic = False

  print("===== start {0} =====".format(i+1))
  BCD_analyze(snapshot, top)
  print("===== end {0} =====".format(i+1))
  print()

  # create memory pic
  if create_pic:
    title = "{0}-{1}".format(dump, i+1)
    min_address, max_address = original_preprocessing(snapshots_NOR[i])
    create_pic_original(min_address, max_address, benchmark, snapshots_NOR[i], None, title)
