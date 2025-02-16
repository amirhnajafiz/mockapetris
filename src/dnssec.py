import dns.message
import dns.name
import dns.query
import dns.rdatatype
import dns.dnssec
import dns.opcode
import dns.rcode
import dns.flags

from .utils import check_a_record, get_rrset, get_dnskey



def is_zone_verified(parent_ds_rrset, ksk):
    hash_algo = 'SHA256' if parent_ds_rrset is None else ('SHA256' if parent_ds_rrset[0].digest_type == 2 else 'SHA1')
    parent_ds_hash = '20326 8 2 E06D44B80B8F1D39A95C0B0D7C65D08458E880409BBC683457104237C7F8EC8D'.lower() if parent_ds_rrset is None else parent_ds_rrset[0].to_text()
    zone = '.' if parent_ds_rrset is None else parent_ds_rrset.name.to_text()
    try:
        hash = dns.dnssec.make_ds(name = zone, key = ksk, algorithm = hash_algo).to_text()
    except dns.dnssec.ValidationFailure as e:
        print("Hash Algorithm {} not supported: {}".format(hash_algo, e))
        return False
    else:
        if hash == parent_ds_hash:
            if zone == '.':
                print("The PubKSK digest matches the root anchor key digest. Hence, Root Zone '{}' successfully verified".format(zone))
            else:
                print("The PubKSK digest matches the DS record from the parent zone. Hence, zone '{}' successfully verified".format(zone))
            return True
        else:
            print("The PubKSK digest(s) of the '{}' zone cannot be verified by the DS record from its parent zone. Hence, "
            "DNSSec verification failed for zone '{}'".format(zone, zone))
            return False

def is_dnskey_rrset_verified(dnskey_rrset, dnskey_rrsig):
    try:
        dns.dnssec.validate(rrset = dnskey_rrset, rrsigset = dnskey_rrsig, keys = {dnskey_rrset.name: dnskey_rrset})
    except dns.dnssec.ValidationFailure as e:
        print("DNSSec verification failed during DNSKey RRSet Verification for '{}' zone: {}\n".format(dnskey_rrset.name.to_text(), e))
        return False
    else:
        print("Found {} DNSKey record(s) for zone '{}', which has been verified with its corresponding RRSig by the PubKSK".format(
            len(dnskey_rrset.items), dnskey_rrset.name.to_text()))
        return True

def is_ds_or_a_rrset_verified(zone_rrset, zone_rrsig, dnskey_rrset):
    try:
        dns.dnssec.validate(rrset = zone_rrset, rrsigset = zone_rrsig, keys = {dnskey_rrset.name: dnskey_rrset})
    except dns.dnssec.ValidationFailure as e:
        print("DNSSec verification failed during DS/A RRSet Verification for '{}' zone: {}\n".format(dnskey_rrset.name.to_text(), e))
        return False
    else:
        print("Found {} DS/A record(s) for zone '{}', which has been verified with its corresponding RRSig by the PubZSK\n".format(
            len(zone_rrset.items), dnskey_rrset.name.to_text()))
        return True

def dnssec_validated(dns_response, dnskey_response, parent_ds_rrset, contains_a_record):
    dnskey_rrsig = get_rrset(dnskey_response.answer, dns.rdatatype.RRSIG)
    dnskey_rrset, ksk = get_dnskey(dnskey_response.answer)

    rr_section, rrset_type = (dns_response.answer, dns.rdatatype.A) if contains_a_record else (dns_response.authority, dns.rdatatype.DS)

    zone_rrsig = get_rrset(rr_section, dns.rdatatype.RRSIG)
    zone_rrset = get_rrset(rr_section, rrset_type)

    if zone_rrset is None:
        print("Could not find the DS record for the child zone from the parent '{}' zone. Hence, DNSSEC "
              "not supported by this domain".format(parent_ds_rrset.name.to_text()))
        return False, zone_rrset
    
    if not is_zone_verified(parent_ds_rrset, ksk):
        print("Zone DNSSEC verification failed for the '{}' zone".format(parent_ds_rrset.name.to_text()))
        return False, zone_rrset
    
    if not is_dnskey_rrset_verified(dnskey_rrset, dnskey_rrsig):
        print("DNSKEY DNSSEC verification failed for the '{}' zone".format(dnskey_rrset.name.to_text()))
        return False, zone_rrset
    
    if not is_ds_or_a_rrset_verified(zone_rrset, zone_rrsig, dnskey_rrset):
        print("DS DNSSEC verification failed for the '{}' zone".format(dnskey_rrset.name.to_text()))
        return False, zone_rrset
    
    return True, zone_rrset

def query(domain_name, rd_type, name_server, dnssec_flag):
    query = dns.message.make_query(dns.name.from_text(domain_name), rd_type, want_dnssec = dnssec_flag)
    try:
        dns_response = dns.query.udp(q = query, where = name_server, timeout = 2)
        return dns_response
    except Exception as e:
        raise e

def resolve(root_servers, domain_name, rd_type, resolve_cname=False, return_A_record=False):
    dns_response = None

    for root_server in root_servers:
        try:
            root_dnskey_response = query('.', dns.rdatatype.DNSKEY, name_server=root_server, dnssec_flag=True)
            root_dns_response = query(domain_name, rd_type, name_server=root_server, dnssec_flag=True)
            dns_response = root_dns_response
        except Exception as e:
            print(f"Error when fetching DNSKey from Root Server {root_server}. Error: {e}")
            continue

        contains_a_record = check_a_record(root_dns_response.answer)
        root_validated, root_ds_rrset = dnssec_validated(root_dns_response, root_dnskey_response, None, contains_a_record)
        if not root_validated:
            continue

        threshold = 0
        parent_ds_rrset = root_ds_rrset
        while not dns_response.answer:
            threshold += 1
            if threshold > 3:
                print("Threshold reached. Could not resolve domain name")
                return dns_response

            if dns_response.additional:
                for rrset in dns_response.additional:
                    if rrset[0].rdtype == dns.rdatatype.A:
                        next_ns_ip_addr = rrset[0].address
                        try:
                            ns_dnskey_response = query(parent_ds_rrset.name.to_text(), dns.rdatatype.DNSKEY, name_server=next_ns_ip_addr, dnssec_flag=True)
                            ns_dns_response = query(domain_name, rd_type, name_server=next_ns_ip_addr, dnssec_flag=True)

                            contains_a_record = check_a_record(ns_dns_response.answer)
                            ns_validated, ns_ds_rrset = dnssec_validated(ns_dns_response, ns_dnskey_response, parent_ds_rrset, contains_a_record)
                            if not ns_validated:
                                continue
                            parent_ds_rrset = ns_ds_rrset

                            if resolve_cname and ns_dns_response.answer and ns_dns_response.answer[0].rdtype == dns.rdatatype.CNAME:
                                return ns_dns_response
                            elif return_A_record and ns_dns_response.answer and ns_dns_response.answer[0].rdtype == dns.rdatatype.A:
                                return ns_dns_response
                            dns_response = ns_dns_response
                            break

                        except Exception as e:
                            print(f"Error when fetching from Name Server {rrset.name.to_text()} with IP {next_ns_ip_addr}. Error: {e}")
            elif dns_response.authority:
                for rrset in dns_response.authority:
                    if rrset.rdtype == dns.rdatatype.SOA:
                        return dns_response
                    ns_domain_name = rrset[0].target.to_text()
                    print(f"Iteratively resolving IP of Authoritative Name Server {ns_domain_name}")
                    ns_dns_response = resolve(ns_domain_name, 'A', return_A_record=True)
                    if not resolve_cname:
                        for auth_rrset in ns_dns_response.answer:
                            auth_ip_addr = auth_rrset[0].address
                            print(f"IP address for Authoritative Name Server {ns_domain_name} was found to be {auth_ip_addr}")
                            try:
                                auth_dnskey_response = query(parent_ds_rrset.name.to_text(), dns.rdatatype.DNSKEY, name_server=auth_ip_addr, dnssec_flag=True)
                                auth_dns_response = query(domain_name, rd_type, name_server=auth_ip_addr, dnssec_flag=True)

                                contains_a_record = check_a_record(auth_dns_response.answer)
                                auth_validated, auth_ds_rrset = dnssec_validated(auth_dns_response, auth_dnskey_response, parent_ds_rrset, contains_a_record)
                                if not auth_validated:
                                    continue

                                parent_ds_rrset = auth_ds_rrset
                                dns_response = auth_dns_response
                            except Exception as e:
                                print(f"Error when fetching from Authoritative Server {auth_ip_addr} with IP {auth_rrset.name.to_text()}. Error: {e}")
                    else:
                        return ns_dns_response

        for rrset in dns_response.answer:
            if dns.rdatatype.from_text(rd_type).value == dns.rdatatype.A and (rrset.rdtype == dns.rdatatype.A or rrset.rdtype == dns.rdatatype.SOA):
                return dns_response

    return dns_response
