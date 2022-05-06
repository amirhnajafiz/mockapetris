package main

import (
	"github.com/amirhnajafiz/mockapetris/internal/config"
	"github.com/amirhnajafiz/mockapetris/internal/database"
	"github.com/amirhnajafiz/mockapetris/internal/dns"
)

func main() {
	cfg := config.Load()

	db := database.Database{}
	db.Register(cfg.Database)

	dns.Server{
		Dns: dns.DNS{
			DB: db,
		},
	}.Start(cfg.Server)
}
