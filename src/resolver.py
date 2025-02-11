import dns.message
import dns.query
import dns.rcode

from .utils import qtype_map, is_valid_ipv4



class DNSResolver:
    """a major class that accepts parameters for `dig` and returns an object for dns resolve."""
    def __init__(self, roots: dict):
        """initializes the dns resolver with root servers.
        
        @params:
        - roots : dictionary, contains ip addresses of root dns servers
        """
        self.__stack = [ip for ip in roots.values()]  # create a stack with roots' ips as initial values

    def resolve(self, domain: str, qtype: str) -> tuple[dns.message.Message, bool]:
        """resolves the input domain and query type.
        
        @params:
        - domain : string, the domain to resolve
        - qtype : string, the query type (e.g., A, NS, MX)
        @returns:
        - tuple[dns.message.Message, bool], the dns response and a boolean indicating success
        """
        query = dns.message.make_query(domain, qtype_map(qtype))  # create dns query
        
        # start from the top of stack, send query until getting an answer
        while self.__stack:
            # get the top ip address, check for ipv4 only
            ip = self.__stack.pop()
            if not is_valid_ipv4(ip):
                continue

            # send dns request and check response emptiness
            try:
                response = dns.query.udp(query, ip, timeout=2.0)
                if response is None:
                    continue
                elif response.rcode() != dns.rcode.NOERROR:
                    return response, True
                elif not response.answer and not response.authority:
                    continue
            except Exception as e:
                continue

            # check the response for answer
            if response.answer:
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
                    ans, ok = self.resolve(name, "A")
                    if ok:
                        self.__stack.append(ans.answer[0][0].to_text())
                        
        return None, False
