package dns

import (
	"log"
	"net"

	"github.com/amirhnajafiz/mockapetris/internal/redis"
	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"
)

// DNS Type
type DNS struct {
	DB redis.Database
}

// Serve method will handle the user request
func (d DNS) Serve(u *net.UDPConn, clientAddr net.Addr, request *layers.DNS) {
	ip, ok := d.DB.Get(string(request.Questions[0].Name))
	if ok != nil {
		log.Println("[FAIL] No record found")
	}

	a, _, _ := net.ParseCIDR(ip + "/24")

	dnsAnswer := layers.DNSResourceRecord{
		Type:  layers.DNSTypeA,
		IP:    a,
		Name:  request.Questions[0].Name,
		Class: layers.DNSClassIN,
	}

	log.Printf("[OK] Request name: %s\n", request.Questions[0].Name)

	replyMess := request
	replyMess.QR = true
	replyMess.ANCount = 1
	replyMess.OpCode = layers.DNSOpCodeNotify
	replyMess.AA = true
	replyMess.Answers = append(replyMess.Answers, dnsAnswer)
	replyMess.ResponseCode = layers.DNSResponseCodeNoErr

	buf := gopacket.NewSerializeBuffer()
	opts := gopacket.SerializeOptions{}
	err := replyMess.SerializeTo(buf, opts)

	if err != nil {
		panic(err)
	}

	_, _ = u.WriteTo(buf.Bytes(), clientAddr)
}
