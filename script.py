import json
import sys

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

    # get the answer
    ans, ok = resolver.resolve()
    if not ok:
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
