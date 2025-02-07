from datetime import datetime
import json
import sys
import time

from src.resolver import DNSResolver



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
    if not ok:
        print("NOT FOUND")
        sys.exit(1)
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

    print(f'\nQuery time: {round((end_time - start_time) * 1000, 2)} msec')
    print(f'WHEN: {execution_time}')
    print(f'MSG SIZE rcvd: {len(ans.to_wire())} bytes')
