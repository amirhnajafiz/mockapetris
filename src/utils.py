import dns.rdatatype
import dns.rrset
import ipaddress



def qtype_map(input: str) -> dns.rdatatype:
    """maps a string to the corresponding dns rdatatype.
    
    @params:
    - input : string (e.g., "NS", "MX", "A")
    @returns:
    - dns.rdatatype
    """
    qtype_map_dict = {
        "NS": dns.rdatatype.NS,
        "MX": dns.rdatatype.MX,
        "A": dns.rdatatype.A
    }
    
    # default to dns.rdatatype.A if input is not recognized
    return qtype_map_dict.get(input, dns.rdatatype.A)


def is_valid_ipv4(ip_str: str) -> bool:
    """checks if an input ip is type ipv4 or not.
    
    @params:
    - ip_str : string
    @returns:
    - bool
    """
    try:
        return isinstance(ipaddress.ip_address(ip_str), ipaddress.IPv4Address)
    except ValueError:
        return False


def check_a_record(answer: dns.rrset) -> bool:
    """checks if the answer section contains an A record.

    @params:
    - answer : dns.rrset
    @returns:
    - bool
    """
    for rrset in answer:
        if rrset.rdtype == dns.rdatatype.A:
            return True

    return False


def get_rrset(section: dns.rrset, rdtype: dns.rdatatype) -> dns.rrset:
    """returns the specified RRSet from the section.

    @params:
    - section : dns.rrset
    - rdtype : dns.rdatatype
    @returns:
    - dns.rrset
    """
    for rrset in section:
        if rrset.rdtype == rdtype:
            return rrset
    return None


def get_dnskey(answer: dns.rrset) -> tuple[dns.rrset.RRset, dns.rrset.RRset]:
    """returns the DNSKEY RRSet and the KSK from the answer section.

    @params:
    - answer : dns.rrset
    @returns:
    - dns.rrset, dns.rrset
    """
    for rrset in answer:
        if rrset.rdtype == dns.rdatatype.DNSKEY:
            for rr in rrset:
                if rr.flags == 257:
                    return rrset, rr
    return None, None
