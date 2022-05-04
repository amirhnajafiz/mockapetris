package database

import "github.com/go-redis/redis/v8"

type Database struct {
	redis *redis.Client
}

func (db *Database) Register(cfg Config) {
	db.redis = redis.NewClient(&redis.Options{
		Addr:     cfg.Address,
		Password: cfg.Password,
		DB:       0,
	})
}
