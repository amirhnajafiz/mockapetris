# MyDIG  

MyDIG is a simplified version of the `dig` command-line tool for resolving DNS records. It also includes a `dnssec` application for resolving DNSSEC records.  

## Installation and Usage  

To use MyDIG, first create a virtual environment and install the required dependencies:  

```sh
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Dependencies  

```txt
dnspython==2.7.0     # Handles DNS resolution queries  
cryptography==44.0.0 # Validates DNSSEC records  
matplotlib==3.10.0   # Supports benchmarking analysis  
```

### Running MyDIG  

You can run `mydig` and `dnssec` using `python` or `python3`. MyDIG performs DNS resolution iteratively, starting from the root servers specified in `configs/roots.json` and proceeding through TLDs and authoritative name servers until it retrieves a response.  

```sh
python3 mydig.py <domain> <query_type>
python3 mydig.py cs.stonybrook.edu A   # Resolves A records  
python3 mydig.py cs.stonybrook.edu NS  # Resolves NS records  
python3 mydig.py cs.stonybrook.edu MX  # Resolves MX records  
python3 mydig.py google.co.jp A        # Resolves A records for multiple domains  
```

### Running DNSSEC  

The `dnssec` application extends MyDIG by making additional queries for DNSKEY records. The root keys used for verification are provided in `configs/ksk.json`.  

DNSSEC validation depends on the root server, as well as TLDs and authoritative name servers. Some servers may not support DNSSEC or may provide invalid keys. To improve reliability, the application includes a `retrys` argument, which attempts alternative root servers and name servers if validation fails. Running the program multiple times with different retry thresholds may improve accuracy.  

```sh
python3 dnssec.py <domain> <retrys>  # Default retrys = 3
python3 dnssec.py paypal.com 3       # Resolves A records for paypal.com with up to 3 retries  
```

## Benchmarking  

To compare the performance of MyDIG with your local DNS resolver and Google’s public DNS resolver, you can use the `benchmark.py` script. This script tests MyDIG against the top 25 Alexa websites by selecting 5 of them and running each resolver 10 times per site. It then calculates the average resolution time.  
