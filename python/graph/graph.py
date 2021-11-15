import sys
import os
import numpy as np

from read_file import read_file, getResultPath
from create_graph import create_OBD_line_graph, create_BCD_line_graph, create_bar_graph, create_bar_graph_all

ANALYSIS_PYTHON_RESULTS = os.environ["ANALYSIS_PYTHON_RESULTS"]

dump = "GC"
if (len(sys.argv) > 1):
  dump = sys.argv[1]

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

## 実行
original_hiddens = []
original_metas = []
compress_hiddens = []
compress_metas = []
BCDs = []
best_BCDs = []
best_is = []
for i, benchmark in enumerate(benchmarks):
  print(benchmark)
  graph_path = "{0}/{1}/graph".format(ANALYSIS_PYTHON_RESULTS, benchmark)

  OBD_file_path = getResultPath(benchmark, "OBD", dump)
  BCD_file_path = getResultPath(benchmark, "BCD", dump)
  BCDAL_file_path = getResultPath(benchmark, "BCDAL", dump)
  BCDAL1_file_path = getResultPath(benchmark, "BCDAL", dump, 1)
  BCDAL2_file_path = getResultPath(benchmark, "BCDAL", dump, 2)
  BCDAL3_file_path = getResultPath(benchmark, "BCDAL", dump, 3)
  BCDAL4_file_path = getResultPath(benchmark, "BCDAL", dump, 4)
  BCDAL5_file_path = getResultPath(benchmark, "BCDAL", dump, 5)
  BCDAL6_file_path = getResultPath(benchmark, "BCDAL", dump, 6)

  OBD_byte_data, OBD_compression_ratio_data = read_file(OBD_file_path)
  BCD_byte_data, BCD_compression_ratio_data  = read_file(BCD_file_path)
  BCDAL_byte_data, BCDAL_compression_ratio_data = read_file(BCDAL_file_path)
  BCDAL1_byte_data, BCDAL1_compression_ratio_data = read_file(BCDAL1_file_path)
  BCDAL2_byte_data, BCDAL2_compression_ratio_data = read_file(BCDAL2_file_path)
  BCDAL3_byte_data, BCDAL3_compression_ratio_data = read_file(BCDAL3_file_path)
  BCDAL4_byte_data, BCDAL4_compression_ratio_data = read_file(BCDAL4_file_path)
  BCDAL5_byte_data, BCDAL5_compression_ratio_data = read_file(BCDAL5_file_path)
  BCDAL6_byte_data, BCDAL6_compression_ratio_data = read_file(BCDAL6_file_path)

  # line graph
  # create_OBD_line_graph(OBD_byte_data, OBD_compression_ratio_data, dump, graph_path)
  # create_BCD_line_graph(BCD_byte_data, BCD_compression_ratio_data, dump, graph_path)
  # create_BCD_line_graph(BCDAL_byte_data, BCDAL_compression_ratio_data, dump, graph_path, dump, True)
  # create_BCD_line_graph(BCDAL1_byte_data, BCDAL1_compression_ratio_data, dump, graph_path, dump, True, 1)
  # create_BCD_line_graph(BCDAL2_byte_data, BCDAL2_compression_ratio_data, dump, graph_path, dump, True, 2)
  # create_BCD_line_graph(BCDAL3_byte_data, BCDAL3_compression_ratio_data, dump, graph_path, dump, True, 3)
  # create_BCD_line_graph(BCDAL4_byte_data, BCDAL4_compression_ratio_data, dump, graph_path, dump, True, 4)
  # create_BCD_line_graph(BCDAL5_byte_data, BCDAL5_compression_ratio_data, dump, graph_path, dump, True, 5)
  # create_BCD_line_graph(BCDAL6_byte_data, BCDAL6_compression_ratio_data, dump, graph_path, dump, True, 6)

  # bar graph
  OBD_average_ratio = np.average(OBD_compression_ratio_data.T, axis=1)
  BCD_average_ratio = np.average(BCD_compression_ratio_data.T, axis=1)
  BCDAL_average_ratio = np.average(BCDAL_compression_ratio_data.T, axis=1)
  BCDAL1_average_ratio = np.average(BCDAL1_compression_ratio_data.T, axis=1)
  BCDAL2_average_ratio = np.average(BCDAL2_compression_ratio_data.T, axis=1)
  BCDAL3_average_ratio = np.average(BCDAL3_compression_ratio_data.T, axis=1)
  BCDAL4_average_ratio = np.average(BCDAL4_compression_ratio_data.T, axis=1)
  BCDAL5_average_ratio = np.average(BCDAL5_compression_ratio_data.T, axis=1)
  BCDAL6_average_ratio = np.average(BCDAL6_compression_ratio_data.T, axis=1)

  original_hidden, original_meta, compress_hidden, compress_meta, BCD, best_BCD, best_i = create_bar_graph(
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
  )
  original_hiddens.append(original_hidden)
  original_metas.append(original_meta)
  compress_hiddens.append(compress_hidden)
  compress_metas.append(compress_meta)
  BCDs.append(BCD)
  best_BCDs.append(best_BCD)
  best_is.append(best_i)

create_bar_graph_all(
  original_hiddens,
  original_metas,
  compress_hiddens,
  compress_metas,
  BCDs,
  best_BCDs,
  best_is,
  benchmarks,
  ANALYSIS_PYTHON_RESULTS,
  dump
)
# print(hiddens)
# print(metas)
# print(BCDs)
# print(best_is)
