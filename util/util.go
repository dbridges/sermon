package util

import "path/filepath"

// ListSerialDevices returns a list of available serial devices
func ListSerialDevices() ([]string, error) {
	return filepath.Glob("/dev/tty.*")
}
