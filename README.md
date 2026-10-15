# DNS_ENVIRONMENT

Updated: Oct 14, 2026

**DNS infrastructure, authoritative zone reconciliation, and operational audit platform** for the primary and secondary BIND DNS services, zone replication, and split-view publication across all network and cluster boundaries.

Core system: Authoritative and recursive DNS infrastructure and zone reconciliation system
Domain: Network naming services, DNS infrastructure, and IP reconciliation
Core runtime: BIND 9 on Debian 13 guests (CT 25100 and CT 26100) with Python inspection and reconciliation tooling
Operational placement: Proxmox VE cluster hosts (Lujan CT 25100 and Centro CT 26100), core edge routers, and public DNS interfaces
Primary transport: DNS protocol (UDP/TCP 53), TSIG AXFR/IXFR, and SSH
Supporting components: Zone reconciliation models, validation tooling, inspection probes, migration checklists, and operational documentation

This project exists to deliver managed authoritative and recursive DNS infrastructure and zone reconciliation; inspection probes, inventory data, and migration helpers are supporting mechanisms and do not define the project identity.

## Scope

- Maintain primary and secondary authoritative BIND 9 services across sites (`ns1.intelisis.com.ar` on CT 25100, `ns2.intelisis.com.ar` on CT 26100).
- Manage split-view policy (Internal view for RFC1918 and internal networks; External view for public authoritative domains).
- Reconcile authoritative forward and reverse records against live edge router address and destination-NAT state.
- Inspect and monitor live zone serial synchronization, TSIG authenticated replication, and query consistency across views.
- Provide a clean migration path and approval boundaries for public IP reorganization and DNS cutovers.

The Database DNS/TLS cutover and Mantis TIC CNAME cutover are live and
reconciled with the current service state. Database internal-client acceptance
passed; external route reachability remains waived and unverified. Mantis
resolves to TIC in both views, with its client forwarding active on TIC and no
Mantis forwarding found on Lujan. External client-port acceptance remains
unverified from the available workstation. The completed and pending work is
documented in
[`config/tic_workload_dns_cutover_plan.yaml`](config/tic_workload_dns_cutover_plan.yaml).
Database service lifecycle and PostgreSQL migration planning are owned by
[DB_ENVIRONMENT](../DB_ENVIRONMENT/README.md); this project retains ownership
of the DNS records, DNS/TLS cutover state, and authoritative verification.
The shared Aero and Intelisis apexes now match their approved split-view
targets and were verified on both authorities. Lujan TCP `80,443` forwarding
targets TIC Gestion CT `27020`; unassigned/disabled customer-port mappings
remain unchanged pending owner review.
The approved October 14 cleanup retired the legacy `database` PTR and the
obsolete `services`, `fileserver`, `owncloud`, and `wiki` Aero records.
`mantis.aero.com.ar` and `gestion.aero.com.ar` remain absent. Authoritative
NXDOMAIN was verified for these names in both views on both DNS authorities.
The active database identity remains `db1.intelisis.com.ar`. The old
`138.121.101.4` assignment and its dynamic `/32` route have now been removed
from all four CORE routers; no old `5432` NAT mapping remains. PMS records were
removed from both DNS views and its External PTR was deleted. PBX now has only
its Internal A record (`192.168.26.6`); no External A or CORE destination NAT
remains. Polodesalud's existing apex and PPPoE route were confirmed correct by
the operator and left unchanged. The detailed actions and verified zone
serials are recorded in
[`doc/EXTERNAL_DNS_SERVICE_RECONCILIATION.md`](doc/EXTERNAL_DNS_SERVICE_RECONCILIATION.md).

## Architecture & Topology

| Role | Container | Site | IP Address | Host Node |
| --- | --- | --- | --- | --- |
| Primary (Master) | CT 25100 (`ns1.intelisis.com.ar`) | Lujan | `192.168.25.100` / `138.121.100.1` | `pve-upr-3-luj` |
| Secondary (Replica) | CT 26100 (`ns2.intelisis.com.ar`) | Centro | `192.168.26.100` / `138.121.102.1` | `pve-upr-3-cen` |

### Authoritative Zones

Ten zones are replicated across two distinct views:
- **Internal View**: `intelisis.com.ar`, `aero.com.ar`, `polodesalud.com.ar`
- **External View**: The same three forward zones plus reverse zones `100.121.138.in-addr.arpa`, `101.121.138.in-addr.arpa`, `102.121.138.in-addr.arpa`, `103.121.138.in-addr.arpa`.

`pro3d.com.ar` was retired from both BIND views on October 13, 2026, by
operator approval. Its parent delegation remains pointed at Spaceship, whose
nameservers were returning `REFUSED` during the retirement. The domain will
remain publicly unavailable until its authoritative zone is correctly served
there; internal pro3d mail and groupware DNS records were also removed.

## Tooling & Inspection

A Python CLI tool (`dns-environment`) provides deterministic validation of the reconciliation ledger and live DNS inspection:

```bash
# Validate reconciliation data
.venv/bin/dns-environment validate --reconciliation config/external_dns_reconciliation.yaml

# Check SOA answers at configured DNS server addresses
.venv/bin/dns-environment inspect

# Run test suite
.venv/bin/pytest
```

The inspection command queries SOA records without recursion and only treats
responses carrying the authoritative-answer flag as valid. Use `--reverse` to
include reverse zones, checked against External-view servers only. When run
from an RFC1918 client, BIND may intentionally select its Internal view even
for a public server address; run reverse inspection from an external vantage
to verify public-view behavior. This unsigned command is source/view dependent;
it does not enumerate both split views. Use view-specific `rndc zonestatus`
and External-TSIG queries via the PVE access procedure below when reconciling
both views.

### Accessing DNS guests for operational verification

Run guest-level checks through the Proxmox VE host that currently runs the
target LXC, using the PVE project's inventory and credential procedure. After
connecting to the trusted PVE host, use read-only commands through `pct exec`,
for example:

```bash
pct exec 25100 -- rndc status
pct exec 25100 -- rndc zonestatus 100.121.138.in-addr.arpa IN External
```

Use CT `25100` on `pve-upr-3-luj` for the primary and CT `26100` on
`pve-upr-3-cen` for the secondary, confirming current placement before access.
Do not connect directly to an LXC from the development workstation, bypass SSH
host-key verification, or expose credentials or TSIG material in command
output. For External-view checks from an RFC1918 source, use the scoped
External TSIG identity without printing its secret; unsigned requests may
select the Internal view according to BIND's client ACLs.

## Related

- `../PVE/` - Proxmox VE host infrastructure and guest provisioning
- `../MIKROTIK-MANAGER/` - Edge router fleet configuration and destination-NAT state
- `../WEB_ENVIRONMENT/` - Ingress reverse-proxy services mapped from DNS endpoints
- `../MAIL_ENVIRONMENT/` - Mailcow mail gateway DNS dependencies
