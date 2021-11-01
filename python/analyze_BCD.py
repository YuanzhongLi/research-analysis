import sys

from ReadFile import read_BCD_file
from LZC_algorithm import compress_48byte, extract_upper_16byte
from printout import print_total, print_virtual_total
from utils import calc_percent, b2kb, divide16

path = "../awfy"
benchmark = sys.argv[1]

option = "BCDGC"
if (len(sys.argv) > 2):
  option = sys.argv[2]
type = "normal"
if (len(sys.argv) > 3):
  type = sys.argv[3]

snap_shots = None
if type == "normal":
  snap_shots = read_BCD_file("{0}/{1}-BCD.txt".format(path, benchmark), option)
elif type == "alignment":
  snap_shots = read_BCD_file("{0}/{1}-alignment.txt".format(path, benchmark), option, type="alignment")


def BCD_analyze(snap_shot):
  virtual_total_bytes = len(snap_shot) * 64
  total_bytes = 0
  compress_target_types = 0
  compress_target_bytes = 0
  dict = {}
  for original_byte, block in snap_shot:
    total_bytes += original_byte
    key = extract_upper_16byte(block)
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

  for original_byte, block in snap_shot:
    key = extract_upper_16byte(block)
    if key in base_dict:
      compression_bits = compress_48byte(base_dict[key], block)
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


for i, snap_shot in enumerate(snap_shots):
  print("===== start {0} =====".format(i+1))
  BCD_analyze(snap_shot)
  print("===== end {0} =====".format(i+1))
  print()
