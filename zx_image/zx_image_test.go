package main_test

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/wallermatt/z80/zx_image"
)

func Test_ReadSnapshot(t *testing.T) {
	s := zx_image.ReadSnapshot("testData/testSnapshot.sna")
	assert.Equal(t, 49179, len(s))
}
