package main

import (
	"github.com/amirhnajafiz/mockapetris/internal/dns"
	"github.com/amirhnajafiz/mockapetris/internal/redis"
	"github.com/amirhnajafiz/mockapetris/internal/root"
)

func main() {
	// initializing our redis client
	db := redis.Database{}
	db.Register()

	// root server for controlling our dns server
	r := root.Root{}.Register(db)
	r.Start()

	// main dns server
	dns.Server{
		Dns: dns.DNS{
			DB: db,
		},
	}.Start()
}
