package dns

import (
	"fmt"
	"log"
	"net"

	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"
)

func serveDNS(u *net.UDPConn, clientAddr net.Addr, request *layers.DNS) {
	ip, ok := Records[string(request.Questions[0].Name)]
	if !ok {
		log.Println("[FAIL] No record found")
	}

	a, _, _ := net.ParseCIDR(ip + "/24")

	dnsAnswer := layers.DNSResourceRecord{
		Type:  layers.DNSTypeA,
		IP:    a,
		Name:  request.Questions[0].Name,
		Class: layers.DNSClassIN,
	}

	fmt.Printf("[OK] Request name: %s\n", request.Questions[0].Name)

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
