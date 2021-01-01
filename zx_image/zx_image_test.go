package main_test

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/wallermatt/z80/zx_image"
)

func Test_ReadSnapshot(t *testing.T) {
	s := zx_image.ReadSnapshot("testData/testSnapshot.sna")
	assert.Equal(t, 49179, len(s))
	assert.Equal(t, uint8(0x3f), s[0])
	assert.Equal(t, uint8(0x0), s[len(s)-1])
}

func Test_LoadScrMemory(t *testing.T) {
	s := zx_image.ReadSnapshot("testData/testSnapshot.sna")
	scrMemory := zx_image.LoadScrMemory(s)
	assert.Equal(t, uint8(0x0), scrMemory[0][0])
	assert.Equal(t, uint8(0xff), scrMemory[110][25])
	assert.Equal(t, uint8(0x0), scrMemory[191][31])
}
