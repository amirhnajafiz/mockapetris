package database

import (
	"context"

	"github.com/go-redis/redis/v8"
)

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

func (db *Database) Add(key string, value string) error {
	ctx := context.Background()

	return db.redis.Set(ctx, key, value, 0).Err()
}

func (db *Database) Get(key string) (string, error) {
	ctx := context.Background()

	return db.redis.Get(ctx, key).Result()
}
