package config

import (
	"github.com/amirhnajafiz/mockapetris/internal/database"
	"github.com/amirhnajafiz/mockapetris/internal/dns"
)

func Default() Config {
	return Config{
		Database: database.Config{
			Address:  "",
			Password: "",
		},
		Server: dns.Config{
			IP:   "",
			Port: 8090,
		},
	}
}
