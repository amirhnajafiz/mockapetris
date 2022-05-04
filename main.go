package main

import (
	"github.com/amirhnajafiz/mockapetris/internal/database"
	"github.com/amirhnajafiz/mockapetris/internal/dns"
)

func main() {
	db := database.Database{}
	db.Register(database.Config{})

	server := dns.Server{
		Dns: dns.DNS{
			DB: db,
		},
	}

	server.Start(dns.Config{})
}
