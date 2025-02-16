import dns.message
import dns.name
import dns.query
import dns.rdatatype
import dns.dnssec
import dns.opcode
import dns.rcode
import dns.flags
import dns.rrset

from .utils import get_rrset, get_dnskey, query



def zone_validation(rrset: dns.rrset.RRset, ksk: dns.rrset.RRset) -> bool:
    """validates the zone by comparing the DS record of the parent zone with the PubKSK of the child zone.
    
    @params:
    - rrset : dns.rrset.RRset
    - ksk : dns.rrset.RRset
    @returns:
    - bool
    """
    # selecting the hash algorithm based on the digest type of the DS record
    method = 'SHA256' if rrset is None else ('SHA256' if rrset[0].digest_type == 2 else 'SHA1')
    # getting the DS record from the parent zone
    phash = '20326 8 2 E06D44B80B8F1D39A95C0B0D7C65D08458E880409BBC683457104237C7F8EC8D'.lower() if rrset is None else rrset[0].to_text()
    # getting the zone name
    zone = '.' if rrset is None else rrset.name.to_text()

    try:
        # generating the DS record from the PubKSK of the child
        hash = dns.dnssec.make_ds(name = zone, key = ksk, algorithm = method).to_text()
    except dns.dnssec.ValidationFailure as e:
        print(e)
        return False
    
    # comparing the DS record of the parent zone with the PubKSK of the child zone
    if hash == phash:
        return True
    else:
        print("DS record of the parent zone does not match with the PubKSK of the child zone")
        return False


def dnskey_validation(rrset: dns.rrset.RRset, rrsig: dns.rrset.RRset) -> bool:
    """validates the DNSKEY RRSet by verifying the RRSig with the PubZSK.
    
    @params:
    - rrset : dns.rrset.RRset
    - rrsig : dns.rrset.RRset
    @returns:
    - bool
    """
    try:
        # validating the DNSKEY RRSet by verifying the RRSig with the PubZSK
        dns.dnssec.validate(rrset=rrset, rrsigset=rrsig, keys={rrset.name: rrset})
    except dns.dnssec.ValidationFailure as e:
        print(e)
        print("DNSSEC verification failed")
        return False

    return True


def ds_validation(rrset: dns.rrset.RRset, rrsig: dns.rrset.RRset, dnskey: dns.rrset.RRset) -> bool:
    """validates the DS RRSet by verifying the RRSig with the DNSKEY RRSet.
    
    @params:
    - rrset : dns.rrset.RRset
    - rrsig : dns.rrset.RRset
    - dnskey : dns.rrset.RRset
    @returns:
    - bool
    """
    try:
        # validating the DS RRSet by verifying the RRSig with the DNSKEY RRSet
        dns.dnssec.validate(rrset = rrset, rrsigset = rrsig, keys = {dnskey.name: dnskey})
    except dns.dnssec.ValidationFailure as e:
        print(e)
        print("DNSSEC verification failed")
        return False

    return True


def dnssec_validation(response: dns.rrset.RRset, dnskey: dns.rrset.RRset, ds_rrset: dns.rrset.RRset) -> tuple[bool, dns.rrset.RRset]:
    """validates the DNSSEC response.
    
    @params:
    - response : dns.rrset.RRset
    - dnskey : dns.rrset.RRset
    - ds_rrset : dns.rrset.RRset
    @returns:
    - tuple[bool, dns.rrset.RRset]
    """
    # check if the response has an A record
    has_a_record = False
    for rrset in response.answer:
        if rrset.rdtype == dns.rdatatype.A:
            has_a_record = True
            break

    # get the DNSKEY RRSet and the KSK from the answer section
    dnskey_rrsig = get_rrset(dnskey.answer, dns.rdatatype.RRSIG)
    dnskey_rrset, ksk = get_dnskey(dnskey.answer)
    rr_section, rrset_type = (response.answer, dns.rdatatype.A) if has_a_record else (response.authority, dns.rdatatype.DS)

    # get the DS RRSet and the RRSig from the answer section
    rrsig = get_rrset(rr_section, dns.rdatatype.RRSIG)
    rrset = get_rrset(rr_section, rrset_type)

    # validate the zone
    if rrset is None:
        print("DNSSEC not supported")
        return False, rrset
    
    # validate the zone
    if not zone_validation(ds_rrset, ksk):
        print("DNSSEC validation failed (zone validation)")
        return False, rrset
    
    # validate the DNSKEY RRSet
    if not dnskey_validation(dnskey_rrset, dnskey_rrsig):
        print("DNSSEC validation failed (DNSKEY validation)")
        return False, rrset
    
    # validate the DS RRSet
    if not ds_validation(rrset, rrsig, dnskey_rrset):
        print("DNSSEC validation failed (DS validation)")
        return False, rrset
    
    print("[INFO] DNSSEC validation successful")
    
    return True, rrset


def resolve(roots: list, domain: str, qtype: dns.rdatatype, retrys: int, CNAME: bool = False, RAR: bool = False) -> tuple[dns.message.Message, bool]:
    """resolves the domain name iteratively.
    
    @params:
    - roots : list
    - domain : string
    - qtype : dns.rdatatype
    - retrys : int
    - CNAME : bool
    - RAR : bool
    @returns:
    - tuple[dns.message.Message, bool]
    """
    # iterate over the root servers
    for ip in roots:
        dns_response = None

        # query the root server
        try:
            root_dnskey_response = query('.', dns.rdatatype.DNSKEY, ip, True)
            root_dns_response = query(domain, qtype, ip, True)
            dns_response = root_dns_response
        except Exception as e:
            print(e)
            continue

        # validate the DNSSEC response
        print(f"[INFO] validating root {ip} DNSSEC for {domain}")
        root_validated, root_ds_rrset = dnssec_validation(root_dns_response, root_dnskey_response, None)
        if not root_validated:
            continue

        threshold = 0
        parent_ds_rrset = root_ds_rrset

        # loop until the response has an answer
        while True:
            # check if the response has an answer
            if dns_response.answer:
                break

            # check if the threshold is reached
            threshold += 1
            if threshold > retrys:
                print("[ERROR] Retry threshold reached, could not resolve domain name.")
                return dns_response, False

            # iterate over the additional section
            if dns_response.additional:
                for rrset in dns_response.additional:
                    if rrset[0].rdtype == dns.rdatatype.A:
                        # get the IP address of the next authoritative name server
                        next_ip = rrset[0].address
                        try:
                            # query the next authoritative name server
                            ns_dnskey_response = query(parent_ds_rrset.name.to_text(), dns.rdatatype.DNSKEY, next_ip, True)
                            ns_dns_response = query(domain, qtype, next_ip, True)

                            # validate the DNSSEC response
                            print(f"[INFO] validating {next_ip} DNSSEC for {domain}")
                            ns_validated, ns_ds_rrset = dnssec_validation(ns_dns_response, ns_dnskey_response, parent_ds_rrset)
                            if not ns_validated:
                                continue

                            # update the parent DS RRSet
                            parent_ds_rrset = ns_ds_rrset
                            dns_response = ns_dns_response

                            # check if the response has a CNAME record
                            if CNAME and ns_dns_response.answer and ns_dns_response.answer[0].rdtype == dns.rdatatype.CNAME:
                                return ns_dns_response, True
                            elif RAR and ns_dns_response.answer and ns_dns_response.answer[0].rdtype == dns.rdatatype.A:
                                return ns_dns_response, True
                            
                            break
                        except Exception as e:
                            print(e)
            
            # check if the response has an authority section with a SOA record
            if dns_response.authority and dns_response.authority[0].rdtype == dns.rdatatype.SOA:
                break

        # check if the response has an A record
        for rrset in dns_response.answer:
            if dns.rdatatype.from_text(qtype).value == dns.rdatatype.A and (rrset.rdtype == dns.rdatatype.A or rrset.rdtype == dns.rdatatype.SOA):
                return dns_response, True

    return dns_response, True
