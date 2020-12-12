for i in range(0, 6144):
    block = i // 2048
    block_offset = i % 2048
    column = block_offset % 32
    line = block_offset // 256
    line_offset = block_offset % 256
    row = line_offset // 32
    print(i, block, row, line, column)
