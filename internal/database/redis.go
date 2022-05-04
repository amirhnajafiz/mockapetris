package database

import (
	"context"

	"github.com/go-redis/redis/v8"
)

type Database struct {
	redis *redis.Client
}

// Register : creates a new redis connection
func (db *Database) Register(cfg Config) {
	db.redis = redis.NewClient(&redis.Options{
		Addr:     cfg.Address,
		Password: cfg.Password,
		DB:       0,
	})
}

// Add : add a new item to redis
func (db *Database) Add(key string, value string) error {
	ctx := context.Background()

	return db.redis.Set(ctx, key, value, 0).Err()
}

// Get : get a record from redis
func (db *Database) Get(key string) (string, error) {
	ctx := context.Background()

	return db.redis.Get(ctx, key).Result()
}

// Delete : remove a record from redis
func (db *Database) Delete(key string) error {
	ctx := context.Background()

	return db.redis.Del(ctx, key).Err()
}
