package main

import (
	"fmt"
	"image"
	"image/color"
	"image/png"
	"io/ioutil"
	"os"
)

type ScrRow [32]byte
type ScrMemory [192]ScrRow
type ScrAttributes [24]ScrRow

type SpecColour struct {
	normal color.RGBA
	bright color.RGBA
}
type SpecColoursType [8]SpecColour

var SpecColours = SpecColoursType{
	SpecColour{color.RGBA{0, 0, 0, 255}, color.RGBA{0, 0, 0, 255}},
	SpecColour{color.RGBA{0, 0, 215, 255}, color.RGBA{0, 0, 255, 255}},
	SpecColour{color.RGBA{215, 0, 0, 255}, color.RGBA{255, 0, 0, 255}},
	SpecColour{color.RGBA{215, 0, 215, 255}, color.RGBA{255, 0, 255, 255}},
	SpecColour{color.RGBA{0, 215, 0, 255}, color.RGBA{0, 255, 0, 255}},
	SpecColour{color.RGBA{0, 215, 215, 255}, color.RGBA{0, 255, 255, 255}},
	SpecColour{color.RGBA{215, 215, 0, 255}, color.RGBA{255, 255, 0, 255}},
	SpecColour{color.RGBA{215, 215, 215, 255}, color.RGBA{255, 255, 255, 255}},
}

const (
	filename           = "/home/matthew/projects/z80/be.sna"
	scrMemoryStart     = 27
	scrAttributesStart = 6171
)

func ReadSnapshot(f string) []byte {
	s, err := ioutil.ReadFile(filename)
	if err != nil {
		panic(err)
	}
	return s
}

func LoadScrMemory(s []byte) ScrMemory {
	snapshotIndex := scrMemoryStart
	scrMemory := ScrMemory{}
	for y, row := range scrMemory {
		for x, _ := range row {
			scrMemory[y][x] = s[snapshotIndex]
			snapshotIndex += 1
		}
	}
	return scrMemory
}

func LoadScrAttributes(s []byte) ScrAttributes {
	snapshotIndex := scrAttributesStart
	scrAttributes := ScrAttributes{}
	for y, row := range scrAttributes {
		for x, _ := range row {
			scrAttributes[y][x] = s[snapshotIndex]
			snapshotIndex += 1
		}
	}
	return scrAttributes
}

func getPaperAndInk(value byte) (paper color.RGBA, ink color.RGBA) {
	bright := (value << 1) / 128
	paperIndex := (value >> 3) % 8
	inkIndex := value % 8
	if bright == 0 {
		paper = SpecColours[paperIndex].normal
		ink = SpecColours[inkIndex].normal
	} else {
		paper = SpecColours[paperIndex].bright
		ink = SpecColours[inkIndex].bright
	}
	return paper, ink
}

func getXYFromScrMemory(memX int, memY int) (x int, y int) {
	x = memX * 8
	block := memY / 64
	blockOffset := memY % 64
	row := blockOffset / 8
	rowOffset := blockOffset % 8
	y = block*64 + rowOffset*8 + row
	return x, y
}

func getScrMemoryFromXY(x int, y int) int {
	memX := x / 8
	block := y / 64
	blockOffset := block % 64
	row := blockOffset % 8
	rowOffset := blockOffset / 8
	memY = block*64 + row*8 + rowOffset
	return scrMemory[memY][memX]
}

func main() {

	s := ReadSnapshot(filename)
	scrMemory := LoadScrMemory(s)
	scrAttributes := LoadScrAttributes(s)

	fmt.Println(len(s))
	fmt.Println(scrMemory)
	fmt.Println(scrAttributes)

	width := 256
	height := 192

	upLeft := image.Point{0, 0}
	lowRight := image.Point{width, height}

	img := image.NewRGBA(image.Rectangle{upLeft, lowRight})

	// Set paper color for each pixel.
	for x := 0; x < width; x++ {
		for y := 0; y < height; y++ {
			gridX := x / 8
			gridY := y / 8
			paper, _ := getPaperAndInk(scrAttributes[gridY][gridX])
			img.Set(x, y, paper)
		}
	}

	f, _ := os.Create("image.png")
	png.Encode(f, img)

}
