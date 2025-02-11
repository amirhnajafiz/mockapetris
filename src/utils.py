import dns.rdatatype
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
    """checks if an input ip is type ipv4 or not"""
    try:
        return isinstance(ipaddress.ip_address(ip_str), ipaddress.IPv4Address)
    except ValueError:
        return False
