package root

import (
	"net/http"

	"github.com/amirhnajafiz/mockapetris/internal/database"
)

type Root struct {
	DB      database.Database
	Srv     *http.ServeMux
	Address string
}

func (r Root) Register(d database.Database) Root {
	srv := http.NewServeMux()

	srv.HandleFunc("/put", r.AddRecord)
	srv.HandleFunc("/del", r.RemoveRecord)

	return Root{
		DB:      d,
		Srv:     srv,
		Address: ":1348",
	}
}

func (r Root) Start() {
	go func() {
		if err := http.ListenAndServe(r.Address, r.Srv); err != nil {
			panic(err)
		}
	}()
}

func (r Root) AddRecord(w http.ResponseWriter, req *http.Request) {

}

func (r Root) RemoveRecord(w http.ResponseWriter, req *http.Request) {

}
