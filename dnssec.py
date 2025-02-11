from datetime import datetime
import json
import sys
import time

from src.dnssec import DNSResolver
from src.tee import Tee



def load_roots(filename):
    """loads roots from roots.json file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("error: roots.json file not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("error: failed to parse roots.json.")
        sys.exit(1)

def validate_args(argv):
    """checks if command line arguments are sufficient"""
    if len(argv) < 2:
        print("not enough input arguments: mydig <domain>")
        sys.exit(1)
    return argv[1]

def resolve_domain(resolver, domain, qtype):
    """resolves a domain using the given resolver"""
    start_time = time.time()
    ans, ok = resolver.resolve(domain, qtype)
    end_time = time.time()
    return ans, ok, start_time, end_time

def print_response(ans, ok, resolver):
    """prints the dns response"""
    if not ok:
        print("error, query not found")
    else:
        # check dnssec and delegation
        if len(ans.answer) != 0:
            res, err, dnskey, rrsig = resolver.check_dnssec(ans.answer[0].name.to_text())
        else:
            res, err, dnskey, rrsig = resolver.check_dnssec(ans.question[0].name.to_text())
        
        # check if dnssec is valid
        if err:
            # check if the answer contins DNSKEY or RRSIG records
            if len(ans.answer) == 0:
                print("DNSSEC not supported")
                sys.exit(1)
            else:
                # check if the answer contains DNSKEY or RRSIG records
                for an in ans.answer:
                    if an.rdtype == 257 or an.rdtype == 46:
                        print("DNSSEC verification failed")
                        sys.exit(1)
                print("DNSSEC not supported")
                sys.exit(1)
        elif not res:
            print("ERROR, DNSSEC not valid")
            sys.exit(1)
        else:
            print(f'\nDNSKEY : {dnskey}')
            print(f'\nRRSIG : {rrsig}')
            print("\nDNSSEC is VALID\n")
        
        if not resolver.check_delegation(ans.answer[0].name.to_text()):
            print("error, delegation not valid")
            sys.exit(1)
        else:
            print("DELEGATION SIGNER is VALID")

        # print sections
        print("\nQUESTION SECTION:")
        for q in ans.question:
            print(q.to_text())

        print("\nANSWER SECTION:")
        for an in ans.answer:
            print(an.to_text())

        if len(ans.additional) > 0:
            print("\nADDITIONAL SECTION:")
            for ad in ans.additional:
                print(ad.to_text())

def print_metadata(start_time, end_time, execution_time, ans, ok):
    """prints metadata about the query"""
    if ok:
        print(f'\nQuery time: {round((end_time - start_time) * 1000, 2)} msec')
        print(f'WHEN: {execution_time}')
        print(f'MSG SIZE rcvd: {len(ans.to_wire())} bytes')
    else:
        print(f'\nQuery time: {round((end_time - start_time) * 1000, 2)} msec')
        print(f'WHEN: {execution_time}')

def main():
    # set the program stdout to `dnssec_output.txt`
    sys.stdout = Tee("dnssec_output.txt")
    print("----------------")
    print(' '.join(sys.argv))

    # load roots
    roots = load_roots('roots.json')

    # validate and parse command line arguments
    domain = validate_args(sys.argv)
    qtype = "A"

    # create a resolver instance
    resolver = DNSResolver(roots)
    execution_time = datetime.now()

    # resolve the domain
    ans, ok, start_time, end_time = resolve_domain(resolver, domain, qtype)

    # print response and metadata
    print_response(ans, ok, resolver)
    print_metadata(start_time, end_time, execution_time, ans, ok)

if __name__ == "__main__":
    main()
