import dns.message
import dns.query
import dns.rdatatype



# Choose a root name server (one of the 13 root servers)
ROOT_SERVER = "198.41.0.4"  # Example: a.root-servers.net

# Create a DNS query message for "example.com" (A record)
domain = "foo.com"
query = dns.message.make_query(domain, dns.rdatatype.A)

# Send query directly to the root name server
response = dns.query.udp(query, ROOT_SERVER)

# Select Authority and its IP
tld = response.authority[0][0].to_text()
print(tld)

ip = ""

for addi in response.additional:
    if addi.name.to_text() == tld:
        print(addi[0].to_text())
        ip = addi[0].to_text()
        break


response2 = dns.query.udp(query, ip)

# Select Authority and its IP
tld2 = response2.authority[0][0].to_text()
print(tld2)

ip2 = ""

for addi in response2.additional:
    if addi.name.to_text() == tld2:
        print(addi[0].to_text())
        ip2 = addi[0].to_text()
        break


response3 = dns.query.udp(query, ip2)
print(response3)