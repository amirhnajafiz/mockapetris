# MyDIG

MyDIG is a simplified version of the `dig` command-line tool, designed to resolve DNS records. It also includes an application called `dnssec` for resolving DNSSEC records.

## Installation and Usage

To use MyDIG, first create a virtual environment and install the necessary dependencies (dnspython, cryptography, and matplotlib).

```sh
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

You can then run `mydig` and `dnssec` using `python` or `python3`. The output will also be saved in `mydig_output.txt` and `dnssec_output.txt`.

```sh
python3 mydig.py cs.stonybrook.edu A
# QUESTION SECTION:
# cs.stonybrook.edu. IN A
#
# ANSWER SECTION:
# cs.stonybrook.edu. 900 IN A 23.185.0.4
#
# Query time: 136.0 msec
# WHEN: 2025-02-11 21:19:58.034056
# MSG SIZE rcvd: 51 bytes

python3 mydig.py cs.stonybrook.edu NS
# QUESTION SECTION:
# cs.stonybrook.edu. IN NS

# AUTHORITY SECTION:
# cs.stonybrook.edu. 900 IN NS whoisthere.stonybrook.edu.
# cs.stonybrook.edu. 900 IN NS nocnoc.stonybrook.edu.
# cs.stonybrook.edu. 900 IN NS mewho.stonybrook.edu.

# Query time: 125.11 msec
# WHEN: 2025-02-11 21:21:59.737110
# MSG SIZE rcvd: 101 bytes

python3 mydig.py cs.stonybrook.edu MX
# QUESTION SECTION:
# cs.stonybrook.edu. IN MX

# AUTHORITY SECTION:
# cs.stonybrook.edu. 900 IN MX 10 aspmx2.googlemail.com.
# cs.stonybrook.edu. 900 IN MX 5 alt2.aspmx.l.google.com.
# cs.stonybrook.edu. 900 IN MX 5 alt1.aspmx.l.google.com.
# cs.stonybrook.edu. 900 IN MX 2 aspmx.l.google.com.
# cs.stonybrook.edu. 900 IN MX 10 aspmx3.googlemail.com.

# Query time: 128.55 msec
# WHEN: 2025-02-11 21:22:33.048771
# MSG SIZE rcvd: 168 bytes

python3 mydig.py google.co.jp A
# QUESTION SECTION:
# google.co.jp. IN A

# ANSWER SECTION:
# google.co.jp. 300 IN A 142.250.176.195

# Query time: 553.52 msec
# WHEN: 2025-02-11 21:23:16.451846
# MSG SIZE rcvd: 46 bytes
```

```sh
python3 dnssec.py paypal.com
# DNSKEY : 256 3 13 P82aHv27vjeEDMJUhvU8f02W9/Weblsv fMCL+ywMEJgD/9xsRStpOJhZC9EwZ4nQ BsP8rlA5rhyXZfBcgc877g==

# RRSIG : DNSKEY 13 2 172800 20250308215136 20250206212548 7037 paypal.com. YHYy9ckDkRhFe16Y7mnUylkEVm1aeTes 1Xw5P+J2Ch7eCAaj40W8qS7L+F9uGq+S A7IFcZhaRK4IO8mmgefxJw==

# DNSSEC is VALID

# DS records for com.: 19718 13 2 8acbb0cd28f41250a80a491389424d341522d946b0da0c0291f2d3d771d7805a
# DELEGATION SIGNER is VALID

# QUESTION SECTION:
# paypal.com. IN A

# ANSWER SECTION:
# paypal.com. 300 IN A 162.159.141.96
# paypal.com. 300 IN A 151.101.3.1
# paypal.com. 300 IN A 151.101.195.1
# paypal.com. 300 IN RRSIG A 13 2 300 20250309004624 20250207003739 23751 paypal.com. LEL/DIVOT9g9ofiIWVh2yI2TKddyRW1q oPaL9ltxFaYoUtqmLavjR28uJXZmKXGc 22PxfTboM/s8MxvXWpREQg==

# Query time: 695.77 msec
# WHEN: 2025-02-11 21:23:59.442088
# MSG SIZE rcvd: 411 bytes

python3 dnssec.py yahoo.com
# DNSSEC not supported

python3 dnssec.py dnssec-failed.org
# DNSSEC verification failed
```

## Benchmark

To compare the performance of MyDIG with your local DNS resolver and Google's public DNS resolver, you can run the `benchmark.py` script. This script tests MyDIG against the top 25 Alexa websites, selecting 5 of them, and runs each resolver 10 times on each site. It then calculates the average resolution time.

## Implementation

### DNS

For DNS resolution, MyDIG uses a simple query method with the `dnspython.query` library. The process involves reading a list of root DNS servers from a `roots.json` file. It then takes the domain name and query type from the user.

In the `src/resolver` directory, there is a `DNSResolver` class. This class uses the root servers to create a stack data structure. The goal is to make single UDP queries to each server, check the response, and if there is no answer, check the authority sections and add new nameservers to the stack. This process continues until an answer is found.

Here is a simplified example of how this works:

```python
stack = [ip for ip in roots.values()]  # Create a stack with root IPs
query = dns.message.make_query(domain, dns.rdatatype.A)  # Create a DNS query

while stack:
    ip = stack.pop()  # Get the top IP address
    if not is_valid_ipv4(ip):
        continue

    # Send a DNS request and check if the response is empty
    response = dns.query.udp(query, ip, timeout=2.0)
    if response.answer:
        return response, True
    
    # Add all authority servers
    for authority in response.authority:
        # First, check in additional sections
        for addi in response.additional:
            if addi.name.to_text() == authority[0].to_text():
                stack.append(addi[0].to_text())
                found = True
        
        # If not found, create a new resolver to find it
        if not found:
            ans, ok = self.resolve(name, "A")
            if ok:
                stack.append(ans.answer[0][0].to_text())
```

This algorithm starts with root servers, gets answers for TLDs, checks TLDs for future NSs, and continues adding NSs to the stack until it reaches the target.

### DNSSec

For DNSSec, MyDIG follows a similar method as DNS. However, after each `dns.query.udp`, it requests DNSSEC keys and makes a new query to get DNSKey. It then validates the result and checks the delegation signer to validate the chain of trust.

To modify the query for DNSSEC data:

```python
query = dns.message.make_query(domain, qtype_map(qtype), want_dnssec=True)  # Create a DNS query with DNSSEC
```

Then, check if the response contains DNSKEY and RRSIG records:

```python
if response.flags & dns.flags.AD:
    # Check if the response contains DNSKEY and RRSIG records
    rrsig_records = [rr for rrset in response.answer for rr in rrset if rrset.rdtype == dns.rdatatype.RRSIG]
```

Next, make another query to the parent to get DNSKEY:

```python
query = dns.message.make_query(domain, dns.rdatatype.DNSKEY, want_dnssec=True)  # Use DNSKEY type of query
```

Now, validate the signature using the fetched keys:

```python
# Fetch keys from rrset
dnskey_rrset = dns.rrset.from_text_list(domain, 3600, dns.rdataclass.IN, dns.rdatatype.DNSKEY, [rr.to_text() for rr in dnskey_records])
rrsig_rrset = dns.rrset.from_text_list(domain, 3600, dns.rdataclass.IN, dns.rdatatype.RRSIG, [rr.to_text() for rr in rrsig_records])

# Use dns.dnssec.validate method
dns.dnssec.validate(dnskey_rrset, rrsig_rrset, {dns.name.from_text(domain): dnskey_rrset})
```

If this validation succeeds, make a query to the parent to check for DNSSEC delegation:

```python
parent_domain = dns.name.from_text(domain).parent().to_text()  # Get the parent domain
request = dns.message.make_query(parent_domain, dns.rdatatype.DS, want_dnssec=True)  # Create a query
```

Then, make a UDP request. If it fails, perform a TCP request and check for DS record existence.

The overall method involves waiting for an answer at each step of resolving a host from root to TLD to NS. It extracts RRSig from the answer and makes a DNSKey query to get the key from the parent. Then, it validates the results and checks the Delegation signer by making a query to the zone parent. Since the root servers are provided by the `roots.json` file, it is assumed that these root servers are trustworthy. Therefore, the answers are checked after the root level.
