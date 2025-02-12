# DNSSec Implementation

## Root Server Configuration and Initial Validation

The `roots.json` file defines the root servers used in this process. It is assumed that these root servers are valid.
If the root servers were not defined in `roots.json`, the root DNSKEY RRset would be obtained from http://data.iana.org/root-anchors/root-anchors.xml.

## Domain Hierarchy Traversal and Result Verification

Since the root server is verified, the next level servers for Top-Level Domains (TLDs) are obtained. The domain hierarchy is then traversed by querying the TLD servers for the domain's IP addresses. Upon receiving a Resource Record Set (RRset) from a DNS server, the result must be verified. This verification process requires obtaining the RRset, the child's Delegation Signer (DS) record, and the digest type (encryption algorithm) used by the child.

## Parent DNS Node Verification

To ensure the authenticity of the records, a query is made to the parent DNS node. The signature (RRSIG) and the public key (KSK) corresponding to the private key used to sign the NS records (RRset) are requested. The validity of the record is verified using dns.dnssec.validate. It takes the RRset, RRSIG, and domain as input and throws an exception if the validation fails.

## Chain of Trust Establishment

Because the TLD also possesses a DNSKEY record and has signed the DS record using its private key, the result is placed in another "RRSIG" record. The root zone has a DS record containing a fingerprint of it, and a DNSKEY record, and an RRSIG record to go along with it. This process creates a chain of trust between root zones and all lower-level zones.

This method iteratively checks for validation at each zone, generates the next level servers starting from the root server, and verifies at each stage until the bottom of the domain hierarchy is reached.

## Identifying DNSSEC Validation Failures and Unsupported Domains

To identify "DNSSEC failed validation," it is necessary to check if the parent's DS record matches the child's generated hash using its DNSKEY (KSK) and validate the signature (RRSIG) and record (RRset) of the child.

To verify the case for "DNSSEC not supported," it is determined that DNSSEC is not supported by a domain if, at any zone, it cannot provide a signature (RRSIG), its public key (KSK), or its child zone's DS record. An exception may also be thrown when querying for DNSKEY.

Citations:
- [1] http://data.iana.org/root-anchors/root-anchors.xml
