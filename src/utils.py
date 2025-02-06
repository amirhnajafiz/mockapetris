import dns.rdatatype



"""qtype_map
accepts an input of string and returns the rdatatype of that.
@params:
    - input : string
@returns:
    - dns.rdatatype
"""
def qtype_map(input : str) -> dns.rdatatype:
    if input == "NS":
        return dns.rdatatype.NS
    elif input == "MX":
        return dns.rdatatype.MX
    else:
        return dns.rdatatype.A
