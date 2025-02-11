import subprocess
import time
import dns.resolver
import matplotlib.pyplot as plt



# a global variable to store the local DNS server
local_dns = ""

# list of 5 websites from https://www.alexa.com/topsites
sites = [
    "https://www.google.com",
    "https://www.youtube.com",
    "https://www.facebook.com",
    "https://www.baidu.com",
    "https://www.wikipedia.org",
    # "https://www.qq.com",
    # "https://www.paypal.com",
    # "https://www.jd.com",
    # "https://www.yahoo.com",
    # "https://www.amazon.com",
    # "https://www.twitter.com",
    # "https://www.instagram.com",
    # "https://www.weibo.com",
    # "https://www.sina.com.cn",
    # "https://www.linkedin.com",
    # "https://www.360.cn",
    # "https://www.reddit.com",
    # "https://www.microsoft.com",
    # "https://www.bing.com",
    # "https://www.office.com",
    # "https://www.live.com",
    # "https://www.alipay.com",
    # "https://www.wordpress.com",
    # "https://www.sohu.com",
    # "https://www.ebay.com"
]

# this script benchmarks the time taken to resolve DNS for each site using mydig.py
def run_mydig(site):
    start_time = time.time()
    subprocess.run(["python3", "mydig.py", site], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    end_time = time.time()
    return end_time - start_time

# this script benchmarks the time taken to resolve DNS for each site using local DNS resolver
def run_local_dns(site):
    resolver = dns.resolver.Resolver()
    # get the resolver nameserver and set it to the local DNS server
    global local_dns
    if local_dns == "":
        try:
            local_dns = resolver.nameservers[0]
        except IndexError:
            print("No local DNS server found.")
            return 0

    start_time = time.time()
    try:
        resolver.resolve(site)
    except (dns.resolver.NoNameservers, dns.resolver.NXDOMAIN, dns.resolver.Timeout):
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

# print the number of sites
print(f"number of sites: {len(sites)}")

# collect data for plotting
site_names = [site.split("//")[1] for site in sites]
mydig_times = [average_time(site, run_mydig) for site in sites]
local_dns_times = [average_time(site, run_local_dns) for site in sites]
google_dns_times = [average_time(site, run_google_dns) for site in sites]

# [lot the data
plt.figure(figsize=(15, 8))
plt.plot(site_names, mydig_times, label='mydig.py', marker='o')
plt.plot(site_names, local_dns_times, label=f'Local DNS {local_dns}', marker='o')
plt.plot(site_names, google_dns_times, label="Google's public DNS", marker='o')

# add labels and title
plt.xlabel('website')
plt.ylabel('average DNS Resolution Time (seconds)')
plt.title('DNS Resolution Time Comparison')
plt.xticks(rotation=90)
plt.legend()
plt.grid(True)
plt.tight_layout()

# Show the plot
plt.show()
