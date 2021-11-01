import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from numpy.lib.function_base import average

from read_file import read_file

def create_line_graph(byte_data, compression_ratio_data, xlabel, graph_path, dump="GC"):
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
  plt.savefig("{0}/byte-line-{1}.png".format(graph_path, dump)) # 画像の保存

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
  plt.savefig("{0}/ratio-line-{1}.png".format(graph_path, dump))

# byte_data, compression_ratio_data = read_file("results/Bounce-small/Bounce-small-analysis.txt")
# create_line_graph(byte_data, compression_ratio_data, "GC", "results/Bounce-small/pic")

def create_BCD_line_graph(byte_data, compression_ratio_data, xlabel, graph_path, dump="GC", alignment = False):
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
    plt.savefig("{0}/byte-line-BCD-alignment-{1}.png".format(graph_path, dump)) # 画像の保存
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
    plt.savefig("{0}/ratio-line-BCD-alignment-{1}.png".format(graph_path, dump)) # 画像の保存
  else:
    plt.savefig("{0}/ratio-line-BCD-{1}.png".format(graph_path, dump)) # 画像の保存

# byte_data, compression_ratio_data = read_file("results/Bounce-small/Bounce-small-BCD-alignment-analysis.txt")
# create_BCD_line_graph(byte_data, compression_ratio_data, "GC", "results/Bounce-small/pic", "GC", True)

path = "./results"
benchmarks = [
  "Bounce-small",
  "CD-dyn-small",
  "CD-small",
  "Mandelbrot-small",
  "NBody-small",
  "Queens-small",
  "Richards-small",
  "Sieve-small",
  "Storage-small"
]

def create_bar_graph(
  average_ratio,
  BCD_average_ratio,
  BCD_al_average_ratio,
  graph_path,
  benchmark
):
  print(average_ratio)
  print(BCD_average_ratio)
  print(BCD_al_average_ratio)
  original_hidden = average_ratio[3]
  original_meta = average_ratio[4]
  virtual_hidden = average_ratio[1]
  virtual_meta = average_ratio[2]
  compress_hidden = average_ratio[6]
  compress_meta = average_ratio[7]
  BCD = BCD_average_ratio[1]
  BCD_al = BCD_al_average_ratio[1]

  left = np.arange(1, 6)
  data = np.zeros((3, 5))
  data[0][0], data[0][1], data[0][2] = original_hidden, virtual_hidden, compress_hidden
  data[1][0], data[1][1], data[1][2] = original_meta, virtual_meta, compress_meta
  data[2][3], data[2][4] = BCD, BCD_al

  labels = [
    "original",
    "virtual",
    "OBD",
    "BCD",
    "BCD-alignment",
  ]
  hatch_list = ["//", "\\\\", "---"]

  fig = plt.figure()
  ax = fig.add_subplot(111)
  for i in range(data.shape[0]):
      plt.bar(left, data[i],
              bottom = np.sum(data[:i], axis = 0),
              width=0.5, edgecolor='k', linewidth=1,
              tick_label=labels, hatch=hatch_list[i % len(hatch_list)])
  plt.title("{0} ratio".format(benchmark))
  plt.xlabel("Method")
  plt.ylabel("%")
  ax.set_ylim([0, 200])
  ax.grid()
  ax.legend(["hidden", "meta", "BCD"], loc='upper left', borderaxespad=1)
  fig.tight_layout()
  plt.xticks(rotation=270)
  plt.subplots_adjust(bottom=0.35)
  plt.savefig("{0}/compare-ratio.png".format(graph_path))

for i, benchmark in enumerate(benchmarks):
  print(benchmark)
  graph_path = "{0}/{1}/graph".format(path, benchmark)

  file_path = "{0}/{1}/{2}-analysis.txt".format(path, benchmark, benchmark)
  BCD_file_path = "{0}/{1}/{2}-BCD-analysis.txt".format(path, benchmark, benchmark)
  BCD_al_file_path = "{0}/{1}/{2}-BCD-alignment-analysis.txt".format(path, benchmark, benchmark)

  byte_data, compression_ratio_data = read_file(file_path)
  BCD_byte_data, BCD_compression_ratio_data  = read_file(BCD_file_path)
  BCD_al_byte_data, BCD_al_compression_ratio_data = read_file(BCD_al_file_path)

  # line graph
  create_line_graph(byte_data, compression_ratio_data, "GC", graph_path)
  create_BCD_line_graph(BCD_byte_data, BCD_compression_ratio_data, "GC", graph_path)
  create_BCD_line_graph(BCD_al_byte_data, BCD_al_compression_ratio_data, "GC", graph_path, "GC", True)

  # bar graph
  average_ratio = np.average(compression_ratio_data.T, axis=1)
  BCD_average_ratio = np.average(BCD_compression_ratio_data.T, axis=1)
  BCD_al_average_ratio = np.average(BCD_al_compression_ratio_data.T, axis=1)
  create_bar_graph(
    average_ratio,
    BCD_average_ratio,
    BCD_al_average_ratio,
    graph_path,
    benchmark
  )




# def create_bar_graph(average_ratios, graph_path):
#   average_ratios_T = average_ratios[:, 1:].T
#   left = np.arange(1, benchmark_size+1)
#   labels = benchmarks
#   hatch_list = ['//', '\\\\']

#   fig = plt.figure()
#   ax = fig.add_subplot(111)
#   for i in range(average_ratios_T.shape[0]):
#       plt.bar(left, average_ratios_T[i],
#               bottom = np.sum(average_ratios_T[:i], axis = 0),
#               width=0.5, edgecolor='k', linewidth=1,
#               tick_label=labels, hatch=hatch_list[i % len(hatch_list)])
#   plt.title("ratio")
#   plt.xlabel("Benchmark")
#   plt.ylabel("%")
#   ax.set_ylim([0, 100])
#   ax.legend(["hidden", "meta"], loc='upper left', borderaxespad=1)
#   fig.tight_layout()
#   plt.xticks(rotation=270)
#   plt.subplots_adjust(bottom=0.35)
#   plt.savefig("{0}/compression-ratio.png".format(graph_path))

# create_bar_graph(average_ratios, path)
