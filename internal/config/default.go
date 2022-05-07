package config

import (
	"github.com/amirhnajafiz/mockapetris/internal/database"
	"github.com/amirhnajafiz/mockapetris/internal/dns"
	"github.com/amirhnajafiz/mockapetris/internal/root"
)

func Default() Config {
	return Config{
		Database: database.Config{
			Address:  "",
			Password: "",
		},
		Root: root.Config{
			Host: ":1348",
		},
		Server: dns.Config{
			IP:   "",
			Port: 8090,
		},
	}
}
