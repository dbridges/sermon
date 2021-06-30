package app

import (
	"fmt"

	"github.com/dbridges/sermon/ui"
	"github.com/dbridges/sermon/widget"
	"github.com/gdamore/tcell/v2"
	"github.com/gdamore/tcell/v2/encoding"
	"github.com/pkg/term"
)

// AppConfig stores attributes needed to setup the serial port
type Config struct {
	Device string
	Baud   int
}

// App is the main object that runs the app
type App struct {
	cfg    Config
	term   *term.Term
	screen tcell.Screen
	text   *widget.Text
	header *widget.Text
	footer *widget.Text
}

// New returns a new App instance
func New(cfg Config) *App {
	return &App{cfg: cfg}
}

func (app *App) draw() {
	w, h := app.screen.Size()
	app.screen.Clear()

	main := ui.NewCanvas(app.screen, 0, 1, w, h-2)
	header := ui.NewCanvas(app.screen, 0, 0, w, 1)
	footer := ui.NewCanvas(app.screen, 0, h-1, w, 1)

	app.header.Draw(header)
	app.text.Draw(main)
	app.footer.Draw(footer)

	app.screen.Show()
}

// Run starts the app
func (app *App) Run() error {
	var err error

	encoding.Register()

	app.screen, err = tcell.NewScreen()
	if err != nil {
		return err
	}
	err = app.screen.Init()
	if err != nil {
		return err
	}

	app.term, err = term.Open(app.cfg.Device, term.Speed(app.cfg.Baud))
	if err != nil {
		return err
	}
	defer app.term.Close()

	// _, err = io.Copy(os.Stdout, app.term)
	// if err != nil {
	// 	return err
	// }
	app.header = widget.NewText(fmt.Sprintf("Connected to %s", app.cfg.Device), tcell.StyleDefault)
	app.text = widget.NewText("Dan", tcell.StyleDefault)
	app.footer = widget.NewText("[q] Quit    [:] Open Command Prompt", tcell.StyleDefault.Reverse(true))

	for {
		switch e := app.screen.PollEvent().(type) {
		case *tcell.EventResize:
			app.draw()
		case *tcell.EventKey:
			if e.Rune() == 'q' || e.Key() == tcell.KeyCtrlC {
				app.screen.Fini()
				return nil
			}
		}
		// fmt.Println(e)
		// return nil
	}
}
