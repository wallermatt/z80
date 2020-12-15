import math

for i in range(0, 6144):
    block = i // 2048
    block_offset = i % 2048
    column = block_offset % 32
    line = block_offset // 256
    line_offset = block_offset % 256
    row = line_offset // 32
    x_coord = column * 8 + (7 - int(math.log(128) / math.log(2)))
    y_coord = block * 64 + row * 8 + line
    print(i, block, row, line, column, x_coord, y_coord)
