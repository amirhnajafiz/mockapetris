package root

import "github.com/amirhnajafiz/mockapetris/internal/database"

type Root struct {
	DB database.Database
}

func (r Root) Register() {

}
