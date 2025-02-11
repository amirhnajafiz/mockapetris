import dns.message
import dns.query
import dns.rcode
import dns.rdatatype
import dns.flags
import dns.rrset
import dns.dnssec
import dns.resolver
import dns.name

from .utils import qtype_map, is_valid_ipv4



class DNSResolver:
    """a major class that accepts parameters for `dig` and returns an object for dnssec resolve."""
    def __init__(self, roots: dict):
        """initializes the dns resolver with root servers.
        
        @params:
        - roots : dictionary, contains ip addresses of root dns servers
        """
        self.__roots = roots
        self.__stack = [ip for ip in roots.values()]  # create a stack with roots' ips as initial values

    def resolve(self, domain: str, qtype: str) -> tuple[dns.message.Message, bool]:
        """resolves the input domain and query type.
        
        @params:
        - domain : string, the domain to resolve
        - qtype : string, the query type (e.g., A, NS, MX)
        @returns:
        - tuple[dns.message.Message, bool], the dns response and a boolean indicating success
        """
        query = dns.message.make_query(domain, qtype_map(qtype), want_dnssec=True)  # create dns query
        
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
                if authority[0].rdtype != dns.rdatatype.NS:
                    continue

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

    def check_dnssec(self, domain: str) -> tuple[bool, bool, str, str]:
        """checks if the domain is DNSSEC protected.
        
        @params:
        - domain : string, the domain to check
        @returns:
        - bool, indicating if the domain is DNSSEC protected
        """
        # create a query for DNSKEY records
        query = dns.message.make_query(domain, dns.rdatatype.DNSKEY, want_dnssec=True)
        stack = [ip for ip in self.__roots.values()]  # create a stack with roots' ips as initial values

        while stack:
            # get the top ip address, check for ipv4 only
            ip = stack.pop()
            if not is_valid_ipv4(ip):
                continue

            # send the query to a DNS server (e.g., Google Public DNS)
            try:
                response = dns.query.udp(query, ip)
            except Exception as e:
                print(f"Error querying DNSKEY for {domain}: {e}")
                continue

            # check if the response contains DNSKEY records and if it is authenticated
            if response.flags & dns.flags.AD:
                # check if the response contains DNSKEY and RRSIG records
                dnskey_records = [rr for rrset in response.answer for rr in rrset if rrset.rdtype == dns.rdatatype.DNSKEY]
                rrsig_records = [rr for rrset in response.answer for rr in rrset if rrset.rdtype == dns.rdatatype.RRSIG]

                if dnskey_records and rrsig_records:
                    try:
                        # validate the DNSKEY records using RRSIG records
                        dnskey_rrset = dns.rrset.from_text_list(domain, 3600, dns.rdataclass.IN, dns.rdatatype.DNSKEY, [rr.to_text() for rr in dnskey_records])
                        rrsig_rrset = dns.rrset.from_text_list(domain, 3600, dns.rdataclass.IN, dns.rdatatype.RRSIG, [rr.to_text() for rr in rrsig_records])
                        dns.dnssec.validate(dnskey_rrset, rrsig_rrset, {dns.name.from_text(domain): dnskey_rrset})
                    except dns.dnssec.ValidationFailure:
                        print(f"Error querying DNSKEY for {domain}: {e}")
                        return False, False, "", ""
                    return True, False, dnskey_records[0].to_text(), rrsig_records[0].to_text()
                else:
                    print(f"DNSKEY or RRSIG records not found for {domain}")
                    continue
        
        return False, True, "", ""
    
    def check_delegation(self, domain: str) -> bool:
        """checks if the domain has DNSSEC delegation.
        
        @params:
        - domain : string, the domain to check
        @returns:
        - bool, indicating if the domain has DNSSEC delegation
        """
        # create a query for DS records
        parent_domain = dns.name.from_text(domain).parent().to_text()
        request = dns.message.make_query(parent_domain, dns.rdatatype.DS, want_dnssec=True)
        stack = [ip for ip in self.__roots.values()]  # create a stack with roots' ips as initial values

        while stack:
            # get the top ip address, check for ipv4 only
            ip = stack.pop()
            if not is_valid_ipv4(ip):
                continue

            try:
                # send the query to a DNS server (e.g., Google Public DNS)
                response = dns.query.udp(request, ip, timeout=5)
                if not response.answer:
                    response = dns.query.tcp(request, ip, timeout=5)
                if response.answer:
                    # validate the DS records
                    ds_records = [rr for rrset in response.answer for rr in rrset if rrset.rdtype == dns.rdatatype.DS]
                    if ds_records:
                        print(f"DS records for {parent_domain}: {ds_records[0].to_text()}")
                        return True
            except dns.resolver.NoAnswer:
                continue
        
        return False
