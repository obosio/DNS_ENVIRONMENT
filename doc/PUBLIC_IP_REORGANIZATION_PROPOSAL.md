# Public IP reorganization proposal

Updated: October 16, 2026 (ART)

## Current reconciliation status (October 16, 2026)

Authenticated RouterOS API checks on October 16 verified SSH `28022`, Winbox
`28291`, API `28728`, and API-SSL `28729` on all 199 reachable routers in the
214-router inventory. This includes all six CORE routers and four CORE
switches. The other 15 routers could not be verified because their API
endpoints refused or failed to complete the connection; do not treat them as
converged. `PDS-Vistalba` required a narrowly scoped edit to its existing
`Router access` input rule so it accepts the new SSH port; port `22` was not
changed. TIC API-SSL has no RouterOS certificate configured, so port
compliance does not establish usable TLS.

Mantis has completed its TIC cutover: `mantis.intelisis.com.ar` is a CNAME to
`tic.intelisis.com.ar` in both DNS views, and TIC owns the active `20502` HTTPS
and `20503` SSH redirects to CT `27050` (`192.168.27.50`). The live Lujan NAT
audit found no Mantis forwarding rules. Router read-only verification on
October 15 confirms `.100.7` is now active with TCP `22/80/443` destination NAT
to `192.168.25.9` for Prestoprenda, while `.100.6` and `.100.8` are also active
with their planned service mappings. External A records for IoT and CEIS were
published on October 15: `iot.intelisis.com.ar` now resolves to `.100.6` and
`ceis.polodesalud.com.ar` to `.100.8`. IoT firmware HTTP and HTTPS/MQTT TLS
endpoints are deployed and verified. On October 16, the operator approved a
forced production renewal. DNS-01 issuance, protected `/ssl` deployment, and
Home Assistant/Mosquitto restarts succeeded. The deployed certificate
fingerprint matches the one served by HTTPS and MQTT TLS, hostname and chain
checks pass, and HTTPS returns 200. The External `intelisis.com.ar` SOA serial
is `2026101522` on both authorities, and public resolvers show no challenge
TXT remaining. A prior staging dry-run against the production lineage failed
with a stale staging authorization; the real production renewal completed
successfully. The IoT SSH high-port route is active and key-authenticated; the
old `8922` SSH forward was removed while MQTT `8883` remained enabled. October
16 read-only HTTP/HTTPS checks passed for CEIS; HTTPS presented a valid
certificate and returned HTTP 200 to `HEAD /`. The operator confirms CEIS was
and remains operational. The live destination-NAT rule was restricted to TCP
`80`/`443` only; unused TCP `12321`/`12323` were removed, and UDP `12321` is
not published.
Ollama is a test service at `192.168.27.10` and is published only in the
Internal DNS view. Its External DNS name remains NXDOMAIN, and it has no public
address assignment, route, or NAT. Prestoprenda's customer-managed external
DNS and service path were confirmed as verified by the operator; no local DNS
cutover or Internal record is pending.
Mantis is a private-use service that must remain reachable through the public
network on its existing custom ports. October 16 checks from this workstation
reached its HTTPS login redirect and SSH banner. The operator confirms all
Mantis ingress access control is enforced by the external firewall and accepts
transport and policy verification as sufficient; no authenticated login was
performed. Earlier Lujan mappings below are historical, not current rollback
instructions.

The operator-approved shared apex DNS targets are `aero.com.ar` and
`intelisis.com.ar` A `10.8.0.21` in Internal and A `138.121.100.4` in
External. Keep `www.aero.com.ar` and `public.aero.com.ar` as CNAMEs to
`aero.com.ar` in both views. `lujan.intelisis.com.ar` remains unchanged at
`10.8.0.21` Internal and `138.121.100.15` External. Apexes remain A records;
live authoritative publication was verified on both authorities on October
14. Internal `intelisis.com.ar` was corrected from the deleted Lujan address
`192.168.25.20` to `10.8.0.21`, and replicated to the secondary.

Lujan NAT on public apex address `138.121.100.4` and internal router address
`10.8.0.21` forwards TCP `80,443` to running TIC Gestion CT `27020` at
`192.168.27.20`. The separate customer-port audit found 95 mappings
overlapping `10000-10500` (53 enabled, 42 disabled). Current gaps and disabled
mappings were not changed; see the external DNS reconciliation record for
exact coverage.

GPS remains on `gps.aero.com.ar` / `138.121.100.2`. On October 15, both
authoritative internal DNS servers returned `192.168.25.8`; public resolvers
returned `138.121.100.2`. CORE-ROUTER-LUJAN has the address, route, and NAT
rule. On October 16, the dedicated environment SSH key authenticated over
TCP `20083` -> guest SSH `22`; this administrative mapping does not replace or
change GPS's public client ports. External TCP connection checks succeeded on
ports `80,443,5005,5027,
5055,5056,5144,8082`; `8080` was refused at both the public address and
backend `192.168.25.8`. The operator confirmed TCP `8080` is not required and
authorized removing its public NAT mapping on October 16; the live rule now
excludes it. Application-level acceptance of the remaining eight required
ports is operator-confirmed. External HTTP `HEAD` checks
returned `301` on port `80`, `200` with valid TLS on `443`, and `200` on
Traccar web port `8082`. TCP listeners on `5005` (T55), `5027` (Teltonika),
`5055` (OsmAnd), `5056` (Easytrack), and `5144` (OwnTracks) accepted
connections. Do not send synthetic telemetry to these production protocol
ports. October 16 checks again returned HTTP 301 on port `80`, HTTP 200 with
TLS 1.3 on `443`, and HTTP 200 on `8082`; TCP listeners on all five telemetry
ports accepted connections. The operator confirms protocol-level GPS
ingestion is already validated; no synthetic telemetry was sent.

IoT verification found Internal authoritative DNS returning `192.168.25.7`.
The External A and PTR resolve to `138.121.100.6`; the former `.101.3` has no
A, PTR, assignment, `/32` route, or NAT on the four audited CORE routers.
Public TCP `80` now maps to Node-RED guest port `1880`, and the effective
firmware URL `http://iot.intelisis.com.ar/endpoint/firmware` returned HTTP 200
without downloading the artifact. Public `443` and MQTT `8883` present a valid
certificate issued October 15, 2026, expiring January 13, 2027. The
fail-closed heartbeat-auth fix is deployed; unauthenticated device-command,
admin, and heartbeat probes return 401. The configured static-auth password
was rotated and the runtime secrets file is owner-only. The local production Certbot app, scoped RFC2136 grant, and protected `/ssl`
deployment/reload path are provisioned. On October 16, the operator approved
a forced production renewal; issuance, deployment, and Home Assistant/Mosquitto
restarts passed. The deployed certificate fingerprint matches the one served
by HTTPS and MQTT TLS, hostname and chain checks pass, HTTPS returned 200, and
public resolvers show no challenge TXT remaining. A prior staging dry-run
against the production lineage failed with a stale staging authorization, but
the real production renewal completed successfully. Keep the HTTP-01 add-on
stopped. On October 16, 2026, a dedicated IoT-admin public key was added
additively to the SSH add-on and authenticated over both `.100.6:8922` and the
new `.100.6:20073` high-port path. The external firewall owner confirmed the
source policy. Both paths use `iot.intelisis.com.ar`; no separate hostname or
DNS change is needed. After the new path was accepted, the old public `8922`
SSH forward was removed while MQTT on `8883` remained enabled.

CEIS External DNS now resolves `ceis.polodesalud.com.ar` to `138.121.100.8`;
Internal DNS remains `192.168.25.151`. The operator confirms CEIS was and
remains operational; the live destination-NAT rule now forwards only TCP `80`
and `443`, with a valid HTTPS certificate. Unused TCP `12321`/`12323` were
removed and UDP `12321` is not published. The former `.101.6`
address has no A, PTR, assignment, `/32` route, or NAT on the four audited
CORE routers. The later shared-proxy migration remains a separate step.

## Purpose

This document records the inspected public IPv4 assignments, the completed
Mailcow pilot cleanup, and the remaining controlled reorganization proposal.
Completed changes are explicitly identified; proposed ingress publication
still requires assignment approval.

## Service exposure classification

Classify the service's intended audience and client protocol before selecting
its ingress ports. A public DNS name or assigned public IP alone does not
establish that a service is a general-public application. Conversely, a
public-facing web service must not be moved to a nonstandard high client port:
public HTTP/HTTPS entry points remain TCP `80`/`443`, either on a dedicated
address or behind a shared reverse proxy listening on those same standard
ports. Native public protocols retain their protocol-required ports.

The server-ID high-port formula is reserved for private application access and
restricted administration where the clients are known to accept an explicit
port. A private-use service may be reachable over the public network without
being a general-public service; its access policy must still limit use to the
intended audience. The formula is not a substitute for a public web ingress.
Internal-only services receive no public publication. Unresolved services are
not eligible for any port or DNS migration until their audience, owner, and
listener inventory are confirmed.

| Existing service or group | Classification from current evidence | Port / migration rule |
| --- | --- | --- |
| CRM and Gestion (`aero.com.ar`, `intelisis.com.ar`, `www`, `public`, and TIC Gestion) | Public-standard web and customer service | Preserve HTTP/HTTPS on `80`/`443` and the approved customer range on `138.121.100.4`; do not move public web to formula ports. |
| GPS (`gps.aero.com.ar`, `.25.8`) | Public application with eight required public-standard/fixed-port TCP listeners; unused TCP `8080` was removed on October 16; SSH administration is separate | Retain its own public IP and required client-facing ports, including ports beyond `80`/`443`. SSH administration is verified at `.100.2:20083` -> `.25.8:22` using the dedicated environment key. Do not migrate GPS client ports to generic high ports or shared ingress. |
| CEIS (`ceis.polodesalud.com.ar`, `.25.151`) | Public-standard web service | External A is published at `.100.8`; Internal A remains `.25.151`. The operator confirms CEIS remains operational. Only TCP `80/443` are forwarded; all additional forwards were removed as unused. Keep its dedicated IP until a later, separately validated reverse-proxy migration. |
| Prestoprenda (`web.prestoprenda.com.ar`) | Public service whose DNS and administration are external to this environment | Retain its own public IP under the external administrator's control. Do not publish an Internal DNS record or create an Internal publication path. |
| Polodesalud apex (`138.121.101.242`) | Public zone apex on an external customer's IP | Preserve the customer-owned public IP and current route/DNS; do not reassign or fold into shared ingress. |
| IoT/Home Assistant (`iot.intelisis.com.ar`, `.25.7`) | Public application/protocol endpoints plus private administration | External A/PTR point to `.100.6`; Internal A remains `.25.7`. Public `:80` maps to guest `:1880`; the effective firmware URL is `http://iot.intelisis.com.ar/endpoint/firmware` and a capped public GET returned HTTP 200. Public `:443` and MQTT `:8883` present the renewed production certificate through January 13, 2027. Endpoint-specific authentication remains enabled and the heartbeat missing-token bypass is fixed. The runtime secrets file is owner-only and the static-auth password was rotated. On October 16, forced production renewal, protected `/ssl` deployment, and Home Assistant/Mosquitto restarts passed; deployed and served fingerprints match, HTTPS returns 200, and MQTT TLS hostname/chain checks pass. The former `.101.3` has no A/PTR/route/NAT. The dedicated IoT-admin key authenticates over `.100.6:20073`; public SSH port `8922` was removed while MQTT `8883` remains enabled. |
| Authoritative DNS (`ns1`, `ns2`) and production Mailcow | Public-native protocol infrastructure; Mailcow is multi-tenant for all hosted domains | Retain DNS TCP/UDP `53` and the existing Mailcow service/IP. Use `mail.intelisis.com.ar` as the canonical mail host; service-host aliases across hosted domains should CNAME to it, while each domain apex retains its own MX and mail-authentication records. |
| PVE/PBS/PDM, WEB/Nginx UI, Netmgr, edge-router management, and server GUI/SSH consoles | Private-use administration, reached through site routers | Use the documented high-port scheme on the existing site-router public address and the corresponding private router address in Internal DNS. Keep the access policy restricted to the intended users; never treat high ports as a substitute for access control. |
| Development (`development.intelisis.com.ar`) | Private-use service; only SSH administration is observed, reachable through a public-network endpoint | Formula ports apply to its private SSH administration after target/listener and external-firewall verification. Keep public-network exposure limited to the intended administrators. Do not infer a public web service from the DNS name or move any future public web listener off `80`/`443`. |
| Database (`db1.intelisis.com.ar`) | Private database-client service; external route acceptance was waived | Existing `20253`/`20254` paths are not a public-web precedent. Keep clients restricted and confirm they support the configured client ports; do not expose a general-public web service this way. |
| PBX (`pbx.aero.com.ar`, `pbx.polodesalud.com.ar`) and Softswitch | Internal-only voice services | No public NAT. Preserve SIP/RTP native service behavior internally; no generic high-port publication. |
| Mantis (`mantis.intelisis.com.ar`) | Private-use application, intentionally reachable through the public network | Retain TIC HTTPS `20502` -> `443` and SSH `20503` -> `22`; these are private-audience high-port endpoints, not general-public web ingress. Preserve the existing external-firewall access policy and application authentication. |
| Projects (`projects.intelisis.com.ar`) | Unresolved; guest is stopped and current NAT is unrestricted | No reactivation or migration. Confirm ownership, audience, listeners, and a scoped replacement plan first. |
| S3 (`s3.intelisis.com.ar`, CT `27028`) | Private application/API and administration; Internal A currently points to `192.168.27.28`; External DNS currently returns authoritative NXDOMAIN | Replace the Internal direct A with a CNAME to `tic.intelisis.com.ar` and publish the same CNAME externally only as part of a staged private-access cutover. Stage high-port NAT on TIC for verified HTTPS API `443` -> `20282` and GUI backends `9443`-`9445` -> `20284`-`20286`, with administrative allowlisting. Do not expose native loopback backends. |
| Ollama (TIC CT `27010`, `192.168.27.10`) | Internal-only test service; guest API listens on TCP `11434` | Publish `ollama.intelisis.com.ar` only in the Internal view at `192.168.27.10`. Keep it absent from External DNS and do not assign a public IP, route, or NAT. The retired `.101.4` address is not reserved for Ollama. |
| Network Orchestrator / Netmgr (Lujan CT `25070`, `.25.70`) | Private-use management/status service; established site-router paths use TCP `20701`/`20702`/`20703` for HTTP/HTTPS/SSH | Retain the existing Internal and External CNAMEs to `lujan.intelisis.com.ar`; External publication is already documented as complete. Public access is through assigned high ports and remains subject to the existing firewall policy. Do not treat the status UI as public-standard web ingress. |
| LTS server and groupware identities | Deprecated by operator direction | `groupware.aero.com.ar` was removed from Internal DNS on October 16; public resolvers already returned NXDOMAIN. `groupware.pro3d.com.ar` is already retired. `lts-server.intelisis.com.ar` has no matching record in the assessed zones, so confirm no record exists elsewhere. DNS retirement does not authorize stopping/deleting the LTS guest. |
| Retired PMS, Database legacy IP, Aero services/fileserver/ownCloud/wiki, and pilot address | Retired | Do not recreate or reuse without separate approval. |

This is a service-level classification, not an address-level assertion: a
shared router public IP can carry separate public-standard, native-protocol,
and restricted-administration endpoints. The machine-readable public-address
reconciliation records the address-level class and separately flags whether
high-port migration is permitted. Projects and other unclassified services
remain explicit owner/verification gates. S3 is private administration staged
for high-port NAT. Ollama is Internal-only at `192.168.27.10` and has no public
DNS or router exposure. Netmgr's External
CNAME already targets the Lujan router identity and its service ports remain
high-port.
Prestoprenda is externally managed and must
not receive Internal publication. Mantis is private-use with a
public-network access path. October 16 transport checks from this workstation
reached its HTTPS login redirect and SSH banner. The operator confirms all
Mantis ingress access control is enforced by the external firewall and accepts
transport and policy verification as sufficient; a subsequent authenticated
web login reached the dashboard with TLS verification enabled. No issue or
customer records were read or changed.

### Target address and DNS layout (operator direction, October 15)

Use a shared standard-port web ingress to reduce public-IP consumption, but do
not force every public service onto it. Retain dedicated addresses where a
service requires multiple fixed/public ports, is still awaiting cutover, is
externally owned, or is explicitly customer-owned. This target layout does not
authorize live DNS, router, or firewall changes.

| Service / role | External DNS and public address | Internal DNS / access | Disposition |
| --- | --- | --- | --- |
| Public web shared ingress: CRM/Gestion now; eligible web services later | Keep `aero.com.ar` and `intelisis.com.ar` A records on `138.121.100.4`; retain `www.aero.com.ar` and `public.aero.com.ar` CNAMEs. Use this existing address as the shared `80`/`443` reverse-proxy candidate after proxy and CRM-route validation. | Resolve public-web names to an approved internal proxy/backend address; do not assume the public or router address is the correct internal target. | No new public IP for each virtual host. Keep the CRM customer-port range on `.100.4`. |
| GPS | `gps.aero.com.ar` remains on `138.121.100.2`; its public client ports are unchanged. | Keep its existing Internal path and standard/fixed client ports; dedicated-key SSH is verified at `.100.2:20083` -> `.25.8:22`. | Retain its dedicated address and client ports, including ports beyond `80`/`443`; do not migrate public GPS protocols to workload ports. |
| IoT / Home Assistant | External A/PTR point to dedicated public IP `138.121.100.6`; the former `.101.3` has no A/PTR or observed CORE assignment/route/NAT. | Internal DNS remains `.25.7`. | Firmware HTTP on `80`, renewed TLS on `443`/`8883`, and key-based SSH on high port `20073` are verified. Public SSH `8922` was retired; no DNS change was needed. |
| Prestoprenda | `.100.7` is the assigned public endpoint with TCP `22/80/443` NAT to `.25.9`; DNS remains externally administered and externally verified per operator confirmation. | No Internal A record or Internal publication. | Preserve the accepted customer-managed DNS path; no local DNS cutover or owner coordination remains pending. |
| CEIS | External A/PTR now point to `138.121.100.8`; the former `.101.6` has no A/PTR or observed CORE assignment/route/NAT. | Internal A remains `.25.151`. | The operator confirms CEIS remains operational; only TCP `80/443` are forwarded. Additional TCP/UDP forwards were removed as unused; keep the later shared-proxy migration separate. |
| Polodesalud | Keep customer-owned `138.121.101.242` and the confirmed route. | Preserve current Internal/External DNS behavior. | Customer address; do not consolidate or reassign. |
| Mailcow multi-tenant service | Keep the existing Mailcow public address `138.121.100.5`. `mail.intelisis.com.ar` is the canonical A-record host; mail service aliases across hosted domains CNAME to it. | Keep current Mailcow service path and split-view behavior. | Do not move Mailcow or change mail flow as part of web-ingress consolidation. Domain apexes keep MX/TXT; they cannot be CNAMEs. MX records should target the canonical mail host directly. |
| Authoritative DNS | Keep primary `138.121.100.1` and secondary `138.121.102.1`. | Preserve the independent Internal/External DNS paths. | Dedicated protocol and redundancy addresses. |
| Router identities / private administration | Keep Lujan `138.121.100.15`, TIC `138.121.101.15`, Centro `138.121.102.15`, and Cordoba `45.238.8.15`. | Internal DNS for private admin access resolves to the corresponding site router addresses `10.8.0.21`, `.61`, `.11`, and `.51`; use the documented service-specific high ports. | Consolidate private GUI/SSH/PVE/PBS/PDM and similar access on these existing site endpoints, with external-firewall access restrictions. |
| Mantis and Database | No separate IP: retain TIC `138.121.101.15` and their existing high-port endpoints (`20502`/`20503` and `20253`/`20254`). | Use TIC's private router/service path for authorized private users and CRM integration. | Private-use services intentionally reachable through the public network; retain intended audience restrictions. |
| Development SSH | Current `.101.8:20022` is a transitional dedicated endpoint. | Move to the TIC router high-port endpoint only after target VM, listener, and access policy are verified; preserve the old path until replacement acceptance. | Then retire `.101.8` only after a separate approved observation and allocation check. |
| S3 private API and GUIs | `s3.intelisis.com.ar` CNAME to `tic.intelisis.com.ar` proposed in External; Internal direct A is to be replaced only during cutover. | CNAME to `tic.intelisis.com.ar`; TCP `20282` -> `.27.28:443`, `20284` -> `:9443`, `20285` -> `:9444`, `20286` -> `:9445`. | Four disabled NAT entries are staged with administrative allowlisting. Verify DNS in both views, firewall policy, and end-to-end TLS before activation; keep loopback backends private. |
| Ollama test service | No public address; the former `138.121.101.4` assignment was retired after Database retirement. | Internal-only A `192.168.27.10`; External DNS remains NXDOMAIN. | Keep Ollama absent from public DNS, address assignments, routes, and NAT. |
| Netmgr | Existing External and Internal CNAMEs target `lujan.intelisis.com.ar`. | Continue using assigned high ports `20701`/`20702`/`20703`. | Existing CNAME publication is documented as complete; verify against authorities during the next live reconciliation. |
| LTS/groupware | `groupware.aero.com.ar` is retired from Internal DNS; public resolvers returned NXDOMAIN before the change. `groupware.pro3d.com.ar` is already retired. No assessed-zone A for `lts-server.intelisis.com.ar`. | Keep the deprecated groupware identity absent; confirm no LTS hostname exists elsewhere if that becomes in scope. | Internal authoritative NXDOMAIN is verified on both authorities at SOA `2026101601`; External zone was unchanged. Do not stop or delete LXC `25004` without separate approval. |
| IoT/Home Assistant | External A/PTR point to `.100.6`; former `.101.3` has no A/PTR or CORE assignment/route/NAT. | TCP `.100.6:20073` -> `.25.7:8922` is active using the existing `iot.intelisis.com.ar` hostname; no DNS change or separate admin hostname is needed. External firewall policy and key-based access are verified. The old public `.100.6:8922` forward is retired, preserving MQTT on `8883`. No RouterOS source restriction is planned. | Public `80` maps to guest `1880`, and `http://iot.intelisis.com.ar/endpoint/firmware` returned HTTP 200. HTTPS `443` and MQTT TLS `8883` serve the renewed certificate through January 13, 2027. Forced production renewal, deployment, and service restarts passed October 16. Heartbeat auth is fail-closed and deployed; unauthenticated endpoint probes returned 401. The runtime secrets file is owner-only and static-auth was rotated. SSH key authentication is verified on `20073`. |
| Projects | Existing `.102.6` publication is unresolved and the guest is stopped. | No new Internal or NAT publication. | Do not activate or migrate; resolve ownership and separately approve any retirement. |

The public web address target is therefore shared ingress, not one address per
server. Public-IP reduction is realized only after eligible web services pass
their proxy cutovers; GPS, CEIS (until its planned cutover), Prestoprenda, the
customer-owned Polo address, DNS, Mailcow, and current protocol-specific
services retain their stated exceptions.
Mantis is private-use with a public-network access path; external client-path
acceptance remains unverified.

The October 12 snapshot below is historical for `pro3d.com.ar`: on October 13,
the operator retired that zone from both local BIND views. The parent still
delegates to Spaceship nameservers, which returned `REFUSED`; public recursive
DNS consequently returns `SERVFAIL`. Pro3d identities shown in the historical
inventory below must not be treated as currently published by this BIND pair.

The source snapshot was read directly from primary DNS CT `25100`:

- `/var/lib/bind/aero.com.ar.External.hosts`
- `/var/lib/bind/intelisis.com.ar.External.hosts`
- `/var/lib/bind/polodesalud.com.ar.External.hosts`
- `/var/lib/bind/pro3d.com.ar.External.hosts`
- `/var/lib/bind/138.121.100.External.rev`
- `/var/lib/bind/138.121.101.External.rev`
- `/var/lib/bind/138.121.102.External.rev`
- `/var/lib/bind/138.121.103.External.rev`

The post-cleanup zones were recompiled with their active journals on October
12, 2026 and reconciled against live CORE-router address and destination-NAT
state. The detailed result is in
[EXTERNAL_DNS_SERVICE_RECONCILIATION.md](./EXTERNAL_DNS_SERVICE_RECONCILIATION.md).
The machine-readable inventory is
`config/external_dns_reconciliation.yaml`, validated via
`dns-environment validate`.

Forward-zone serials at inspection time were:

| Zone | External serial |
| --- | ---: |
| `aero.com.ar` | `2026101102` |
| `intelisis.com.ar` | `2026101120` |
| `polodesalud.com.ar` | `2026101103` |
| `pro3d.com.ar` | `2026101102` |

## Current forward assignments

The four External forward zones contained 15 unique IPv4 addresses in A records
at the October 12 snapshot. Mail migration removed the pilot use of
`138.121.100.8`; it was subsequently assigned to CEIS, and the CEIS External A
was published there on October 15. The current reconciliation records 14
unique addresses in active External A records. Multiple DNS names sharing one
address are grouped below.

| Public IP | External DNS identities | Current role | Proposed disposition |
| --- | --- | --- | --- |
| `138.121.100.1` | `ns1.aero.com.ar`, `ns1.intelisis.com.ar`, `ns1.polodesalud.com.ar`, `ns1.pro3d.com.ar` | Primary authoritative DNS | Preserve as dedicated DNS infrastructure |
| `138.121.100.2` | `gps.aero.com.ar` | Public GPS application with multiple standard/fixed ports | Retain and verify its existing dedicated public IP and required client ports |
| `138.121.100.3` | PBX Internal-only at `192.168.26.6`; no External A/PTR or CORE NAT | PBX/voice service | Keep Internal-only; do not publish or add NAT |
| `138.121.100.4` | `aero.com.ar`, `intelisis.com.ar` | CRM/Gestion standard-port web ingress | Preserve; candidate shared reverse-proxy address after proxy and CRM-route validation |
| `138.121.100.5` | Mailcow multi-tenant service | Shared production mail address | Preserve current mail service/IP; canonical mail host is `mail.intelisis.com.ar` |
| `138.121.100.6` | `iot.intelisis.com.ar` External A/PTR | Firmware HTTP, renewed HTTPS/MQTT TLS, forced production renewal/deployment, external firewall policy, and SSH-key authentication on `20073` verified October 16 | Public SSH `8922` has been retired; MQTT remains on `8883` |
| `138.121.100.7` | Prestoprenda public endpoint; externally administered DNS | Lujan assignment and TCP 22/80/443 NAT to `.25.9` | Retain its own public IP; no Internal DNS publication |
| `138.121.100.8` | `ceis.polodesalud.com.ar` External A/PTR | TCP 80/443 only; HTTPS certificate is valid; operator confirms CEIS remains operational | Published October 15; additional forwards removed October 16 |
| `138.121.100.15` | `web.intelisis.com.ar`, `lujan.intelisis.com.ar` (A); TIC is the Mantis CNAME target | Shared Lujan workload endpoints | Preserve current assigned services; Mantis now routes through TIC |
| `138.121.101.2` | No local External A/PTR observed; not the current Prestoprenda endpoint | No current Lujan address assignment, route, or NAT observed | Retired from the current service path; do not reassign without separate allocation confirmation |
| `138.121.101.3` | No External A or PTR; former IoT endpoint | No assignment, `/32` route, or NAT on four audited CORE routers; current External A/PTR use `.100.6` | Retired as the IoT forward endpoint; confirm allocation before reuse |
| `138.121.101.4` | No A or PTR; former `database.intelisis.com.ar` PTR retired October 14 | Address removed from Lujan loopback; no Ollama assignment, route, or NAT | Retired; not reserved for Ollama or available for reuse without separate allocation confirmation |
| `138.121.101.6` | No External A or PTR; former CEIS endpoint | No assignment, `/32` route, or NAT on four audited CORE routers; current External A/PTR use `.100.8` | Retired as the CEIS forward endpoint; confirm allocation before reuse |
| `138.121.101.7` | No A or PTR after PMS retirement | Retired PMS endpoint; no CORE address, route, or NAT | Keep retired; do not reuse |
| `138.121.101.8` | `development.intelisis.com.ar` | Transitional private SSH endpoint; distinct from proposed CEIS address `.100.8` | Migrate private SSH only after target verification, then retire `.101.8` separately |
| `138.121.101.242` | `polodesalud.com.ar` | Public zone apex on an external customer's IP; routed through Lujan PPPoE-in `backbone-16` | Preserve customer ownership, address, DNS, and route |
| `138.121.101.246` | `pro3d.com.ar` | Public zone apex | Preserve until an apex migration is explicitly approved |
| `138.121.102.1` | `ns2.aero.com.ar`, `ns2.intelisis.com.ar`, `ns2.polodesalud.com.ar`, `ns2.pro3d.com.ar` | Secondary authoritative DNS | Preserve as dedicated DNS infrastructure |
| `138.121.102.6` | `projects.intelisis.com.ar` | Powered-off, unresolved Projects application | Do not activate or migrate; separately approve any publication retirement |

## Other public-IP declarations

SPF records authorize these public source addresses:

| Public IP | SPF use |
| --- | --- |
| `138.121.100.5` | Production mail for `aero.com.ar`, `intelisis.com.ar`, `polodesalud.com.ar`, and `pro3d.com.ar` |
| `138.121.100.8` | Obsolete pilot SPF authorization; remove with the pilot DNS cleanup |

`138.121.100.5` remains the only retained production mail address. It must not
be reassigned without coordinated mail-flow, SPF, reverse-DNS, reputation, and
deliverability validation.

## Reverse-DNS observations

| Public IP | External PTR |
| --- | --- |
| `138.121.100.1` | `ns1.intelisis.com.ar` |
| `138.121.100.4` | `aero.com.ar` |
| `138.121.100.5` | `mail.intelisis.com.ar` |
| `138.121.100.6` | `iot.intelisis.com.ar` |
| `138.121.100.8` | `ceis.polodesalud.com.ar`; retired pilot PTR cleanup verified October 14 |
| `138.121.101.3` | No PTR; IoT PTR moved to `.100.6` on October 15 |
| `138.121.101.4` | No PTR; former `database.intelisis.com.ar` PTR retired October 14; address remains retired and is not reserved for Ollama |
| `138.121.101.6` | No PTR; CEIS PTR moved to `.100.8` on October 15 |
| `138.121.101.7` | No PTR; PMS retired October 14 |
| `138.121.102.1` | `ns2.intelisis.com.ar` |
| `138.121.102.6` | `projects.intelisis.com.ar` |

`138.121.101.4` has no External A or PTR record; its Lujan loopback assignment
and dynamic `/32` route were removed after Database retirement. It is retired
and is not allocated or reserved for Ollama. The current database identity
remains `db1.intelisis.com.ar` on `138.121.101.15`.

An A record without a PTR does not prove a defect for HTTP services, and a PTR
without an A record does not prove that an address is unused. Forward/reverse
consistency should be decided according to each service's protocol and
operational requirements.

## Related DNS findings

- `138.121.100.4` remains the approved External A target for both apexes; it is
  not available for a separate ingress assignment.
- `pbx.aero.com.ar` is Internal-only at `192.168.26.6`; its External A record
  was removed. No PBX destination NAT exists on the four audited CORE routers.
- PMS was retired: its Internal and External A records and External PTR were
  removed. Its former `.101.7` assignment was not found on the audited CORE
  routers.
- The former Database address `138.121.101.4` was removed from the Lujan
  loopback and all four audited CORE routers; it has no External A or PTR.
  It is now selected for Ollama, pending allocation and route reactivation
  verification.
- `public.aero.com.ar` and `www.aero.com.ar` remain CNAMEs to `aero.com.ar`,
  so they depend on `138.121.100.4`. `gestion.aero.com.ar` is retired and
  must not be recreated.
- `services.aero.com.ar`, `fileserver.aero.com.ar`, `owncloud.aero.com.ar`,
  and `wiki.aero.com.ar` were retired from their applicable Aero views on
  October 14. All return authoritative NXDOMAIN in both views on both
  authorities. No application or address ownership is implied by the
  historical `192.168.25.10` records.
-   `web.intelisis.com.ar` is published through TCP `20602` to
  `192.168.25.60:443`, with SSH TCP `20603` to `192.168.25.60:22`. The same
  mappings are active through Internal router address `10.8.0.21`. Source
  policy remains with the external firewall.
- No External A or PTR declarations from `45.238.8.0/22` were observed in the
  inspected zones. This is not evidence that the range is unallocated.

## Completed mail migration cleanup

Production mail is consolidated on Mailcow using `138.121.100.5`. The former
pilot namespace is no longer part of the target design. The following observed
External records should be removed as one coordinated DNS change:

| Record | Current value |
| --- | --- |
| `mailcow-pilot.intelisis.com.ar A` | `138.121.100.8` |
| `pilot.intelisis.com.ar MX` | `10 mailcow-pilot.intelisis.com.ar` |
| `pilot.intelisis.com.ar TXT` | `v=spf1 ip4:138.121.100.8 -all` |
| `_dmarc.pilot.intelisis.com.ar TXT` | Pilot DMARC policy |
| `dkim._domainkey.pilot.intelisis.com.ar TXT` | Pilot DKIM public key |
| `autoconfig.pilot.intelisis.com.ar CNAME` | `mailcow-pilot.intelisis.com.ar` |
| `autodiscover.pilot.intelisis.com.ar CNAME` | `mailcow-pilot.intelisis.com.ar` |
| `8.100.121.138.in-addr.arpa PTR` | `mailcow-pilot.intelisis.com.ar` |

Before deletion, confirm that Mailcow has no `pilot.intelisis.com.ar` domain,
mailbox, alias, transport, certificate, monitoring check, or queued message
dependency. Remove the forward records through the dynamic External-zone update
path, remove the PTR through the authoritative reverse-zone procedure, verify
primary/secondary replication, and verify public recursive answers after TTL
expiry.

At the October 12 pilot cleanup, removing those records did not by itself make
`138.121.100.8` available. The operator subsequently selected the address for
CEIS. On October 15, its Lujan assignment, routes, and NAT were verified and
the CEIS External A was published. The reverse PTR remains absent; do not
infer reverse-DNS readiness from the forward record.

### PVE/PBS audit result

The read-only audit found no separate pilot VM or container. VM `25040` is the
running production Mailcow guest (`mail.intelisis.com.ar`) and remains in the
Lujan HA resource set. It must not be deleted or removed from HA.

The following stale pilot references were cleaned up on 2026-10-12:

- The PVE VM `25040` retains the production name
  `mail.intelisis.com.ar`; its stale pilot description was replaced.
- The PVE Ceph-capacity monitor sender is now
  `watchdog@mail.intelisis.com.ar` and its post-change run succeeded.
- The pilot forward records were removed from External DNS at serial
  `2026101121`.
- The pilot reverse PTR was removed at serial `1503626320`.
- CORE ROUTER LUJAN no longer assigns `138.121.100.8/32` to `lo`; its two
  disabled Mail Management NAT rules were removed and the connected route
  disappeared automatically.

The current PBS inventory also contains a later snapshot noted as
`mail.intelisis.com.ar`, confirming that the backup set is not pilot-only.
All three backups were retained: the two historical pilot-labelled recovery
artifacts and the later production snapshot. No deletion of VM `25040`, its HA
entry, or its PBS snapshots was performed.

DNS backups are retained under the root-only directory
`/root/mailcow-pilot-dns-cleanup-20261012T154202Z/` on CT `25100`. The
allocation/reuse warning above records the state at that cleanup; the address
was subsequently assigned and verified for CEIS on October 15.

## Availability warning

Absence from External DNS proves only **no A or PTR record was observed**. It
does not prove that an address is free, routed to the desired site, absent from
NAT, unused by a firewall object, assigned outside DNS, reserved by an ISP, or
safe to reuse.

Before assigning any public address, validate it against:

1. Edge-router interface and ARP/neighbor state.
2. Destination NAT and source NAT rules.
3. Firewall address lists, rules, and published-service objects.
4. Load balancers, upstream provider assignments, and static routes.
5. Current traffic counters and packet capture during an observation window.
6. Monitoring, asset inventory, and service-owner confirmation.
7. Forward DNS, reverse DNS, SPF, certificate, and application dependencies.

## Proposed target model

### Shared standard-port web ingress

Do not allocate another public IP solely for HTTP/HTTPS virtual hosts. Preserve
`138.121.100.4` as the existing CRM/Gestion standard-port ingress and evaluate
it as the shared reverse-proxy address. The live path currently forwards
TCP `80`/`443` to TIC Gestion; it is not yet evidence that a reverse proxy has
been installed or validated. Before adding host-based routes, verify proxy
ownership, CRM behavior, certificates, backend routing, and customer-port
separation. Do not expose Nginx UI's loopback backend port `9000`.

Eligible public web names can then use External A/CNAME records to the shared
ingress, with the proxy listening on standard TCP `80`/`443`. Internal DNS
should resolve each name to an approved internal proxy or backend endpoint.
The operator separately selected dedicated addresses for GPS (`.100.2`,
already documented), IoT (`.100.6`), Prestoprenda (`.100.7`), and CEIS
(`.100.8`). These are service-address assignments, not shared-proxy targets;
verify allocation and routing before cutting over. Keep the customer-owned
Polo address, Mailcow, authoritative DNS, and existing site-router addresses
in their separate roles.

### Mailcow and domain aliases

Keep the existing multi-tenant Mailcow service on `138.121.100.5`. Use
`mail.intelisis.com.ar` as its canonical A-record hostname. Mail service
hostnames in other hosted domains, and service subdomains such as `imap`,
`smtp`, `autoconfig`, and `autodiscover`, may CNAME to that canonical hostname
when their certificate and client-discovery behavior are validated. The
domain apexes themselves must not be CNAMEs: retain each apex's MX and
mail-authentication records, and point MX records directly to the canonical
mail host. Keep existing behavior unchanged until a separately reviewed DNS
change is approved.

### Private server administration

Use the existing public site-router addresses (`138.121.100.15`,
`138.121.101.15`, `138.121.102.15`, and `45.238.8.15`) for private-use server
consoles, GUIs, and SSH that must be reachable over the public network. Apply
the documented high-port formula per server and verified backend listener.
Internal DNS should resolve those private-use names to the corresponding
private site-router address (`10.8.0.21`, `.61`, `.11`, or `.51`) where router
NAT is required. Continue applying audience restrictions at the external
firewall; high ports are not an access-control mechanism. Mantis, Database,
and Development follow this model, with Development's existing `.101.8`
endpoint retained until an approved replacement is verified.

### Controlled migration order

1. Verify selected-address allocation, router assignments, routes, NAT,
   firewall objects, monitoring, and provider ownership for `.100.6`, `.100.7`,
   `.100.8`, and the reactivation of `.101.4`.
2. Keep GPS on `.100.2` with its existing public service; its authoritative DNS
   and router forwarding are verified. The operator confirmed protocol-level
   ingestion acceptance for the eight required TCP ports. TCP `8080` was
   removed from the public NAT mapping on October 16 with operator
   authorization.
3. IoT DNS and firmware HTTP plus HTTPS/MQTT TLS endpoints are verified on
   `.100.6`. The approved IoT-local Certbot app, scoped RFC2136 grant, and
   protected deploy/reload hook are provisioned; forced production renewal,
   deployment, and HTTPS/MQTT verification passed October 16. Migrate
   administration only after the external firewall policy and high-port path
   are accepted.
4. Coordinate Prestoprenda's external DNS owner and move its observed NAT path
   from `.101.2` to `.100.7` only after verifying the legacy `.100.7:443`
   compatibility rule, destination, and client behavior. Do not publish
   Internal DNS.
5. CEIS now uses `.100.8` and is operator-confirmed operational. Only TCP
   `80`/`443` are forwarded; additional forwards were removed as unused.
   Consider its separate shared-proxy migration independently.
6. Reactivate `.101.4` for Ollama only after allocation and route verification,
   external TLS termination, and API authentication are confirmed; keep
   TCP `11434` NAT disabled until then.
7. Consolidate private console/GUI/SSH access onto each site's existing `.15`
   router address using the high-port registry, one verified service at a time.
8. Keep Mailcow, DNS, customer-owned Polo, and unresolved Projects in their
   documented current states. Any additional change requires separate
   protocol/owner approval.

For every approved web migration, verify upstream health, TLS identity,
headers, sessions, uploads, and WebSockets; test from an independent external
network; retain rollback; and remove an old address only after acceptance and
the agreed observation period.

## Proposed address-role policy

This policy describes the desired organization; it does not retroactively
declare unused addresses:

| Range / address | Intended role |
| --- | --- |
| `138.121.100.1` and `138.121.102.1` | Authoritative DNS |
| `138.121.100.5` | Production mail egress/ingress |
| `138.121.100.15`, `138.121.101.15`, `138.121.102.15`, and `45.238.8.15` | Per-site router identities and private-service high-port ingress; not the default for public-standard web |
| `138.121.100.4` | Existing CRM/Gestion standard-port ingress and candidate shared web reverse-proxy address after validation |
| `138.121.100.2` | Dedicated public GPS service; retain and verify its multiple public client ports |
| `138.121.100.6` | IoT firmware HTTP, renewed HTTPS/MQTT TLS, and key-based SSH on high port `20073` are verified; old SSH port `8922` is retired |
| `138.121.100.7` | Prestoprenda endpoint with router assignment/NAT verified; externally managed DNS and no Internal publication |
| `138.121.100.8` | CEIS External A is published; operator confirms operational. Only TCP `80`/`443` forwarded; additional forwards removed |
| `138.121.101.4` | Retired after Database service retirement; not assigned or reserved for Ollama |
| `138.121.101.242` | External customer-owned Polodesalud public IP; preserve |
| Existing application addresses | Transitional only, retired after migration and observation |
| High addresses such as `138.121.101.242` and `.246` | Preserve until apex-service ownership and routing are documented |

## Cluster edge publication proposal

### Live implementation audit

The four CORE routers were inspected through their RouterOS APIs on
2026-10-12. The proposed per-site `.15` publication model is not currently
implemented for workloads:

| Site | Live edge address | State | Workload destination NAT on this address |
| --- | --- | --- | --- |
| Lujan | `138.121.100.15/32` on `lo` | Enabled, `Router Public` | None |
| TIC | `138.121.101.15/32` on `lo` | Enabled, `TIC Public` | None |
| Centro | `138.121.102.15/32` on `lo` | Enabled, `Router Public` | None |
| Cordoba | `45.238.8.15/22` on `lo` | Enabled, `Aero Public` | None |

The only observed workload NAT at or above port `20000` is the existing TIC
development SSH mapping:

`138.121.101.8:20022 -> 192.168.27.15:22`

It does not use the TIC `.15` address and is therefore a migration candidate,
not an example of the final design.

The October 16 fleet audit verified all four management ports on the 199
API-reachable routers. The fleet-wide router-management target is the exclusive
`28000-28999` block. RouterOS also uses several dynamic routing, detection,
and WireGuard ports above `30000`, so workload allocations remain in their
separate registered ranges.

### Target edge addresses

The target model is one workload-ingress address per site:

| Site | Target public ingress | Current readiness |
| --- | --- | --- |
| Lujan | `138.121.100.15` | Address exists; NAT and firewall policy required |
| TIC | `138.121.101.15` | Address exists; NAT and firewall policy required |
| Centro | `138.121.102.15` | Address exists; NAT and firewall policy required |
| Cordoba | `45.238.8.15` | Address exists; NAT and firewall policy required |

Cordoba remains aligned with its locally originated `45.238.8.0/22` public
range. The existing `45.238.8.15` assignment is the target workload-ingress
address; no `138.121.103.15` assignment or cross-site `/32` routing change is
part of this proposal.

### Router management block

Reserve `28000-28999` exclusively for management services hosted by the edge
router itself. Use the following target standard:

| Router service | Target TCP port |
| --- | ---: |
| SSH | `28022` |
| Winbox | `28291` |
| RouterOS API | `28728` |
| RouterOS API TLS | `28729` |

The four services are normalized from their native RouterOS ports into the
`28xxx` range. Routing protocols and WireGuard retain their separately
managed ports; they are not management services and must not be folded into
this block.

Router port migration must be performed one edge at a time:

1. Save a RouterOS export and preserve an out-of-band or already authenticated
   recovery path.
2. Converge one router at a time and verify access immediately.
3. Update MIKROTIK-MANAGER inventory and operator connection profiles for
   that router.
4. Verify all four new service ports before considering that router complete.
5. Remove obsolete input rules only after the new management path is proven.
6. Reconcile the 15 API-unreachable routers individually; update their
   management-port references only after authenticated live verification.

The staged management-port rollout is complete on all 199 API-reachable
routers, and the local service snapshots and state ledgers have been
reconciled. Fifteen routers remain unverified and require a working management
path before their service state can be confirmed or changed. The normalization
policy expresses the fleet target but does not prove convergence on those
unreachable devices.

### October 12 CORE migration snapshot (historical; superseded October 14)

At the October 12 checkpoint, the four CORE routers used the old `20xxx`
management ports. The October 14 reconciliation above supersedes that
checkpoint: the CORE services have since moved to `28xxx`.

CORE ROUTER TIC completed that historical pilot on 2026-10-12:

- SSH remained on `20022`.
- Winbox moved from `28291` to `20291`.
- API moved from `28728` to `20728`.
- API TLS moved from `28729` to `20729`.
- Authenticated API verification passed and all three old ports closed.
- Inventory and Winbox profiles were updated.
- The existing unrestricted provider exposure was preserved by explicit
  operator decision; source-policy hardening remains separate.
- The normalization target at that checkpoint declared `20xxx`; the current
  fleet target is documented in the October 14 status above.

### Deterministic workload-port allocation

The operator-approved October 15 policy uses a three-digit server ID, normally
the destination workload IPv4 final octet, zero-padded. IDs must be unique
among servers using the same site router/public ingress; allocate an alternate
registry ID if final-octet IDs would collide.

Each server may receive up to 20 client-facing mappings in two batches:

```text
Batch 1: client_port = 20000 + (server_id * 10) + slot
Batch 2: client_port = 30000 + (server_id * 10) + slot
slot = 1..10 in each batch
```

Use Batch 1 for the first ten mappings and Batch 2 for mappings 11-20,
restarting the slot at 1. Slots 1, 2, and 3 are HTTP, HTTPS, and SSH; slots
4-10 are individually registered service mappings. Batch 2 reuses the same
slot meanings. Do not exceed 20 mappings per server; for a requirement above
20, recommend a dedicated public IP instead of extending the formula.

For example, server ID `060` uses `20601` for HTTP, `20602` for HTTPS, and
`20603` for SSH in Batch 1, then `30601`-`30610` in Batch 2. The active WEB
ports `20602`/`20603` and Mantis ports `20502`/`20503` already follow the
server-ID formula. The router translates each client port to the existing
backend listener; do not change the server-side port.

Check the canonical registry for collisions before allocating a port. Batch 2
uses `30000+`; inspect RouterOS dynamic services and tunnel listeners before
reserving or enabling a mapping in that range. Router management remains
separate at `28000-28999`.

**SSH is mandatory for every private/restricted server included in this
workload-ingress migration.** Each endpoint's registry entries must include its selector-3
destination-NAT and corresponding forward policy; these remain enabled while
the server is active, including during DNS/NAT migration. Do not remove an old
working SSH mapping until its replacement is enabled and verified. Preserve
the guest's actual SSH listener rather than changing its backend port; for
example, the IoT appliance's recorded SSH listener is `8922`, so any
separately approved administrative path must target `8922`, not assume port
`22`. The external firewall continues to own source restrictions and must
apply the approved access policy. Public-standard and public-native services
retain their current client-facing ports and are not included in this
high-port SSH rule.

After applying the service classification above, Development and IoT private
Development SSH and remaining workload high-port paths are staged as disabled
proposals; IoT's high-port SSH rule is active:

| Service | Destination listener mapping | DNS target when migrated |
| --- | --- | --- |
| Development, current VM `.27.15` | Existing TCP `20022 -> 22`; retain until a replacement is enabled and verified | Current public endpoint; no DNS change approved |
| Development, proposed VM `.27.65` | TCP `20653 -> 22`, only after the VM/address, admin-only audience, and listener are verified | CNAME to `tic.intelisis.com.ar` only after an approved cutover |
| IoT/Home Assistant, VM `.25.7` | Active TCP `.100.6:20073 -> 192.168.25.7:8922`; external firewall policy verified; public TCP `8922` removed, with no RouterOS source restriction | Keep the existing `iot.intelisis.com.ar` External A/PTR and Internal A unchanged; no separate administrative hostname |

These Development and IoT paths are administrative, not public web
publication. `20653` remains a proposal; `20073` is active and end-to-end
verified. The dedicated IoT-admin key works on the new path; public `8922` has
been retired while MQTT `8883` remains active. No IoT DNS change is needed. GPS and
CEIS public listeners remain on their dedicated IPs and existing ports;
IoT's public application, MQTT/TLS, and firmware paths remain on its dedicated
IP, with only SSH separated for private administration. Projects remains
stopped and unclassified; do not stage or activate a replacement. Keep all
existing dedicated addresses reserved until their service cutovers and IP
dispositions are explicitly approved.

The high port is the router-facing port only. The router translates it to the
service's existing listening port on the workload; do not change the workload
service port as part of this migration. Every mapping must be present in the
reviewed `MIKROTIK-MANAGER/config/public_nat_registry.yaml` with site, public
address, client-facing protocol/port, destination address/port, service owner,
FQDN, source policy, certificate lineage where applicable, change reference,
and rollback rule. The registry must contain no credentials or certificate
private material.

### TLS and DNS behavior

Destination NAT remains layer 4 and must not terminate or replace TLS. Each
for private/restricted high-port access, the External DNS name points to the
site's `.15` router address while the client connects to the allocated
external port. This does not apply to public-standard web services: their
External DNS points to the dedicated or shared standard-port ingress and users
connect on TCP `80`/`443`. The destination server continues presenting its
existing local certificate:

`https://service.example:external-port -> site .15:external-port -> internal-ip:native-port`

TLS certificates validate hostnames, not TCP port numbers. The certificate
must therefore contain the exact external FQDN. Keep DNS-01 renewal and the
existing local deployment hooks; no public port `80` or `443` is required for
renewal.

For private/restricted services selected for router redirection, Internal DNS
may resolve names to the appropriate private border-router address in
`10.8.0.0/24` instead of directly to a workload address in `192.168.24.0/22`.
Clients may use the assigned high port only when their audience and software
support an explicit port. The router translates that port to the workload's
unchanged listener. Add and verify the matching private-side destination-NAT
and forward policy before changing each Internal DNS record. Public-standard
services must continue to accept requests on TCP `80`/`443`; if they share an
ingress, the reverse proxy must listen on those standard ports.

The active private router addresses confirmed from the four CORE routers on
October 13, 2026 are:

| Site | Router | Private router address |
| --- | --- | --- |
| Lujan | `CORE-ROUTER-LUJAN` | `10.8.0.21/32` |
| TIC | `CORE-ROUTER-TIC` | `10.8.0.61/32` |
| Centro | `CORE-ROUTER-CENTRO` | `10.8.0.11/32` |
| Cordoba | `CORE-ROUTER-CORDOBA` | `10.8.0.51/32` |

`service.internal-FQDN -> site router 10.8.0.x:client-facing-port -> workload private-ip:existing-service-port`

Keep the existing routed reachability to `192.168.24.0/22` and direct workload
access available during this compatibility phase. Do not withdraw routes,
block direct access, or otherwise make those subnets unreachable as part of an
individual DNS/NAT migration. Clients with cached DNS, static addresses, or
legacy connection definitions may continue to depend on the direct path.
Prove the router-NAT path per service, retain the direct path through the
agreed observation and compatibility period, and handle route withdrawal or
network blocking only as a separately approved final phase.

Rollback for an individual service must restore its previous Internal DNS
answer and disable the new private-side NAT/forward rules while leaving the
existing direct routes intact.

DNS does not carry port numbers. Only restricted/private clients use an
assigned high client-facing port in their URL or connection settings. Public
web clients continue to use standard `80`/`443` URLs. External and Internal DNS
may return different router addresses; do not add broad hairpin NAT.

### Security and routing policy

- Create one explicit destination-NAT rule per protocol/port mapping. Match the
  exact `.15` destination address; never use a catch-all destination.
- Use high client-facing ports only for classified private/restricted
  services, translating to their unchanged workload listeners. Public web
  ingress remains on TCP `80`/`443`; public DNS, mail, and other fixed
  protocols retain their required ports. Nonstandard ports are not a security
  boundary. Do not add RouterOS source-address restrictions. Enforce approved
  source policy at the external firewall, with explicit forward-chain allows
  and default-deny policy. During compatibility, direct workload access may
  still expose legacy service ports.
- Add a corresponding forward-chain allow rule and retain a default deny for
  unsolicited traffic.
- Keep source-address policy out of RouterOS rules for SSH, PVE, PBS, PDM,
  Nginx UI, database, and application services. The external firewall owns
  source filtering; service authentication and external-firewall policy remain
  required where applicable.
- Keep source addresses visible to the server. Do not add source NAT to normal
  Internet destination-NAT flows merely to simplify return routing.
- Preserve routed direct access to `192.168.24.0/22` throughout the service
  migration and compatibility period; removing it is not part of DNS/NAT
  cutovers.
- Use the site's `.15` router address for private-service high-port access,
  not as a general replacement for public-standard web ingress. Outbound
  identity remains service-specific unless separately approved.
- Use existing `138.121.100.4` as the candidate shared standard-port web
  ingress only after the reverse proxy and existing CRM routing are validated.
- Retain the dedicated GPS, transitional CEIS, externally administered
  Prestoprenda, and customer-owned Polodesalud addresses as specified in the
  October 15 target layout.
- Keep production Mailcow on `138.121.100.5`; mail reputation, SPF, PTR, and
  delivery make it an explicit exception to `.15` consolidation.
- Keep `mail.intelisis.com.ar` as the canonical Mailcow host. CNAME only
  service hostnames to it; preserve domain-apex MX/TXT records and point MX
  directly at the canonical host.
- Keep authoritative DNS and protocol-specific services such as PBX on their
  dedicated addresses unless their owners approve a separate migration.
- Rate-limit logging and alert on repeated denied connections; do not log
  credentials, request bodies, or message content.
- Preserve rollback as rule disablement plus DNS restoration. Do not delete
  the former public assignment until the observation period has passed.

### Minimal rollout and acceptance

1. Keep router management on its separately defined `28xxx` block; restore
   authenticated API reachability to the 15 unverified routers before
   assessing or changing them.
2. Validate the existing CRM/Gestion `138.121.100.4` standard-port ingress
   before introducing a shared reverse proxy; preserve customer-port NAT.
3. CEIS is operator-confirmed operational on `.100.8`; only TCP `80`/`443`
   are forwarded. Consider its shared reverse-proxy migration separately.
4. Consolidate private server GUI/SSH endpoints onto existing site-router
   addresses using the approved high-port registry and external-firewall
   access policy.
5. Verify every DNS, public client port, backend listener, TLS identity, and
   source policy from the appropriate internal and external networks.
6. Preserve routed direct access and rollback options during each transition.
   Remove an old address only after acceptance, owner approval, and the
   agreed observation period.

The router-management migration is verified on all 199 API-reachable routers;
15 routers remain unverified. The canonical registry defines 46
endpoints: 24 PVE, three PBS, three PDM, two WEB, two Mantis, two disabled
Development SSH proposals, active GPS and IoT administrative SSH rules, four
disabled TIC S3 high-port NAT proposals, and four active Cordoba S3 endpoints.
Ollama has no public NAT proposal. GPS retains its own public
IP and multiple client ports. CEIS is published at `.100.8` and retains its
dedicated IP while the later proxy decision remains separate. UDP `12321` is
unused and is not published.
IoT is published at `.100.6` with firmware HTTP and HTTPS/MQTT TLS verified;
certificate renewal and SSH on high port `20073` are complete. The old public
SSH `8922` forward is retired, while MQTT `8883` remains enabled. GPS SSH on
high port `20083` is also key-authenticated. Projects is
powered off and is not staged.
WEB HTTPS/SSH are active on `20602`/`20603`; Mantis HTTPS/SSH are active on TIC
on `20502`/`20503`. Both DNS views make `mantis.intelisis.com.ar` a CNAME to
`tic.intelisis.com.ar`; no Mantis legacy forwarding was found on Lujan.
October 16 transport checks reached Mantis HTTPS and SSH from this workstation;
an authenticated web login reached the dashboard with TLS verification
enabled. No issue or customer records were read or changed. The operator
confirms all ingress access control is enforced by the external firewall.

## Required decisions

Before implementation, approve:

1. The recovery path and validation window for the 15 API-unreachable routers
   before their `28xxx` service state can be verified.
2. The recovery path for API-unreachable routers and API-SSL certificate
   readiness; configured TLS ports do not prove usable TLS.
3. The deterministic workload port blocks and router-reserved exclusions.
4. The external-firewall source policies for administrative and application
   service classes; do not implement them as RouterOS source-address matches.
5. The first HTTPS-only pilot workload and its service owner.
6. The proposed `MIKROTIK-MANAGER/config/public_nat_registry.yaml` registry
   location and its change-approval owner.
7. The observation period before releasing each legacy public assignment.
8. The compatibility/observation criteria and separate approval required
   before withdrawing routes to or blocking direct access to `192.168.24.0/22`.

No live DNS or network change is authorized by this proposal.
