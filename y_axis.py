for i in range(192):
    block = i // 64
    block_offset = i % 64
    row = block_offset % 8
    row_offset = block_offset // 8
    memory = block * 2048 + row * 256 + row_offset * 32
    print(i, block, row, row_offset, memory)

    
