# External DNS service reconciliation

Updated: October 13, 2026

## Scope and evidence

The October 12 audit snapshot reconciled public IPv4 identities observed in the
authoritative External DNS views with live address and destination-NAT state
on the four CORE routers. Its counts are historical; the current ledger below
also includes router A records published on October 13.

The live dynamic zones were compiled with their journals on DNS primary CT
`25100`. That October 12 snapshot contained:

- 25 A records using 14 unique forward addresses;
- 23 CNAME records;
- four MX records;
- ten PTR records; and
- 16 reconciled public addresses.

The current October 13 External forward-zone snapshot contains 26 A records
using 16 unique addresses, 19 CNAME records, and three MX records. The
machine-readable source is `config/external_dns_reconciliation.yaml`; it
records 18 public identities reconciled with router assignments, including
PTR-only and router identities.

## Live inspection follow-up (October 13, 2026)

Read-only checks on the primary (CT `25100` on `pve-upr-3-luj`) and secondary
(CT `26100` on `pve-upr-3-cen`) confirmed matching primary/secondary serials
for each replicated zone. The forward zones have distinct Internal and
External serials where their view data differs:

| Forward zone | Internal serial | External serial |
| --- | ---: | ---: |
| `intelisis.com.ar` | `2026101304` | `2026101304` |
| `aero.com.ar` | `2026101102` | `2026101109` |
| `polodesalud.com.ar` | `2026101103` | `2026101103` |

The four reverse zones are declared for the External view only, so the
inspector checks them against the two External endpoints rather than the
Internal view servers. ARIN authoritative servers `r.arin.net` and `u.arin.net`
confirmed delegation of all four `/24` reverse zones to
`ns1.intelisis.com.ar` and `ns2.intelisis.com.ar` (TTL 172800).

Read-only inspection through the PVE hosts and `pct exec` confirmed the
primary is running with the reverse zones loaded as primaries and the
secondary is running with them loaded as secondaries. Their SOA responses,
queried with the configured External TSIG identity, carried the authoritative
answer (`AA`) flag and matching serials:

| Reverse zone | Primary and secondary serial |
| --- | ---: |
| `100.121.138.in-addr.arpa` | `1503626320` |
| `101.121.138.in-addr.arpa` | `2026100602` |
| `102.121.138.in-addr.arpa` | `1513198928` |
| `103.121.138.in-addr.arpa` | `1513198889` |

All ten PTR records in the inventory also returned authoritative answers with
the expected targets from both endpoints.

The earlier unsigned probes originated from the Development environment, whose
route uses source `192.168.27.15`. This falls within BIND's configured
RFC1918 `localnet` ACL and can select the Internal view even when a query is
sent to a public DNS address. The earlier unsigned SOA comparison therefore
observed Internal serials and did not verify the External forward view.
Reverse zones are intentionally absent from the Internal view, so those
non-authoritative referrals did not indicate a public reverse-DNS outage. The
CLI's unsigned `inspect` check is source/view dependent and does not enumerate
both BIND views by itself. Use view-specific `rndc zonestatus` and
External-TSIG queries from an authorized PVE path for reconciliation; use an
external vantage to independently verify public-client view selection. No DNS
or router configuration was changed during this read-only inspection.

### Mantis endpoint recovery (October 13, 2026)

The published `mantis.aero.com.ar` endpoint resolved to
`138.121.100.15`, but TCP `21150` timed out because its destination-NAT rule
was missing from `CORE-ROUTER-LUJAN`. The Mantis guest at `192.168.25.50`
was running Apache, MariaDB, and Postfix and returned HTTPS locally on port
`21150`. Restored the exact mapping `138.121.100.15:21150` to
`192.168.25.50:21150`; external HTTPS then passed certificate verification,
redirected to `/login_page.php`, and returned HTTP `200`. The legacy
`138.121.100.7:443` rollback path was left unchanged.

After approval to publish both hostnames, expanded the Apache vhost and
Certbot SAN certificate to cover `mantis.aero.com.ar` and
`mantis.intelisis.com.ar`. The staging DNS-01 test passed before production
issuance, and the renewal hook now checks both names before reloading Apache.
Published split-view A records for `mantis.intelisis.com.ar`: Internal
`192.168.25.50` (TTL 38400) and External `138.121.100.15` (TTL 300). Both
authoritative servers returned the matching answers in both views, with
External SOA serial `2026101309`. HTTPS using normal DNS resolution returned
HTTP `200` with successful certificate verification for both names.

### CRM and Database canonical names (October 13, 2026)

After the operator approved both names subject to certificate validation, the
CRM at `138.121.100.4` was configured with a separate
`gestion.intelisis.com.ar` certificate and Apache vhost. A scoped RFC2136 key
can change only TXT at
`_acme-challenge.gestion.intelisis.com.ar`; the Internal view excludes that
identity. The staging challenge and production issuance both succeeded. HTTPS
to `/usuarios/iniciar_sesion` returned HTTP `200` with TLS verification `0`,
and HTTP redirects to the HTTPS canonical hostname. The existing Aero
certificate/vhosts, CRM application configuration, and NAT were left intact.
Automatic DNS-01 renewal is configured with a root-only credential and a
deploy hook that verifies the hostname and Apache configuration before reload.

PostgreSQL at `138.121.101.4:5432` presented a trusted certificate for
`database.intelisis.com.ar` with hostname verification successful. Published
External A records at TTL 300:

- `gestion.intelisis.com.ar` -> CNAME `tic.intelisis.com.ar` -> `138.121.101.15`
- `database.intelisis.com.ar` -> `138.121.101.4`

Gestion is now a CNAME to the TIC router identity in both views;
`gestion.aero.com.ar` was removed from Internal and External DNS and returns
authoritative NXDOMAIN on both servers. Cloudflare and Google Public DNS also
returned NXDOMAIN during final verification. Aero apex and its `www`/`public`
aliases remain on Lujan. Both authorities were verified.
The External Intelisis SOA serial after the latest update is `2026101323`.
Cloudflare DNS still returned its pre-publication cached
negative answer for the CRM name during verification; its cached negative TTL
was approximately 10 hours 30 minutes. This is resolver cache state, not an
authoritative DNS or service failure.

### Pro3d zone retirement

After operator approval on October 13, `pro3d.com.ar` was removed from both
Internal and External BIND views on primary CT `25100` and secondary CT
`26100`. Its old zone serial was `2026101102` in both views. The External NS
and A records in the retired zone had pointed to `ns1.pro3d.com.ar`
(`138.121.100.1`) and `ns2.pro3d.com.ar` (`138.121.102.1`), but the `.com.ar`
parent delegates the domain to `launch1.spaceship.net` and
`launch2.spaceship.net`. Both delegated servers returned `REFUSED`; public
resolvers returned `SERVFAIL` before and after the local retirement.

The Internal zone, including its MX, mail aliases, and groupware record, was
also removed by operator instruction. Mailcow's domain configuration was not
changed. The active reconciliation ledger excludes the retired pro3d zone and its
public apex address.

### Edge-router A records

On October 13, the External A records for `lujan.intelisis.com.ar`,
`tic.intelisis.com.ar`, `centro.intelisis.com.ar`, and
`cordoba.intelisis.com.ar` were reconciled with the corresponding CORE router
public loopback assignments:

| Name | External address | Router |
| --- | --- | --- |
| `lujan.intelisis.com.ar` | `138.121.100.15` | `CORE-ROUTER-LUJAN` |
| `tic.intelisis.com.ar` | `138.121.101.15` | `CORE-ROUTER-TIC` |
| `centro.intelisis.com.ar` | `138.121.102.15` | `CORE-ROUTER-CENTRO` |
| `cordoba.intelisis.com.ar` | `45.238.8.15` | `CORE-ROUTER-CORDOBA` |

The three newly added addresses were verified as `/32` assignments on their
respective router loopback interfaces. This DNS reconciliation does not
inventory or change destination-NAT services on those addresses.

## Disposition summary (October 12 router audit; Mantis updated October 13)

| Public address | Primary DNS identity or role | Live router finding | Disposition |
| --- | --- | --- | --- |
| `138.121.100.1` | Primary authoritative DNS | TCP/UDP 53 to `192.168.25.100` | Dedicated exception |
| `138.121.100.2` | `gps.aero.com.ar` | Nine TCP ports to `192.168.25.8` | Conditional migration candidate |
| `138.121.100.3` | `pbx.aero.com.ar` | No assignment or NAT on audited CORE routers | Dedicated PBX exception; locate owner |
| `138.121.100.4` | `aero.com.ar`, `intelisis.com.ar` | Broad CRM NAT plus customer ranges `10000-10474` | Preserve pending dedicated apex/CRM cutover |
| `138.121.100.5` | Production mail | Mail and HTTPS ports to `192.168.25.40` | Dedicated mail exception |
| `138.121.100.7` | Legacy Mantis HTTPS compatibility route; PTR retired | TCP 443 to `192.168.25.50:443` | Remove after Mantis service acceptance |
| `138.121.100.15` | WEB and Lujan router A records; Mantis CNAME target | TCP 20502 to Mantis HTTPS `:443`, 20503 to SSH `:22`, legacy 21150 to HTTPS `:443`, WEB 20602 to `.25.60:443`, and 20603 to `.25.60:22` | Active shared endpoints |
| `138.121.101.3` | `iot.intelisis.com.ar` | HTTP, MQTT/TLS, and application ports to `192.168.25.7` | Owner and protocol decision required |
| `138.121.101.4` | PTR-only `database.intelisis.com.ar` | Existing TCP 5432 to `192.168.25.25` | Retain as Lujan rollback configuration; approved TIC endpoint is `138.121.101.15:20254` with mandatory SSH `20253`, pending target validation; no RouterOS source filtering |
| `138.121.101.6` | `ceis.polodesalud.com.ar` | TCP 80/443/12321/12323 to `192.168.25.151` | Conditional migration candidate |
| `138.121.101.7` | `pms.polodesalud.com.ar` | No assignment or NAT on audited CORE routers | Locate owner before any DNS change |
| `138.121.101.8` | `development.intelisis.com.ar` | Only TCP 20022 to SSH on `192.168.27.15` | Inventory and owner decision required |
| `138.121.101.242` | `polodesalud.com.ar` apex | No assignment or NAT on audited CORE routers | Preserve pending dedicated apex cutover |
| `138.121.102.1` | Secondary authoritative DNS | TCP/UDP 53 to `192.168.26.100` | Dedicated exception |
| `138.121.102.6` | `projects.intelisis.com.ar` | All protocols and ports to `192.168.26.10` | Inventory, then migrate explicit ports only |
| `138.121.101.15` | `tic.intelisis.com.ar` | Public loopback assignment verified; NAT service inventory is out of scope | Dedicated router identity |
| `138.121.102.15` | `centro.intelisis.com.ar` | Public loopback assignment verified; NAT service inventory is out of scope | Dedicated router identity |
| `45.238.8.15` | `cordoba.intelisis.com.ar` | Public loopback assignment verified; NAT service inventory is out of scope | Dedicated router identity |

## Alias and dependency findings

- All `autoconfig`, `autodiscover`, `imap`, and `smtp` aliases resolve through
  the dedicated production mail identities on `138.121.100.5`.
- `public.aero.com.ar` and `www.aero.com.ar` depend on the shared
  `aero.com.ar` apex at `138.121.100.4`. `gestion.aero.com.ar` is retired.
- `www.polodesalud.com.ar` and `www.pro3d.com.ar` depend on their respective
  apex addresses.
- `owncloud.aero.com.ar` and `wiki.aero.com.ar` point to
  `services.aero.com.ar`, but no External A or CNAME record for that target was
  observed. These aliases are unresolved and require an owner decision rather
  than automatic migration.
- `web.intelisis.com.ar` resolves externally to `138.121.100.15` and internally
  to Lujan router `10.8.0.21`. Both router views forward TCP `20602` to
  `192.168.25.60:443` and TCP `20603` to `192.168.25.60:22`; source policy is
  owned by the external firewall. HTTPS is served by the replacement WEB VM.
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
   `polodesalud.com.ar`, and the unresolved `services.aero.com.ar` aliases
   before changing their DNS.

No address is considered available solely because a forward or reverse record
is absent.

## Mantis current DNS and client ports (October 13, 2026)

The later client-access change supersedes the historical Mantis A-record and
backend-port observations above. `mantis.intelisis.com.ar` is a CNAME to
`lujan.intelisis.com.ar` in both DNS views. The target resolves internally to
`10.8.0.21` and externally to `138.121.100.15`; the Internal and External
SOA serials are `2026101307` and `2026101319`, respectively. The External
zone now has 26 A records and 20 CNAME records.

Lujan CT `25050` remains the active production source at `192.168.25.50`.
Apache listens on ports 80/443 and redirects HTTP to HTTPS. Both router
`:20502` endpoints forward to guest port 443, and both `:20503` endpoints
forward to guest port 22; `20501` is unused. Legacy public `:21150` and
`.100.7:443` HTTPS compatibility routes remain pointed at guest port 443.
`mantis.aero.com.ar` is retired, the active certificate identity is
`mantis.intelisis.com.ar`, and the TIC migration remains paused. Pre-change
zone backups are under `/root/mantis-cname-cutover-20261013` on primary CT
`25100`.
