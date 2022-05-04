package database

import "github.com/go-redis/redis/v8"

func New(cfg Config) *redis.Client {
	return redis.NewClient(&redis.Options{
		Addr:     cfg.Address,
		Password: cfg.Password,
		DB:       0,
	})
}
