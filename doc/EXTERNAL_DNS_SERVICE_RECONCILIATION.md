# External DNS service reconciliation

Updated: October 14, 2026

## Scope and evidence

The October 13 Mantis recovery and Lujan service details below are historical
snapshots. The current October 14 cutover status later in this document
supersedes any earlier statement that Mantis still uses Lujan or that TIC
migration is paused.

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

The post-retirement October 14 External forward-zone snapshot contains 26 A
records using 16 unique addresses, 18 CNAME records, and three MX records.
The machine-readable source is `config/external_dns_reconciliation.yaml`; it
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
| `100.121.138.in-addr.arpa` | `1503626321` |
| `101.121.138.in-addr.arpa` | `2026100602` |
| `102.121.138.in-addr.arpa` | `1513198928` |
| `103.121.138.in-addr.arpa` | `1513198889` |

The pre-cleanup October 14 authenticated External AXFR found nine PTR records
across the four reverse zones. It confirmed that the retired Mailcow pilot PTR
at `138.121.100.8` is gone, and exposed a stale PTR at `138.121.101.4` pointing
to `database.intelisis.com.ar`.

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

### Approved DNS retirements (October 14, 2026)

Following explicit operator approval, the legacy `database.intelisis.com.ar`
PTR was removed from the External `101.121.138.in-addr.arpa` zone. The forward
name was already absent from both Intelisis views; the active database name
remains `db1.intelisis.com.ar` on the TIC endpoint.

The obsolete Aero records were removed from the applicable Aero views:

- Internal: `services.aero.com.ar` and `fileserver.aero.com.ar` A records,
  plus `owncloud.aero.com.ar` and `wiki.aero.com.ar` CNAMEs.
- External: `owncloud.aero.com.ar` and `wiki.aero.com.ar` CNAMEs.
- `mantis.aero.com.ar` and `gestion.aero.com.ar` had already been absent and
  were rechecked; neither was recreated.

All seven names (`database.intelisis.com.ar`, `services.aero.com.ar`,
`fileserver.aero.com.ar`, `owncloud.aero.com.ar`, `wiki.aero.com.ar`,
`mantis.aero.com.ar`, and `gestion.aero.com.ar`) returned authoritative
NXDOMAIN in both views on both DNS authorities. The External checks used the
scoped TSIG identity. Aero Internal and External serials are both
`2026101401`; reverse zone `101.121.138.in-addr.arpa` is `2026101401`.
Primary and secondary serials match. Pre-change zone backups are retained on
primary CT `25100` in `/root/dns-cleanup-20261014T1722Z/`.

No router or DNS configuration was changed during the routing/ownership
follow-up below.

### Routing and ownership follow-up (October 14, 2026)

Authenticated read-only API queries covered address assignments, exact host
routes, destination NAT, and relevant ARP entries on all four CORE routers.
Current PVE cluster configuration and guest state were also checked where the
target was expected to reside.

- **PBX (`138.121.100.3`):** No address assignment, host route, or destination
  NAT for the public address was found on the four CORE routers. Centro PBX
  VM `26006` is running at `192.168.26.6`; its configured interface MAC
  matches the active Centro ARP entry. The public route/firewall owner remains
  unknown. There is no External PTR.
- **PMS (`138.121.101.7` / `192.168.25.152`):** No public address assignment,
  host route, or destination NAT was found on the four CORE routers. Lujan
  ARP for `192.168.25.152` is `failed`, and no guest config containing that
  address was found in the audited Lujan or Centro PVE clusters. A host outside
  those clusters or a non-PVE service remains possible; ownership is not
  established. The existing DNS A/PTR records were left unchanged.
- **Polodesalud apex (`138.121.101.242`):** The active `/32` route is present
  on Lujan via `192.168.102.194` on running PPPoE-in session `backbone-16`.
  TIC, Centro, and Cordoba route this destination over their Lujan backhauls.
  No local address assignment or destination NAT was found. This confirms a
  routed path toward a downstream peer, not which service host or owner serves
  the apex.
- **Former Database endpoint (`138.121.101.4`):** At the time of the initial
  read-only audit, the old TCP `5432` NAT mapping was absent but the address
  remained assigned to the Lujan loopback and routed from TIC, Centro, and
  Cordoba. The subsequent approved cleanup removed that assignment and
  withdrew the dynamic `/32` route from all four CORE routers.

At the time of the read-only audit, DNS records for PBX, PMS, and Polodesalud
were preserved and no routing or firewall changes were made.

### Operator-approved cleanup (October 14, 2026)

After the audit, the operator approved and the following changes were applied:

- Retired PMS: removed `pms.polodesalud.com.ar` A records from both Internal
  and External views and removed its External PTR. The primary zones validate,
  and the secondary has matching serials.
- Restricted PBX to Internal: removed the External
  `pbx.aero.com.ar -> 138.121.100.3` A record while retaining its Internal
  `pbx.aero.com.ar -> 192.168.26.6` A record. No PBX destination NAT was
  present on any of the four audited CORE routers.
- Retired `.101.4`: removed `138.121.101.4/32` from the Lujan loopback. Its
  local dynamic route and the learned routes on TIC, Centro, and Cordoba are
  absent. No NAT for the address or the deleted Database guest remains.
- Preserved Polodesalud: the operator confirmed the existing
  `polodesalud.com.ar` A record, `www` CNAME, and Lujan PPPoE route are correct;
  no DNS or routing changes were made for Polo.

The updated External serials are `aero.com.ar` `2026101402`,
`polodesalud.com.ar` `2026101104`, and
`101.121.138.in-addr.arpa` `2026101402`. Primary zone validation passed and
the secondary serials match. Pre-change zone copies are retained on CT `25100`
under `/root/dns-cleanup-pms-pbx-20261014T1915Z/`.

### Mantis endpoint recovery (October 13, 2026; historical)

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

### Mantis TIC cutover and router-port reconciliation (October 14, 2026)

Read-only queries to both authoritative DNS servers and both public DNS
addresses returned `mantis.intelisis.com.ar CNAME tic.intelisis.com.ar`;
the TIC target resolves to `10.8.0.61` internally and
`138.121.101.15` externally. Internal and External `intelisis.com.ar` SOA
serials are both `2026101402` on the primary and secondary.

The live RouterOS NAT audit found TIC rules for `20502` to CT `27050`
(`192.168.27.50:443`) and `20503` to `192.168.27.50:22` on both the internal
and public TIC addresses. No Mantis NAT rule was found on Lujan, including no
legacy `21150` or `.100.7:443` forwarding. The public Mantis ports were not
reachable from the available workstation; external client-path acceptance is
therefore unverified.

All four CORE routers now expose SSH `28022`, Winbox `28291`, API `28728`, and
API-SSL `28729`, verified through authenticated RouterOS API checks. The
fleet-wide normalization policy targets these ports, but routers outside CORE
have not yet been validated. TIC has no API-SSL certificate configured, so
`28729` is configured but TLS service usability remains unverified.

The three newly added addresses were verified as `/32` assignments on their
respective router loopback interfaces. This DNS reconciliation does not
inventory or change destination-NAT services on those addresses.

### Shared Aero and Intelisis apexes (operator decision, October 14, 2026)

The approved split-view targets are:

| Record | Internal view | External view |
| --- | --- | --- |
| `aero.com.ar` | A `10.8.0.21` | A `138.121.100.4` |
| `intelisis.com.ar` | A `10.8.0.21` | A `138.121.100.4` |
| `www.aero.com.ar` | CNAME to `aero.com.ar` | CNAME to `aero.com.ar` |
| `public.aero.com.ar` | CNAME to `aero.com.ar` | CNAME to `aero.com.ar` |
| `lujan.intelisis.com.ar` | A `10.8.0.21` (unchanged) | A `138.121.100.15` (unchanged) |

The apexes remain A records; do not convert either zone apex to a CNAME.
`www` and `public` alias the Aero apex, and Lujan's router records remain
unchanged.

The approved state was published and verified October 14 on both
authoritative servers. Internal apex A records are `10.8.0.21`, External
apex A records are `138.121.100.4`, and both aliases are CNAMEs to
`aero.com.ar`. `lujan.intelisis.com.ar` remains `10.8.0.21` Internal and
`138.121.100.15` External. Current `aero.com.ar` serials are `2026101401` in
both views; `intelisis.com.ar` remains Internal `2026101403` and External
`2026101414`. The secondary serves the updated Internal
`intelisis.com.ar` serial, and the SOA inspection confirms synchronization.

The prior Internal `intelisis.com.ar` A pointed to deleted Lujan CT `25020`.
It was changed to `10.8.0.21` on primary CT `25100`, validated and reloaded;
the secondary received the update. A root-only backup is retained on the
primary at `/root/intelisis-internal-apex-20261014T1537Z.hosts`.

Read-only RouterOS inspection found Lujan TCP `80,443` destination NAT to
`192.168.27.20` for both public apex address `138.121.100.4` and internal
router address `10.8.0.21`. TIC Gestion CT `27020` is running with that
address. No NAT rules were changed. The customer-port audit found 95 rules
overlapping `10000-10500`: 53 enabled and 42 disabled. Enabled mappings cover
265 ports; enabled and disabled rules cover 465 distinct ports through
`10474`, with no rule for `10145-10149`, `10235-10239`, or `10475-10500`.
These gaps and disabled customer mappings remain untouched pending owner/client
review.

## Disposition summary (October 12 router audit; DNS status updated October 15)

| Public address | Primary DNS identity or role | Live router finding | Disposition |
| --- | --- | --- | --- |
| `138.121.100.1` | Primary authoritative DNS | TCP/UDP 53 to `192.168.25.100` | Dedicated exception |
| `138.121.100.2` | `gps.aero.com.ar` | Nine TCP NAT mappings to `192.168.25.8`; `8080` is operator-confirmed not required and refuses connections | Retain dedicated public IP; complete application checks on the eight required ports; leave the extra NAT mapping unchanged pending separate approval |
| `138.121.100.3` | PBX is Internal-only; no External A | Centro PBX VM `26006` is running at `.26.6`; no public assignment, route, or NAT on audited CORE routers | Preserve Internal-only; do not add External DNS or NAT |
| `138.121.100.4` | `aero.com.ar`, `intelisis.com.ar` | TCP 80/443 to TIC Gestion `192.168.27.20`; customer ranges `10000-10474` | Preserve; candidate shared standard-port web proxy after validation; customer mappings pending owner review |
| `138.121.100.5` | Multi-tenant production Mailcow | Mail and HTTPS ports to `192.168.25.40` | Preserve existing service/IP; canonical mail host is `mail.intelisis.com.ar` |
| `138.121.100.7` | Retired address; no Mantis compatibility route | No destination NAT observed | Keep retired; do not recreate without approval |
| `138.121.100.15` | WEB and Lujan router A records; Mantis now targets TIC | WEB 20602 to `.25.60:443` and 20603 to `.25.60:22`; no Mantis NAT observed | Active WEB endpoint; no Mantis forwarding |
| `138.121.101.2` | Prestoprenda, externally administered; no local External A/PTR observed | Active destination NAT observed | Retain its own externally managed public IP; do not publish Internal DNS here |
| `138.121.101.3` | `iot.intelisis.com.ar` | TCP `80`, `8883`, and `8922` to `192.168.25.7`; TCP `443` to `192.168.25.7:8123` | Retain this dedicated public service IP and all current public application/protocol paths. Stage only private admin SSH at Lujan TCP `20073` -> `192.168.25.7:8922`; keep the current SSH path until allowlist, separate admin DNS, and end-to-end verification are accepted. |
| `138.121.101.4` | No A or PTR; legacy Database DNS retired October 14 | Address removed from Lujan loopback; `/32` withdrawn from all four CORE routers; no NAT | Retired; do not reuse without provider-allocation confirmation |
| `138.121.101.6` | `ceis.polodesalud.com.ar` | TCP 80/443/12321/12323 to `192.168.25.151` | Retain its own IP until the planned shared reverse-proxy web cutover is accepted |
| `138.121.101.7` | PMS retired; no A or PTR | No assignment, route, or NAT on the audited CORE routers | Keep retired; do not republish or reuse without separate review |
| `138.121.101.8` | `development.intelisis.com.ar` | Only TCP 20022 to SSH on `192.168.27.15` | Private-use administration confirmed; preserve the current path until a verified TIC site-router high-port replacement is accepted. Retire `.101.8` only after separate approval. |
| `138.121.101.242` | `polodesalud.com.ar` apex | Routed through Lujan PPPoE-in `backbone-16` via `.102.194`; no local assignment or NAT | External customer-owned IP; preserve address, DNS, and route |
| `138.121.102.1` | Secondary authoritative DNS | TCP/UDP 53 to `192.168.26.100` | Dedicated exception |
| `138.121.102.6` | `projects.intelisis.com.ar` | All protocols and ports to `192.168.26.10`; guest is powered off | Do not activate or migrate; separately approve disposition of the existing publication |
| `138.121.101.15` | `tic.intelisis.com.ar` | Public loopback assignment verified; NAT service inventory is out of scope | Dedicated router identity |
| `138.121.102.15` | `centro.intelisis.com.ar` | Public loopback assignment verified; NAT service inventory is out of scope | Dedicated router identity |
| `45.238.8.15` | `cordoba.intelisis.com.ar` | Public loopback assignment verified; NAT service inventory is out of scope | Dedicated router identity |

The October 15 target keeps the site `.15` addresses for private GUI/SSH and
other approved high-port access, not as a replacement for public-standard web
ingress. Use existing `138.121.100.4` as the shared `80`/`443` proxy candidate
only after CRM routing and proxy behavior are validated. GPS keeps its own IP;
CEIS keeps its own IP until its planned proxy cutover; Prestoprenda remains
externally administered with no Internal DNS publication; and the
customer-owned Polodesalud address remains unchanged. No live records or NAT
were changed by this target classification.

## Alias and dependency findings

- All `autoconfig`, `autodiscover`, `imap`, and `smtp` aliases resolve through
  the dedicated production mail identities on `138.121.100.5`.
- Operator direction October 15: retain the multi-tenant Mailcow service on
  its existing IP, use `mail.intelisis.com.ar` as the canonical A-record host,
  and make compatible mail service hostnames across the hosted domains CNAMEs
  to it. Preserve each domain apex's MX/TXT records; point MX directly at the
  canonical mail host rather than making a domain apex a CNAME.
- `public.aero.com.ar` and `www.aero.com.ar` depend on the shared
  `aero.com.ar` apex at `138.121.100.4`. `gestion.aero.com.ar` is retired.
- `www.polodesalud.com.ar` and `www.pro3d.com.ar` depend on their respective
  apex addresses.
- `services.aero.com.ar`, `fileserver.aero.com.ar`, `owncloud.aero.com.ar`,
  and `wiki.aero.com.ar` were removed from their applicable views on October
  14 and return authoritative NXDOMAIN in both views on both authorities.
- `polodesalud.com.ar` remains A `138.121.101.242` in both views and
  `www.polodesalud.com.ar` remains a CNAME to the apex. The operator confirmed
  the active `/32` route through Lujan PPPoE-in `backbone-16` via
  `192.168.102.194` is correct; no further change is required. Its MX points
  to `mail.intelisis.com.ar`.
- `pms.polodesalud.com.ar` was retired: it has no A record in either view and
  no External PTR. The former internal target `192.168.25.152` had failed ARP,
  with no guest config found in the audited Lujan or Centro PVE clusters.
- The former `mantis.aero.com.ar` and `gestion.aero.com.ar` names both return
  authoritative NXDOMAIN in Internal and External views on both authorities;
  Mantis's current canonical name is the TIC CNAME.
- `pbx.aero.com.ar` is A `192.168.26.6` in Internal and absent from External.
  Centro PBX VM `26006` is running and its configured MAC matches the active
  ARP entry. No PBX destination NAT exists on the four audited CORE routers.
- `web.intelisis.com.ar` resolves externally to `138.121.100.15` and internally
  to Lujan router `10.8.0.21`. Both router views forward TCP `20602` to
  `192.168.25.60:443` and TCP `20603` to `192.168.25.60:22`; source policy is
  owned by the external firewall. HTTPS is served by the replacement WEB VM.
- `138.121.101.2` has active Prestoprenda NAT but no A or PTR in the inspected
  zones. The operator confirmed the service is externally resolved and
  administered, must retain its own public IP, and must not receive Internal
  DNS publication from this environment.
- IoT's public service identity remains `iot.intelisis.com.ar` on
  `138.121.101.3`; it is not repointed to the Lujan router. A separate
  `iot-admin.intelisis.com.ar` CNAME to `lujan.intelisis.com.ar` is only a
  proposal for restricted SSH administration and is not published. The staged
  `20073` -> guest `8922` path remains disabled until an administrative
  allowlist, both-view DNS, and end-to-end access are accepted. Retain the
  existing `.101.3:8922` path until then.
- There is an unresolved IoT firmware-route discrepancy: the router inventory
  records public TCP `80` forwarding to `.25.7`, while IOT-SERVER's Node-RED
  firmware URL builder uses `orchestrator.firmware_base_url` and falls back to
  HTTP port `1880`. The effective database setting is not established by the
  repository evidence, and the observed NAT summary does not establish whether
  public `80` is translated to guest `80` or `1880`. Before changing any public
  IoT service or IP path, verify the live NAT destination port, guest listeners,
  effective database setting, and a generated firmware URL. The public-IP and
  other application-port treatment is unchanged by the private SSH proposal.

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
5. Retain GPS on its own public IP and client ports. Retain CEIS on its current
   IP until its planned shared reverse-proxy web cutover is validated. Do not
   activate or migrate Projects while it is powered off and unresolved.
6. Move Development's private SSH path to the TIC site-router high-port
   endpoint only after target/listener/access-policy verification. Keep IoT's
   public IP and application/protocol ports; stage only its private SSH path
   on Lujan TCP `20073` -> guest `8922` after allowlist, DNS, and end-to-end
   acceptance. Resolve the firmware HTTP `80`/`1880` discrepancy before any
   public IoT path change. PMS and `.101.4` are retired; preserve the
   customer-owned Polodesalud IP and route.

No address is considered available solely because a forward or reverse record
is absent.

## Historical Mantis DNS and client ports (October 13, 2026)

The later client-access change supersedes the historical Mantis A-record and
backend-port observations above. `mantis.intelisis.com.ar` is a CNAME to
`lujan.intelisis.com.ar` in both DNS views. The target resolves internally to
`10.8.0.21` and externally to `138.121.100.15`; the Internal and External
SOA serials at that snapshot were `2026101307` and `2026101319`,
respectively. The External zone then had 26 A records and 20 CNAME records;
the approved October 14 cleanup reduced the current CNAME count to 18.

Lujan CT `25050` remains the active production source at `192.168.25.50`.
Apache listens on ports 80/443 and redirects HTTP to HTTPS. Both router
`:20502` endpoints forward to guest port 443, and both `:20503` endpoints
forward to guest port 22; `20501` is unused. Legacy public `:21150` and
`.100.7:443` HTTPS compatibility routes remain pointed at guest port 443.
`mantis.aero.com.ar` is retired, the active certificate identity is
`mantis.intelisis.com.ar`, and the TIC migration was then paused. Pre-change
zone backups are under `/root/mantis-cname-cutover-20261013` on primary CT
`25100`. The October 14 TIC cutover supersedes this status; no Lujan Mantis
forwarding remains in the current router audit.
