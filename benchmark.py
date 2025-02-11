import subprocess
import time
import socket
import dns.resolver

# list of 5 websites from https://www.alexa.com/topsites
sites = [
    "https://www.google.com",
    "https://www.youtube.com",
    "https://www.facebook.com",
    "https://www.baidu.com",
    "https://www.wikipedia.org",
    "https://www.qq.com",
    "https://www.paypal.com",
    "https://www.jd.com",
    "https://www.yahoo.com",
    "https://www.amazon.com",
    "https://www.twitter.com",
    "https://www.instagram.com",
    "https://www.weibo.com",
    "https://www.sina.com.cn",
    "https://www.linkedin.com",
    "https://www.360.cn",
    "https://www.reddit.com",
    "https://www.microsoft.com",
    "https://www.bing.com",
    "https://www.office.com",
    "https://www.live.com",
    "https://www.alipay.com",
    "https://www.wordpress.com",
    "https://www.sohu.com",
    "https://www.ebay.com"
]

print(len(sites))

# this script benchmarks the time taken to resolve DNS for each site using mydig.py
def run_mydig(site):
    start_time = time.time()
    subprocess.run(["python3", "mydig.py", site], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    end_time = time.time()
    return end_time - start_time

# this script benchmarks the time taken to resolve DNS for each site using local DNS resolver
def run_local_dns(site):
    start_time = time.time()
    try:
        socket.gethostbyname(site)
    except socket.gaierror:
        pass
    end_time = time.time()
    return end_time - start_time

# this script benchmarks the time taken to resolve DNS for each site using Google's public DNS
def run_google_dns(site):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['8.8.8.8', '8.8.4.4']
    start_time = time.time()
    try:
        resolver.resolve(site)
    except (dns.resolver.NoNameservers, dns.resolver.NXDOMAIN, dns.resolver.Timeout):
        pass
    end_time = time.time()
    return end_time - start_time

# run the benchmark for each site 10 times and calculate the average time
def average_time(site, run_function, runs=10):
    total_time = 0
    for _ in range(runs):
        total_time += run_function(site)
    return total_time / runs

# print the local DNS name
local_dns_name = socket.getfqdn()
print(f"Local DNS name: {local_dns_name}")

# run the benchmark for each site and print the average time using local DNS resolver
for site in sites:
    avg_time = average_time(site, run_mydig)
    print(f"Average time to resolve DNS for {site} using mydig.py: {avg_time:.4f} seconds")
    avg_local_time = average_time(site, run_local_dns)
    print(f"Average time to resolve DNS for {site} using local DNS resolver {local_dns_name}: {avg_local_time:.4f} seconds")
    avg_google_time = average_time(site, run_google_dns)
    print(f"Average time to resolve DNS for {site} using Google's public DNS: {avg_google_time:.4f} seconds")
