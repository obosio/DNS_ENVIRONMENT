# DNS_ENVIRONMENT

Updated: Oct 12, 2026

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

## Architecture & Topology

| Role | Container | Site | IP Address | Host Node |
| --- | --- | --- | --- | --- |
| Primary (Master) | CT 25100 (`ns1.intelisis.com.ar`) | Lujan | `192.168.25.100` / `138.121.100.1` | `pve-upr-3-luj` |
| Secondary (Replica) | CT 26100 (`ns2.intelisis.com.ar`) | Centro | `192.168.26.100` / `138.121.102.1` | `pve-upr-3-cen` |

### Authoritative Zones

Twelve replicated zones are managed across two distinct views:
- **Internal View**: `intelisis.com.ar`, `aero.com.ar`, `polodesalud.com.ar`, `pro3d.com.ar`
- **External View**: The four forward zones plus reverse zones `100.121.138.in-addr.arpa`, `101.121.138.in-addr.arpa`, `102.121.138.in-addr.arpa`, `103.121.138.in-addr.arpa`.

## Tooling & Inspection

A Python CLI tool (`dns-environment`) provides deterministic validation of the reconciliation ledger and live DNS inspection:

```bash
# Validate reconciliation data
.venv/bin/dns-environment validate --reconciliation config/external_dns_reconciliation.yaml

# Run live DNS inspection across all authoritative servers and views
.venv/bin/dns-environment inspect

# Run test suite
.venv/bin/pytest
```

## Related

- `../PVE/` - Proxmox VE host infrastructure and guest provisioning
- `../MIKROTIK-MANAGER/` - Edge router fleet configuration and destination-NAT state
- `../WEB_ENVIRONMENT/` - Ingress reverse-proxy services mapped from DNS endpoints
- `../MAIL_ENVIRONMENT/` - Mailcow mail gateway DNS dependencies
