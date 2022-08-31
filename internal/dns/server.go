package dns

import (
	"log"
	"net"

	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"
)

type Server struct {
	Dns DNS
}

func (s Server) Start() {
	// Listen on UDP Port
	addr := net.UDPAddr{
		Port: 8090,
		IP:   net.ParseIP("0.0.0.0"),
	}
	u, _ := net.ListenUDP("udp", &addr)

	log.Printf("[OK] DNS server on port: %d\n", 8090)

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
