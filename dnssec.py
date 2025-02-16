import json
import sys
import time
from datetime import datetime

from src.dnssec import resolve



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


if __name__ == '__main__':
    # check for command line arguments
    if len(sys.argv) < 2:
        print("not enough input arguments: dnssec <domain>")
        sys.exit(1)

    # load the roots
    roots = load_roots('configs/roots.json')

    # set execution time
    execution_time = datetime.now()

    # get the domain name and rdtype
    domain_name = sys.argv[1]
    rdtype = "A"
    
    # begin the resolution process
    start_time = time.time()
    ans = resolve(list(roots.values()), domain_name, rdtype)
    end_time = time.time()

    # check if the domain name was resolved
    if ans is None:
        print("Error: Could not resolve domain name")
        sys.exit(1)

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

    # print metadata
    print(f'\nQuery time: {round((end_time - start_time) * 1000, 2)} msec')
    print(f'WHEN: {execution_time}')
    print(f'MSG SIZE rcvd: {len(ans.to_wire())} bytes')
