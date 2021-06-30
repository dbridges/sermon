package widget

// Widget defines the base interface for all on screen components
type Widget interface {
	Draw()
	Focusable() bool
}
