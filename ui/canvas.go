package ui

import "github.com/gdamore/tcell/v2"

// Canvas represents a drawable subset of a screen
type Canvas struct {
	screen              tcell.Screen
	x, y, width, height int
}

// NewCanvas creates and returns a new canvas struct
func NewCanvas(screen tcell.Screen, x, y, w, h int) *Canvas {
	return &Canvas{screen, x, y, w, h}
}

// SetCell sets the cell of a canvas
func (c *Canvas) SetCell(x, y int, char rune, style tcell.Style) {
	if x < 0 || x >= c.width {
		return
	}
	if y < 0 || y >= c.height {
		return
	}
	c.screen.SetContent(c.x+x, c.y+y, char, nil, style)
}

// Fill fills the entire canvas with the given rune
func (c *Canvas) Fill(char rune, style tcell.Style) {
	for i := 0; i < c.width; i++ {
		for j := 0; j < c.height; j++ {
			c.SetCell(i, j, char, style)
		}
	}
}

// Clear clears the entire canvas area
func (c *Canvas) Clear(style tcell.Style) {
	c.Fill(' ', style)
}

// Width returns the width of the canvas
func (c *Canvas) Width() int {
	return c.width
}

// Height returns the height of the canvas
func (c *Canvas) Height() int {
	return c.height
}
