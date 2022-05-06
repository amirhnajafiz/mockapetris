package config

import (
	"github.com/amirhnajafiz/mockapetris/internal/database"
	"github.com/amirhnajafiz/mockapetris/internal/dns"
)

type Config struct {
	Database database.Config `koanf:"cache"`
	Server   dns.Config      `koanf:"dns"`
}
