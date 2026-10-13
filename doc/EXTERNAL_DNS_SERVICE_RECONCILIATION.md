# External DNS service reconciliation

Updated: October 12, 2026

## Scope and evidence

This audit reconciles every public IPv4 identity observed in the authoritative
External DNS views with live address and destination-NAT state on the four
CORE routers. It is an inventory and classification exercise only; no DNS,
RouterOS, firewall, or workload configuration was changed.

The live dynamic zones were compiled with their journals on DNS primary CT
`25100`. The resulting snapshot contains:

- 24 A records using 14 unique forward addresses;
- 23 CNAME records;
- four MX records;
- ten PTR records; and
- one additional PTR-only public identity, for 15 reconciled addresses.

The machine-readable source is
`config/external_dns_reconciliation.yaml`.

## Disposition summary

| Public address | Primary DNS identity or role | Live router finding | Disposition |
| --- | --- | --- | --- |
| `138.121.100.1` | Primary authoritative DNS | TCP/UDP 53 to `192.168.25.100` | Dedicated exception |
| `138.121.100.2` | `gps.aero.com.ar` | Nine TCP ports to `192.168.25.8` | Conditional migration candidate |
| `138.121.100.3` | `pbx.aero.com.ar` | No assignment or NAT on audited CORE routers | Dedicated PBX exception; locate owner |
| `138.121.100.4` | `aero.com.ar`, `intelisis.com.ar` | Broad CRM NAT plus customer ranges `10000-10474` | Preserve pending dedicated apex/CRM cutover |
| `138.121.100.5` | Production mail | Mail and HTTPS ports to `192.168.25.40` | Dedicated mail exception |
| `138.121.100.7` | Legacy Mantis PTR and DNS-cache rollback | Temporary TCP 443 to `192.168.25.50:21150` | Retirement pending after the original TTL and acceptance window |
| `138.121.100.15` | Shared WEB and Mantis workloads | TCP 21150 to Mantis and TCP 21160 to WEB | Active shared endpoints |
| `138.121.101.3` | `iot.intelisis.com.ar` | HTTP, MQTT/TLS, and application ports to `192.168.25.7` | Owner and protocol decision required |
| `138.121.101.4` | PTR-only `database.intelisis.com.ar` | TCP 5432 to `192.168.25.25` | Owner decision and strict allowlist required |
| `138.121.101.6` | `ceis.polodesalud.com.ar` | TCP 80/443/12321/12323 to `192.168.25.151` | Conditional migration candidate |
| `138.121.101.7` | `pms.polodesalud.com.ar` | No assignment or NAT on audited CORE routers | Locate owner before any DNS change |
| `138.121.101.8` | `development.intelisis.com.ar` | Only TCP 20022 to SSH on `192.168.27.15` | Inventory and owner decision required |
| `138.121.101.242` | `polodesalud.com.ar` apex | No assignment or NAT on audited CORE routers | Preserve pending dedicated apex cutover |
| `138.121.101.246` | `pro3d.com.ar` apex | No assignment or NAT on audited CORE routers | Preserve pending dedicated apex cutover |
| `138.121.102.1` | Secondary authoritative DNS | TCP/UDP 53 to `192.168.26.100` | Dedicated exception |
| `138.121.102.6` | `projects.intelisis.com.ar` | All protocols and ports to `192.168.26.10` | Inventory, then migrate explicit ports only |

## Alias and dependency findings

- All `autoconfig`, `autodiscover`, `imap`, and `smtp` aliases resolve through
  the dedicated production mail identities on `138.121.100.5`.
- `gestion.aero.com.ar`, `public.aero.com.ar`, and `www.aero.com.ar` depend on
  the shared `aero.com.ar` apex at `138.121.100.4`.
- `www.polodesalud.com.ar` and `www.pro3d.com.ar` depend on their respective
  apex addresses.
- `owncloud.aero.com.ar` and `wiki.aero.com.ar` point to
  `services.aero.com.ar`, but no External A or CNAME record for that target was
  observed. These aliases are unresolved and require an owner decision rather
  than automatic migration.
- `web.intelisis.com.ar` is now published externally at
  `138.121.100.15:21160` and maps to `192.168.25.60:21160`. Its WEB SSH mapping
  remains planned and disabled. Source restrictions for HTTPS are owned by the
  external firewall.
- `138.121.101.2` has active Prestoprenda NAT but no A or PTR in the inspected
  zones. This is a network-only publication and is not an External DNS service.

## Resulting migration order

1. Keep authoritative DNS, production mail, and PBX outside shared workload
   publication.
2. Do not alter any apex address until its aliases, certificates, hosting, and
   rollback are handled as one dedicated change.
3. Pilot WEB endpoint `160` under the operator-approved
   `public_https_external_firewall` policy; keep Nginx UI authentication
   mandatory and do not expose its loopback port `9000`.
4. Evaluate Mantis next because it has a simple TCP 80/443 mapping and a known
   Lujan destination. On October 12, 2026, its active Certbot lineage was
   migrated from Apache HTTP-01 to RFC2136 DNS-01 with an exact
   `_acme-challenge.mantis.aero.com.ar TXT` grant. The 120-second staging
   renewal and Apache deployment hook passed, challenge TXT cleanup was
   verified through both public resolvers, and the redundant hourly `acme.sh`
   cron entry was disabled while retaining its recovery files. Certificate
   renewal therefore no longer requires public TCP 80.
5. Inventory GPS, CEIS, and Projects protocols before allocating endpoint
   slots.
6. Resolve ownership and live hosting for PMS, Development, IoT, Database,
   `polodesalud.com.ar`, `pro3d.com.ar`, and the unresolved
   `services.aero.com.ar` aliases before changing their DNS.

No address is considered available solely because a forward or reverse record
is absent.
