package dns

import (
	"fmt"
	"net"

	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"
)

var Records map[string]string

type Server struct {
	Dns DNS
}

func (s *Server) Start(cfg Config) {
	Records = map[string]string{
		"google.com": "216.58.196.142",
		"amazon.com": "176.32.103.205",
	}

	// Listen on UDP Port
	addr := net.UDPAddr{
		Port: cfg.Port,
		IP:   net.ParseIP(cfg.IP),
	}
	u, _ := net.ListenUDP("udp", &addr)

	fmt.Println("[OK] DNS server on port: 8090")

	// Wait to get request on that port
	for {
		// temp buffer
		tmp := make([]byte, 1024)
		// read from UDP
		_, clientAddr, _ := u.ReadFrom(tmp)
		// create DNS Packet
		dnsPacket := gopacket.NewPacket(tmp, layers.LayerTypeDNS, gopacket.Default).Layer(layers.LayerTypeDNS)
		// TCP creation
		tcp, _ := dnsPacket.(*layers.DNS)
		// calling serve DNS
		s.Dns.Serve(u, clientAddr, tcp)
	}
}
