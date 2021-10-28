import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from read_file import read_file

def create_line_graph(byte_data, compression_ratio_data, xlabel, graph_path):
  x_size =  byte_data.shape[0]

  # byte line graph
  total_bytes = byte_data[:, 0]
  total_compression_bytes = byte_data[:, 1]
  hidden_bytes = byte_data[:, 2]
  meta_bytes = byte_data[:, 3]
  x = np.arange(1, x_size+1)

  max_bytes = np.max(total_bytes) + 1000

  c1,c2,c3,c4 = "blue","green","red", "cyan"
  l1,l2,l3,l4 = "total", "total_compression", "hidden", "meta"

  fig, ax = plt.subplots()
  plt.gca().get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True)) # x軸を整数にする
  ax.set_xlabel(xlabel)
  ax.set_ylabel("Byte")
  # ax.set_title()
  ax.grid()
  #ax.set_xlim([1, x_size])
  ax.set_ylim([0, max_bytes])
  ax.plot(x, total_bytes, color=c1, label=l1)
  ax.plot(x, total_compression_bytes, color=c2, label=l2)
  ax.plot(x, hidden_bytes, color=c3, label=l3)
  ax.plot(x, meta_bytes, color=c4, label=l4)
  ax.legend(loc=0)    # 凡例
  fig.tight_layout()  # レイアウトの設定
  plt.savefig("{0}/byte-line-GC.png".format(graph_path)) # 画像の保存
  plt.show()

  # ratio line graph
  total_combression_ratio = compression_ratio_data[:, 0]
  hidden_ratio = compression_ratio_data[:, 1]
  meta_ratio = compression_ratio_data[:, 2]
  total_combression_ratio_average = np.average(total_combression_ratio)
  hidden_ratio_average = np.average(hidden_ratio)
  meta_ratio_average = np.average(meta_ratio)
  x = np.arange(1, x_size+1)

  c1,c2,c3 = "blue","green","red"
  l1,l2,l3 = "total_compression", "hidden", "meta"

  fig, ax = plt.subplots()
  plt.gca().get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True)) # x軸を整数にする
  ax.set_xlabel(xlabel)
  ax.set_ylabel("%")
  # ax.set_title()
  ax.grid()
  #ax.set_xlim([1, x_size])
  ax.set_ylim([0, 100])
  ax.plot(x, total_combression_ratio, color=c1, label=l1)
  ax.plot(x, hidden_ratio, color=c2, label=l2)
  ax.plot(x, meta_ratio, color=c3, label=l3)
  ax.legend(loc=0)    # 凡例
  fig.tight_layout()  # レイアウトの設定
  plt.savefig("{0}/ratio-line-GC.png".format(graph_path))

  return np.array([total_combression_ratio_average, hidden_ratio_average, meta_ratio_average])


# create_line_graph(byte_data, compression_ratio_data, "GC")

path = "./results"
benchmarks = [
  "Bounce-small",
  "CD-dyn-small",
  "CD-small",
  "List-small",
  "Mandelbrot-small",
  "NBody-small",
  "Queens-small",
  "Richards-small",
  "Sieve-small",
  "Storage-small"
]

benchmark_size = len(benchmarks)
# average_ratios = np.array([
#   [61.8525, 18.11,   43.7325],
#   ...
# ])
average_ratios = np.zeros((benchmark_size, 3))
for i, benchmark in enumerate(benchmarks):
  file_path = "{0}/{1}/{2}-analysis.txt".format(path, benchmark, benchmark)
  graph_path = "{0}/{1}/graph".format(path, benchmark)

  byte_data, compression_ratio_data = read_file(file_path)
  averages = create_line_graph(byte_data, compression_ratio_data, "GC", graph_path)
  average_ratios[i] = averages

def create_bar_graph(average_ratios, graph_path):
  average_ratios_T = average_ratios[:, 1:].T
  left = np.arange(1, benchmark_size+1)
  labels = benchmarks
  hatch_list = ['//', '\\\\']

  fig = plt.figure()
  ax = fig.add_subplot(111)
  for i in range(average_ratios_T.shape[0]):
      plt.bar(left, average_ratios_T[i],
              bottom = np.sum(average_ratios_T[:i], axis = 0),
              width=0.5, edgecolor='k', linewidth=1,
              tick_label=labels, hatch=hatch_list[i % len(hatch_list)])
  plt.title("ratio")
  plt.xlabel("Benchmark")
  plt.ylabel("%")
  ax.set_ylim([0, 100])
  ax.legend(["hidden", "meta"], loc='upper left', borderaxespad=1)
  fig.tight_layout()
  plt.xticks(rotation=270)
  plt.subplots_adjust(bottom=0.35)
  plt.savefig("{0}/compression-ratio.png".format(graph_path))

create_bar_graph(average_ratios, path)
