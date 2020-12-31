package zx_image_test

import (
	"testing"

	"github.com/wallermatt/z80/zx_image"
)

func Test_ReadSnapshot(t *testing.T) {
	s := zx_image.ReadSnapshot("testSnapshot.sna")
	assert.Equal(t, 25, len(s))
}
