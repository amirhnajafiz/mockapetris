import json
import sys

from src.resolver import DNSResolver



# Read roots from `roots.json`
roots = {}
with open('roots.json', 'r') as f:
    roots = json.load(f)

domain = "cs.stonybrook.edu"
qtype = "A"

resolver = DNSResolver(roots, domain, qtype)

ans, ok = resolver.resolve()
if not ok:
    sys.exit(1)
else:
    print(ans)
