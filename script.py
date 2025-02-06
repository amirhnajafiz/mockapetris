import json
import sys

from src.resolver import DNSResolver



# read roots from `roots.json`
with open('roots.json', 'r') as f:
    roots = json.load(f)

domain = "cs.stonybrook.edu"
qtype = "A"

if __name__ == "__main__":
    # create a resolver instance
    resolver = DNSResolver(roots, domain, qtype)

    # get the answer
    ans, ok = resolver.resolve()
    if not ok:
        sys.exit(1)
    else:
        print(ans)
