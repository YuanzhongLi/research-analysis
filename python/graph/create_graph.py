import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from read_file import read_file, getResultPath

ANALYSIS_PYTHON_RESULTS = os.environ["ANALYSIS_PYTHON_RESULTS"]

def create_OBD_line_graph(byte_data, compression_ratio_data, xlabel, graph_path, dump="GC"):
  x_size =  byte_data.shape[0]

  # byte line graph
  total_bytes = byte_data[:, 0]
  virtual_total_bytes = byte_data[:, 1]
  virtual_hidden_bytes = byte_data[:, 2]
  virtula_meta_bytes = byte_data[:, 3]
  total_hidden_bytes = byte_data[:, 4]
  total_meta_bytes = byte_data[:, 5]
  total_compress_bytes = byte_data[:, 6]
  hidden_compress_bytes = byte_data[:, 7]
  meta_compress_bytes = byte_data[:, 8]
  x = np.arange(1, x_size+1)

  max_bytes = np.max(total_bytes) + 1000

  # (label, color)
  lc1,lc2,lc3,lc4,lc5,lc6,lc7,lc8,lc9 = \
    ("total", "black"), \
    ("virtual_total", ""), \
    ("virtual_hidden", ""), \
    ("virtula_meta", ""), \
    ("total_hidden", ""), \
    ("total_meta", ""), \
    ("total_compress", "blue"), \
    ("hidden_compress", "red"), \
    ("meta_compress", "green")


  fig, ax = plt.subplots()
  plt.gca().get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True)) # x軸を整数にする
  ax.set_xlabel(xlabel)
  ax.set_ylabel("Byte")
  # ax.set_title()
  ax.grid()
  #ax.set_xlim([1, x_size])
  ax.set_ylim([0, max_bytes])
  ax.plot(x, total_bytes, label=lc1[0], color=lc1[1])
  ax.plot(x, total_compress_bytes, label=lc7[0], color=lc7[1])
  ax.plot(x, hidden_compress_bytes, label=lc8[0], color=lc8[1])
  ax.plot(x, meta_compress_bytes, label=lc9[0], color=lc9[1])
  ax.legend(loc=0)    # 凡例
  fig.tight_layout()  # レイアウトの設定
  plt.savefig("{0}/byte-line-OBD-{1}.png".format(graph_path, dump)) # 画像の保存

  # ratio line graph
  total_combress_ratio = compression_ratio_data[:, 5]
  hidden_compress_ratio = compression_ratio_data[:, 6]
  meta_compress_ratio = compression_ratio_data[:, 7]
  x = np.arange(1, x_size+1)

  fig, ax = plt.subplots()
  plt.gca().get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True)) # x軸を整数にする
  ax.set_xlabel(xlabel)
  ax.set_ylabel("%")
  # ax.set_title()
  ax.grid()
  #ax.set_xlim([1, x_size])
  ax.set_ylim([0, 100])
  ax.plot(x, total_combress_ratio, label=lc7[0], color=lc7[1])
  ax.plot(x, hidden_compress_ratio, label=lc8[0], color=lc8[1])
  ax.plot(x, meta_compress_ratio, label=lc9[0], color=lc9[1])
  ax.legend(loc=0)    # 凡例
  fig.tight_layout()  # レイアウトの設定
  plt.savefig("{0}/ratio-line-OBD-{1}.png".format(graph_path, dump))

# byte_data, compression_ratio_data = read_file("results/Bounce-small/Bounce-small-analysis.txt")
# create_line_graph(byte_data, compression_ratio_data, "GC", "results/Bounce-small/pic")

def create_BCD_line_graph(byte_data, compression_ratio_data, xlabel, graph_path, dump="GC", alignment = False, top=0):
  x_size =  byte_data.shape[0]

  # byte line graph
  total_bytes = byte_data[:, 0]
  virtual_total_bytes = byte_data[:, 1]
  total_compress_bytes = byte_data[:, 2]
  x = np.arange(1, x_size+1)

  max_bytes = np.max(total_bytes) + 1000

  # (label, color)
  lc1,lc2,lc3 = \
    ("total", "black"), \
    ("virtual_total", ""), \
    ("total_compress", "blue"), \

  fig, ax = plt.subplots()
  plt.gca().get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True)) # x軸を整数にする
  ax.set_xlabel(xlabel)
  ax.set_ylabel("Byte")
  # ax.set_title()
  ax.grid()
  #ax.set_xlim([1, x_size])
  ax.set_ylim([0, max_bytes])
  ax.plot(x, total_bytes, label=lc1[0], color=lc1[1])
  ax.plot(x, total_compress_bytes, label=lc3[0], color=lc3[1])
  ax.legend(loc=0)    # 凡例
  fig.tight_layout()  # レイアウトの設定
  if alignment:
    if top == 0:
      plt.savefig("{0}/byte-line-BCDAL-{1}.png".format(graph_path, dump)) # 画像の保存
    else:
      plt.savefig("{0}/byte-line-BCDAL-{1}-{2}.png".format(graph_path, dump, top)) # 画像の保存
  else:
    plt.savefig("{0}/byte-line-BCD-{1}.png".format(graph_path, dump)) # 画像の保存

  # ratio line graph
  total_combress_ratio = compression_ratio_data[:, 1]
  x = np.arange(1, x_size+1)

  fig, ax = plt.subplots()
  plt.gca().get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True)) # x軸を整数にする
  ax.set_xlabel(xlabel)
  ax.set_ylabel("%")
  # ax.set_title()
  ax.grid()
  #ax.set_xlim([1, x_size])
  ax.set_ylim([0, 130])
  ax.plot(x, total_combress_ratio, label=lc3[0], color=lc3[1])
  ax.legend(loc=0)    # 凡例
  fig.tight_layout()  # レイアウトの設定
  if alignment:
    if top == 0:
      plt.savefig("{0}/ratio-line-BCDAL-{1}.png".format(graph_path, dump)) # 画像の保存
    else:
      plt.savefig("{0}/ratio-line-BCDAL-{1}-{2}.png".format(graph_path, dump, top)) # 画像の保存
  else:
    plt.savefig("{0}/ratio-line-BCD-{1}.png".format(graph_path, dump)) # 画像の保存

# byte_data, compression_ratio_data = read_file("results/Bounce-small/Bounce-small-BCD-alignment-analysis.txt")
# create_BCD_line_graph(byte_data, compression_ratio_data, "GC", "results/Bounce-small/pic", "GC", True)

def create_bar_graph(
  OBD_average_ratio,
  BCD_average_ratio,
  BCDAL_average_ratio,
  BCDAL1_average_ratio,
  BCDAL2_average_ratio,
  BCDAL3_average_ratio,
  BCDAL4_average_ratio,
  BCDAL5_average_ratio,
  BCDAL6_average_ratio,
  graph_path,
  benchmark,
  dump
):
  original_hidden = OBD_average_ratio[3]
  original_meta = OBD_average_ratio[4]
  virtual_hidden = OBD_average_ratio[1]
  virtual_meta = OBD_average_ratio[2]
  compress_hidden = OBD_average_ratio[6]
  compress_meta = OBD_average_ratio[7]
  BCD = BCD_average_ratio[1]
  BCDAL = BCDAL_average_ratio[1]
  BCDAL1 = BCDAL1_average_ratio[1]
  BCDAL2 = BCDAL2_average_ratio[1]
  BCDAL3 = BCDAL3_average_ratio[1]
  BCDAL4 = BCDAL4_average_ratio[1]
  BCDAL5 = BCDAL5_average_ratio[1]
  BCDAL6 = BCDAL6_average_ratio[1]

  BCDALs = [BCDAL, BCDAL1, BCDAL2, BCDAL3, BCDAL4, BCDAL5, BCDAL6]
  best_BCD = BCDAL
  best_i = 0
  for i in range(len(BCDALs)):
    if BCDALs[i] < best_BCD:
      best_BCD = BCDALs[i]
      best_i = i

  left = np.arange(1, 6 + 6)
  data = np.zeros((3, 5 + 6))
  data[0][0], data[0][1], data[0][2] = original_hidden, virtual_hidden, compress_hidden
  data[1][0], data[1][1], data[1][2] = original_meta, virtual_meta, compress_meta
  data[2][3], data[2][4], data[2][5], data[2][6], data[2][7], data[2][8], data[2][9], data[2][10] = \
  BCD, BCDAL, BCDAL1, BCDAL2, BCDAL3, BCDAL4, BCDAL5, BCDAL6

  labels = [
    "original",
    "virtual",
    "OBD",
    "BCD",
    "BCDAL",
    "BCDAL1",
    "BCDAL2",
    "BCDAL3",
    "BCDAL4",
    "BCDAL5",
    "BCDAL6",
  ]
  hatch_list = ["//", "\\\\", "---"]

  fig = plt.figure()
  ax = fig.add_subplot(111)
  for i in range(data.shape[0]):
      plt.bar(left, data[i],
              bottom = np.sum(data[:i], axis = 0),
              width=0.5, edgecolor='k', linewidth=1,
              tick_label=labels, hatch=hatch_list[i % len(hatch_list)])
  plt.title("{0}-{1} ratio".format(benchmark.replace("-small", ""), dump))
  plt.xlabel("Method")
  plt.ylabel("%")
  ax.set_ylim([0, 200])
  ax.grid()
  ax.legend(["javascript object class", "meta class", "BCD"], loc='upper left', bbox_to_anchor=(0, -0.3), fontsize="small")
  fig.tight_layout()
  plt.xticks(rotation=270)
  plt.subplots_adjust(bottom=0.35)
  plt.savefig("{0}/compare-ratio-{1}.png".format(graph_path, dump))

  return original_hidden, original_meta, compress_hidden, compress_meta, BCD, best_BCD, best_i

def create_bar_graph_all(
  original_hiddens,
  original_metas,
  compress_hiddens,
  compress_metas,
  BCDs,
  best_BCDs,
  best_is,
  benchmarks,
  graph_path,
  dump
):


  left = np.arange(1, 4 * len(benchmarks) + 1)
  data = np.zeros((3, 4 * len(benchmarks)))
  labels = []

  for i, benchmark in enumerate(benchmarks):
    data[0][i*4] = original_hiddens[i]
    data[1][i*4] = original_metas[i]
    data[0][i*4+1] = compress_hiddens[i]
    data[1][i*4+1] = compress_metas[i]
    data[2][i*4+2] = BCDs[i]
    data[2][i*4+3] = best_BCDs[i]

    labels.append("{0}".format(benchmark.replace("-small", "")))
    labels.append("{0}-OBD".format(benchmark.replace("-small", "")))
    labels.append("{0}-BCD".format(benchmark.replace("-small", "")))
    BCD_type = "BCD"
    best_i = best_is[i]
    if best_i == 0:
      BCD_type = "BCDAL"
    elif best_i > 0:
      BCD_type = "BCDAL{0}".format(best_i)
    labels.append("{0}-{1}".format(benchmark.replace("-small", ""), BCD_type))

  hatch_list = ["//", "\\\\", "---"]

  fig = plt.figure()
  ax = fig.add_subplot()
  for i in range(data.shape[0]):
      plt.bar(left, data[i],
              bottom = np.sum(data[:i], axis = 0),
              width=0.5, edgecolor='k', linewidth=0.8,
              tick_label=labels, hatch=hatch_list[i % len(hatch_list)])
  plt.title("Benchmark-{0} ratio".format(dump))
  plt.xlabel("Benchmark")
  plt.ylabel("%")
  ax.set_ylim([0, 110])
  ax.grid()
  ax.legend(["javascript object class", "meta class", "BCD"], loc='upper left', borderaxespad=0, bbox_to_anchor=(0, -0.7), fontsize="small")
  fig.tight_layout()
  plt.xticks(rotation=270)
  plt.subplots_adjust(bottom=0.48)
  plt.savefig("{0}/Benchmark-ratio-{1}.png".format(graph_path, dump))

  # average
  left = np.arange(1, 5)
  data = np.zeros((3, 4))
  data[0][0] = np.average(original_hiddens)
  data[1][0] = np.average(original_metas)
  data[0][1] = np.average(compress_hiddens)
  data[1][1] = np.average(compress_metas)
  data[2][2] = np.average(BCDs)
  data[2][3] = np.average(best_BCDs)
  labels = ["original", "OBD", "BCD", "BEST BCD"]

  fig = plt.figure()
  ax = fig.add_subplot()
  for i in range(data.shape[0]):
      plt.bar(left, data[i],
              bottom = np.sum(data[:i], axis = 0),
              width=0.5, edgecolor='k', linewidth=0.8,
              tick_label=labels, hatch=hatch_list[i % len(hatch_list)])
  plt.title("Average-{0} ratio".format(dump))
  plt.xlabel("Method")
  plt.ylabel("%")
  ax.set_ylim([0, 110])
  ax.grid()
  ax.legend(["javascript object class", "meta class", "BCD"], loc='upper left', borderaxespad=0, bbox_to_anchor=(0, -0.3), fontsize="small")
  fig.tight_layout()
  plt.xticks(rotation=270)
  plt.subplots_adjust(bottom=0.4)
  plt.savefig("{0}/Average-ratio-{1}.png".format(graph_path, dump))
