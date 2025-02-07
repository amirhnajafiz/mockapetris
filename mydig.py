from datetime import datetime
import json
import sys
import time

from src.resolver import DNSResolver
from src.tee import Tee



# set the program stdout to `mydig_output.txt`
sys.stdout = Tee("mydig_output.txt")
print("----------------")
print(' '.join(sys.argv))

# read roots from `roots.json` file
with open('roots.json', 'r') as f:
    roots = json.load(f)

if __name__ == "__main__":
    # check for command line arguments
    if len(sys.argv) < 3:
        print("not enough input arguments: mydig <domain> <query_type>")
        sys.exit(1)

    domain = sys.argv[1]
    qtype = sys.argv[2]

    # create a resolver instance
    resolver = DNSResolver(roots, domain, qtype)
    execution_time = datetime.now()

    # get the answer
    start_time = time.time()
    ans, ok = resolver.resolve()
    end_time = time.time()

    # check for response status
    if not ok:
        print("ERROR, QUERY NOT FOUND")
    else:
        print("\nQUESTION SECTION:")
        for q in ans.question:
            print(q.to_text())

        if qtype == "MX" or qtype == "NS":
            print("\nAUTHORITY SECTION:")
        else:
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
