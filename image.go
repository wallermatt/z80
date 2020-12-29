package main

import (
	"fmt"
	"io/ioutil"
)

type ScrRow [32]byte
type ScrMemory [192]ScrRow
type ScrAttributes [24]ScrRow

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
}
