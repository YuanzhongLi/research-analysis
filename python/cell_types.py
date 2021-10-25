WHITE = (255, 255, 255)
BLACK = (0,0,0)

CellTypeDict = {
  0: ("CELLT_FREE", WHITE),
  4: ("CELLT_STRING", (0, 255, 255)),
  5: ("CELLT_FLONUM", (0, 0, 192)),
  6: ("CELLT_SIMPLE_OBJECT", (255, 255, 0)), # JSObject
  7: ("CELLT_ARRAY", (128, 0, 0)), # JSObject
  8: ("CELLT_FUNCTION", (0, 255, 0)), # JSObject
  9: ("CELLT_BUILTIN", (255, 0, 255)), # JSObject
  10: ("CELLT_ITERATOR", (0, 128, 128)),
  11: ("CELLT_REGEXP", (0, 192, 0)), # JSObject
  12: ("CELLT_BOXED_STRING", (192, 0, 0)), # JSObject
  13: ("CELLT_BOXED_NUMBER", (0, 192, 192)), # JSObject
  14: ("CELLT_BOXED_BOOLEAN", (192, 0, 192)), # JSObject

  17: ("CELLT_PROP", (0, 0, 255)), # Array of JSValues
  18: ("CELLT_ARRAY_DATA", (0, 0, 128)), # Array of JSValues
  19: ("CELLT_BYTE_ARRAY", (192, 192, 0)), # Array of primitives
  20: ("CELLT_FUNCTION_FRAME", (64, 64, 64)),
  21: ("CELLT_STR_CONS", (255, 0, 0)),
  # 22: "CELLT_CONTEXT", no longer used
  # 23: "CELLT_STACK", no longer used
  24: ("CELLT_TRANSITIONS", (128, 128, 0)),
  25: ("CELLT_HASHTABLE", (192, 192, 192)),
  # 26: "CELLT_HASH_BODY",  no longer used
  # 27: "CELLT_HASH_CELL", no longer used
  28: ("CELLT_PROPERTY_MAP", (128, 128, 128)),
  29: ("CELLT_SHAPE", (0, 128, 0)),
  30: ("CELLT_UNWIND", (0, 64, 0)),
  31: ("CELLT_PROPERTY_MAP_LIST", (128, 0, 128)),
}

def is_hidden_class(type):
  return (6 <= type and type <= 14 and type != 10)

def num2color(x):
  r = x >> 16
  g = (x >> 8) % (1 << 8)
  b = x % (1 << 8)
  return (r, g, b)

def color2num(c):
  r, g, b = c[0], c[1], c[2]
  return (r << 16) + (g << 8) + b
