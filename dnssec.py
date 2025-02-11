from datetime import datetime
import json
import sys
import time

from src.sec import DNSResolver
from src.tee import Tee



def main():
    # set the program stdout to `dnssec_output.txt`
    sys.stdout = Tee("dnssec_output.txt")
    print("----------------")
    print(' '.join(sys.argv))

    # read roots from `roots.json` file
    try:
        with open('roots.json', 'r') as f:
            roots = json.load(f)
    except FileNotFoundError:
        print("ERROR: roots.json file not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("ERROR: failed to parse roots.json.")
        sys.exit(1)

    # check for command line arguments
    if len(sys.argv) < 2:
        print("not enough input arguments: mydig <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    qtype = "A"

    # create a resolver instance
    resolver = DNSResolver(roots)
    execution_time = datetime.now()

    # get the answer
    start_time = time.time()
    ans, ok = resolver.resolve(domain, qtype)
    end_time = time.time()

    # check for response status
    if not ok:
        print("ERROR, QUERY NOT FOUND")
    else:
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
    if ok:
        print(f'\nQuery time: {round((end_time - start_time) * 1000, 2)} msec')
        print(f'WHEN: {execution_time}')
        print(f'MSG SIZE rcvd: {len(ans.to_wire())} bytes')
    else:
        print(f'\nQuery time: {round((end_time - start_time) * 1000, 2)} msec')
        print(f'WHEN: {execution_time}')


if __name__ == "__main__":
    main()
