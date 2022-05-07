package main

import (
	"github.com/amirhnajafiz/mockapetris/internal/config"
	"github.com/amirhnajafiz/mockapetris/internal/database"
	"github.com/amirhnajafiz/mockapetris/internal/dns"
	"github.com/amirhnajafiz/mockapetris/internal/root"
)

func main() {
	cfg := config.Load()

	db := database.Database{}
	db.Register(cfg.Database)

	r := root.Root{}.Register(root.Config{}, db)
	r.Start()

	dns.Server{
		Dns: dns.DNS{
			DB: db,
		},
	}.Start(cfg.Server)
}
