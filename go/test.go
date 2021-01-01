package main

import (
	"fmt"
	"math"
	"os"
)

func getXYFromScrMemory(memX int, memY int) (x int, y int) {
	x = memX * 8
	block := memY / 64
	blockOffset := memY % 64
	row := blockOffset / 8
	rowOffset := blockOffset % 8
	y = block*64 + row*8 + rowOffset
	return x, y
}

func getScrMemoryFromXY(x int, y int) (int, int) {
	memX := x / 8
	block := y / 64
	blockOffset := y % 64
	row := blockOffset % 8
	rowOffset := blockOffset / 8
	memY := block*64 + row*8 + rowOffset
	//fmt.Println(block, blockOffset, row, rowOffset)
	return memX, memY
}

func getXPixelFromByte(x int, memory byte) int {
	offsetX := x % 8
	return int(memory) & int(math.Pow(2, float64(7-offsetX)))
}

func main() {

	args := os.Args
	fmt.Println(args)

	x, y := getScrMemoryFromXY(0, 0)
	fmt.Println(x, y)
	memX, memY := getScrMemoryFromXY(0, 0)
	fmt.Println(memX, memY)

	x, y = getScrMemoryFromXY(1, 0)
	fmt.Println(x, y)
	memX, memY = getScrMemoryFromXY(1, 0)
	fmt.Println(memX, memY)

	x, y = getScrMemoryFromXY(8, 0)
	fmt.Println(x, y)
	memX, memY = getScrMemoryFromXY(8, 0)
	fmt.Println(memX, memY)

	x, y = getScrMemoryFromXY(0, 1)
	fmt.Println(x, y)
	memX, memY = getScrMemoryFromXY(0, 8)
	fmt.Println(memX, memY)

	x, y = getScrMemoryFromXY(0, 8)
	fmt.Println(x, y)
	memX, memY = getScrMemoryFromXY(0, 1)
	fmt.Println(memX, memY)
}
