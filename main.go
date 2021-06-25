package main

import (
	"flag"
	"fmt"
	"os"

	"github.com/dbridges/sermon/util"
)

// Version is auto set from the Makefile
var Version string

// SerialConfig stores attributes needed to setup the serial port
type SerialConfig struct {
	device   string
	baud     int
	dataBits int
	stopBits int
}

func usage() {
	fmt.Println("usage: sermon [--baud b] [--databits d] [--stopbits s] [device]")
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
	cfg := SerialConfig{}

	flag.Usage = usage

	flag.IntVar(&cfg.baud, "baud", 9600, "set baud rate")
	flag.IntVar(&cfg.dataBits, "databits", 8, "set number of data bits")
	flag.IntVar(&cfg.stopBits, "stopbits", 1, "set number of stop bits")

	flag.Parse()

	if flag.NArg() == 1 {
		if flag.Arg(0) == "help" {
			flag.Usage()
			return
		}
		cfg.device = flag.Arg(0)
	} else {
		d, err := promptDevice()
		if err != nil {
			os.Stderr.WriteString(fmt.Sprintf("Error selecting device: %v\n", err))
			os.Exit(1)
		}
		cfg.device = d
	}

	fmt.Println(cfg)
}
