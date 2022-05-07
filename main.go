package main

import (
	"github.com/amirhnajafiz/mockapetris/internal/config"
	"github.com/amirhnajafiz/mockapetris/internal/database"
	"github.com/amirhnajafiz/mockapetris/internal/dns"
	"github.com/amirhnajafiz/mockapetris/internal/root"
)

func main() {
	// loading configs
	cfg := config.Load()

	// initializing our redis client
	db := database.Database{}
	db.Register(cfg.Database)

	// root server for controlling our dns server
	r := root.Root{}.Register(cfg.Root, db)
	r.Start()

	// main dns server
	dns.Server{
		Dns: dns.DNS{
			DB: db,
		},
	}.Start(cfg.Server)
}
