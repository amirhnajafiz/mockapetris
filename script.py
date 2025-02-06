import dns.message
import dns.query
import dns.rdatatype



# Choose a root name server (one of the 13 root servers)
ROOT_SERVER = "198.41.0.4"  # Example: a.root-servers.net

# Create a DNS query message for "example.com" (A record)
domain = "cs.stonybrook.edu"
query = dns.message.make_query(domain, dns.rdatatype.MX)

# Send query directly to the root name server
response = dns.query.udp(query, ROOT_SERVER)
tdl = ""
ip = ""

while True:
    # Check the response for answer
    if len(response.answer) > 0:
        print(response)
        break

    # Select Authority and its IP
    tld = response.authority[0][0].to_text()
    print(tld)

    # Get the IP of NS from additional
    ip = ""
    for addi in response.additional:
        if addi.name.to_text() == tld:
            print(addi[0].to_text())
            ip = addi[0].to_text()
            break


    tmp = dns.query.udp(query, ip)
    response = tmp
