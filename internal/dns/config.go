package dns

type Config struct {
	IP   string `koanf:"ip"`
	Port int    `koanf:"port"`
}
