package widget

import (
	"github.com/dbridges/sermon/ui"
	"github.com/gdamore/tcell/v2"
)

// Text displays a text box with the given content
type Text struct {
	content string
	style   tcell.Style
}

// NewText creates and returns a new text widget
func NewText(content string, style tcell.Style) *Text {
	return &Text{content, style}
}

// Draw draws the text
func (widget *Text) Draw(canvas *ui.Canvas) {
	canvas.Clear(widget.style)
	x := 0
	y := 0
	for _, c := range widget.content {
		switch c {
		case '\n':
			x = 0
			y++
		case '\r':
		default:
			canvas.SetCell(x, y, c, widget.style)
		}

		x++
		if x >= canvas.Width() {
			x = 0
			y++
		}
		if y >= canvas.Height() {
			return
		}
	}
}

// SetContent sets the content string
func (widget *Text) SetContent(content string) {
	widget.content = content
}

// Focusable always returns false
func (widget *Text) Focusable() bool {
	return false
}
