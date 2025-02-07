import dns.message
import dns.query
import ipaddress

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
    """class constructor"""
    def __init__(self, roots : dict, domain : str, qtype : str):
        self.__roots = roots

        # create an stack with roots' IPs as initial values
        self.__stack = []
        for ip in roots.values():
            self.__stack.append(ip)

        # create dns query
        self.__query = dns.message.make_query(domain, qtype_map(qtype))
    
    """checks if an input IP is type IPv4 or not"""
    def __is_valid_ipv4(self, ip_str):
        try:
            ipaddress.ip_address(ip_str)
            if isinstance(ipaddress.ip_address(ip_str), ipaddress.IPv4Address):
                return True
            else:
                return False
        except ValueError:
            return False

    """resolve the input domain and query_type"""
    def resolve(self) -> tuple[dns.message.Message, bool]:
        # start from the top of stack, send query until getting an answer
        while True:
            # exit if the stack is empty
            if len(self.__stack) == 0:
                break

            # get the top IP address, check for ipv4 only
            ip = self.__stack.pop()
            if not self.__is_valid_ipv4(ip):
                continue

            # send dns request and check response emptiness
            try:
                response = dns.query.udp(self.__query, ip, timeout=2.0)
                if response is None:
                    continue
                elif response.rcode() != dns.rcode.NOERROR:
                    return response, True
                elif len(response.answer) == 0 and len(response.authority) == 0:
                    continue
            except:
                continue

            # check the response for answer
            if len(response.answer) > 0:
                return response, True
            
            # add all authority servers
            for authority in response.authority:
                name = authority[0].to_text()
                found = False

                # first check in additionals
                for addi in response.additional:
                    if addi.name.to_text() == name:
                        self.__stack.append(addi[0].to_text())
                        found = True
                
                # if not found, then create a new resolver to find it
                if not found:
                    resolver = DNSResolver(self.__roots, name, "A")
                    ans, ok = resolver.resolve()
                    if ok:
                        self.__stack.append(ans.answer[0][0].to_text())
                        
        return None, False
