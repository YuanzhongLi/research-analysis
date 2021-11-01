from math import floor
from cell_types import is_hidden_class

def calc_percent(x, y, d=2):
  if y == 0:
    return 0
  return floor((x * 100 * 10**d)/y)/(10**d)

def b2kb(b, d=2):
  return floor(b / 1024 * 100) / 100

def get_key(type, hidden_class, byte):
  if is_hidden_class(type):
    return (-1, hidden_class)
  else:
    return (type, byte)

# 16byte何個分が必要でそのトータルのbyte数を返す
def divide16(x):
  return ((x + 15) // 16) * 16
