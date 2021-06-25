.PHONY: all run run-with-race clean install uninstall release

VERSION=0.1.0
GO_SRC = $(shell find . -iname '*.go')
BINDIR?=/usr/local/bin
BINNAME?=sermon

all: dist/$(BINNAME)

dist/$(BINNAME): $(GO_SRC) dist
	go build -ldflags "-X main.Version=$(VERSION)" -o $@

run:
	@go run $(GO_SRC)

run-with-race:
	@GORACE="log_path=race_log" go run -race *.go

clean:
	rm -f dist/*
	rm -f race_log.*

install: all
	mkdir -p $(BINDIR)
	install dist/$(BINNAME) $(BINDIR)/$(BINNAME)

dist:
	mkdir dist

uninstall:
	rm -f $(BINDIR)/$(BINNAME)

release: dist/$(BINNAME)
	mkdir -p dist/sermon-v$(VERSION)
	cp README.md dist/sermon-v$(VERSION)
	cp dist/sermon dist/sermon-v$(VERSION)
	cd dist && tar -zcvf sermon-v$(VERSION).tar.gz sermon-v$(VERSION)
	git tag -a v$(VERSION) -m "sermon v$(VERSION)"
	git push origin v$(VERSION)
