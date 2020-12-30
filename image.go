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
	normal string
	bright string
}
type SpecColoursType [8]SpecColour

var SpecColours = SpecColoursType{
	SpecColour{"#000000", "#000000"},
	SpecColour{"#0000D7", "#0000FF"},
	SpecColour{"#D70000", "#FF0000"},
	SpecColour{"#D700D7", "#FF00FF"},
	SpecColour{"#00D700", "#00FF00"},
	SpecColour{"#00D7D7", "#00FFFF"},
	SpecColour{"#D7D700", "#FFFF00"},
	SpecColour{"#D7D7D7", "#FFFFFF"},
}

/*
rgb(0,0,0) rgb(0,0,0)
rgb(0,0,215) rgb(0,0,255)
rgb(215,0,0) rgb(255,0,0)
rgb(215,0,215) rgb(255,0,255)
rgb(0,215,0) rgb(0,255,0)
rgb(0,215,215) rgb(0,255,255)
rgb(215,215,0) rgb(255,255,0)
rgb(215,215,215) rgb(255,255,255)
*/

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

	// Colors are defined by Red, Green, Blue, Alpha uint8 values.
	cyan := color.RGBA{100, 200, 200, 0xff}

	// Set color for each pixel.
	for x := 0; x < width; x++ {
		for y := 0; y < height; y++ {
			switch {
			case x < width/2 && y < height/2: // upper left quadrant
				img.Set(x, y, cyan)
			case x >= width/2 && y >= height/2: // lower right quadrant
				img.Set(x, y, color.White)
			default:
				// Use zero value.
			}
		}
	}

	f, _ := os.Create("image.png")
	png.Encode(f, img)

	fmt.Println(SpecColours)

}
