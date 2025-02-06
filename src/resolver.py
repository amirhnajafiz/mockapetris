import dns.message
import dns.query
from .utils import qtype_map



"""DNSResolver
A major class that accepts parameters for `dig` and returns an object
for DNS resolve.
@params
    - roots : dictionary
    - domain : string
    - qtype: string (enum: A, NS, MX)
"""
class DNSResolver:
    def __init__(self, roots : dict, domain : str, qtype : str):
        self.index = 0
        self.roots = list(roots.items())
        self.query = dns.message.make_query(domain, qtype_map(qtype))

    def resolve(self) -> tuple[dns.message.Message, bool]:
        # check the index limit
        if self.index == len(self.roots):
            return None, False

        # get one root address
        root_ip = self.roots[self.index][1]
        self.index += 1

        # call the root DNS
        response = dns.query.udp(self.query, root_ip)
        if len(response.answer) == 0 and len(response.authority) == 0:
            return None, True

        # loop variables
        tld = ""
        tld_ip = ""

        while True:
            # check the response for answer
            if len(response.answer) > 0:
                return response, True

            # select authority and its IP
            tld = response.authority[0][0].to_text()
            print(tld)

            # get the IP of NS from additional
            for addi in response.additional:
                if addi.name.to_text() == tld:
                    print(addi[0].to_text())
                    tld_ip = addi[0].to_text()
                    break
            
            # make a new call to the next
            response = dns.query.udp(self.query, tld_ip)
