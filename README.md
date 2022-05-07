# mockapetris

Implementing a DNS server with Golang programming language.

## How does it work?
Mockapetris uses a local cache and saves the records of host,ip pairs
in that cache. After that it listens on port **8090** for our requests
to get the domain name and return the ip address of that domain.

The connection protocol is UDP and our main server is a DNS type A.

Our service also provides a root server where you can control the DNS. You
can add or remove records in the DNS cache.

## Run DNS server
You can run the DNS server by the following command:
```shell
go run main.go
```

After that you will have the following services:
- DNS server: 127.0.0.1:8090
- Root server: 127.0.0.1:1230

## Requests
You can edit the records by the following requests:

#### Add new record
```shell
curl -X POST -H "Content-Type: application/json" \
    -d '{"url": "[host]", "ip": "[IP]"}' \
    http://localhost:1230/put
```

#### Remove record
```shell
curl -X POST -H "Content-Type: application/json" \
    -d '{"url": "[host]"}' \
    http://localhost:1230/del
```

## Test DNS server
You can test the dns server with the following command:
```shell
nslookup www.google.com localhost -port=8090
```
