package main

import (
	"flag"
	"fmt"
	"os"

	"github.com/dbridges/sermon/app"
	"github.com/dbridges/sermon/util"
)

// Version is auto set from the Makefile
var Version string

func usage() {
	fmt.Println("usage: sermon [--baud b] [device]")
	flag.PrintDefaults()
}

func promptDevice() (string, error) {
	devices, err := util.ListSerialDevices()
	if err != nil {
		return "", err
	}

	fmt.Println()
	for i, d := range devices {
		fmt.Printf("\t%d. %s\n", i+1, d)
	}
	fmt.Println()
	fmt.Printf("Select device [1-%d]: ", len(devices))

	var response int
	fmt.Scanln(&response)
	if response < 1 || response > len(devices) {
		return "", fmt.Errorf("invalid device selection")
	}

	return devices[response-1], nil
}

func main() {
	cfg := app.Config{}

	flag.Usage = usage

	flag.IntVar(&cfg.Baud, "baud", 9600, "set baud rate")

	flag.Parse()

	if flag.NArg() == 1 {
		if flag.Arg(0) == "help" {
			flag.Usage()
			os.Exit(0)
		}
		cfg.Device = flag.Arg(0)
	} else {
		d, err := promptDevice()
		if err != nil {
			os.Stderr.WriteString(fmt.Sprintf("Error selecting device: %v\n", err))
			os.Exit(1)
		}
		cfg.Device = d
	}

	app.New(cfg).Run()
}
