# Public IP reorganization proposal

Updated: October 12, 2026 (ART)

## Purpose

This document records the inspected public IPv4 assignments, the completed
Mailcow pilot cleanup, and the remaining controlled reorganization proposal.
Completed changes are explicitly identified; proposed ingress publication
still requires assignment approval.

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

The four External forward zones contain 15 unique IPv4 addresses in A records
at snapshot time. Mail migration is complete, so the pilot records on
`138.121.100.8` are stale cleanup items rather than a retained service. After
their removal, 14 unique addresses remain in active External A records.
Multiple DNS names sharing one address are grouped below.

| Public IP | External A records | Current role | Proposed disposition |
| --- | --- | --- | --- |
| `138.121.100.1` | `ns1.aero.com.ar`, `ns1.intelisis.com.ar`, `ns1.polodesalud.com.ar`, `ns1.pro3d.com.ar` | Primary authoritative DNS | Preserve as dedicated DNS infrastructure |
| `138.121.100.2` | `gps.aero.com.ar` | GPS application | Assess for ingress migration after application testing |
| `138.121.100.3` | `pbx.aero.com.ar` | PBX/voice service | Preserve as a dedicated non-HTTP service unless its protocol design changes |
| `138.121.100.4` | `aero.com.ar`, `intelisis.com.ar` | Shared web apex address | Preserve during transition; migrate only through a separately approved apex cutover |
| `138.121.100.5` | `mail.aero.com.ar`, `mail.intelisis.com.ar`, `mail.polodesalud.com.ar`, `mail.pro3d.com.ar` | Shared production mail address | Preserve as dedicated mail infrastructure |
| `138.121.100.7` | None after Mantis cutover | Legacy Mantis PTR and TCP 443 DNS-cache rollback | Remove the PTR, router address, and rollback NAT after the original TTL and acceptance window |
| `138.121.100.15` | `mantis.aero.com.ar`, `web.intelisis.com.ar` | Shared Lujan workload endpoints | Preserve for canonical high-port workload publication |
| `138.121.100.8` | None after cleanup | Retired migration-pilot address | DNS, PTR, router address, route, and NAT removed; provider allocation still requires confirmation before reuse |
| `138.121.101.3` | `iot.intelisis.com.ar` | IoT service | Assess protocol and client compatibility before any ingress migration |
| `138.121.101.6` | `ceis.polodesalud.com.ar` | Web application | Candidate for migration behind shared ingress |
| `138.121.101.7` | `pms.polodesalud.com.ar` | Web application | Candidate for migration behind shared ingress |
| `138.121.101.8` | `development.intelisis.com.ar` | Development web environment | Preferred low-risk application migration candidate |
| `138.121.101.242` | `polodesalud.com.ar` | Public zone apex | Preserve until an apex migration is explicitly approved |
| `138.121.101.246` | `pro3d.com.ar` | Public zone apex | Preserve until an apex migration is explicitly approved |
| `138.121.102.1` | `ns2.aero.com.ar`, `ns2.intelisis.com.ar`, `ns2.polodesalud.com.ar`, `ns2.pro3d.com.ar` | Secondary authoritative DNS | Preserve as dedicated DNS infrastructure |
| `138.121.102.6` | `projects.intelisis.com.ar` | Projects application | Candidate for migration behind shared ingress |

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
| `138.121.100.7` | `mantis.aero.com.ar` (temporary legacy PTR pending endpoint acceptance) |
| `138.121.100.8` | `mailcow-pilot.intelisis.com.ar` (obsolete pilot PTR; remove) |
| `138.121.101.3` | `iot.intelisis.com.ar` |
| `138.121.101.4` | `database.intelisis.com.ar` |
| `138.121.101.6` | `ceis.polodesalud.com.ar` |
| `138.121.101.7` | `pms.polodesalud.com.ar` |
| `138.121.102.1` | `ns2.intelisis.com.ar` |
| `138.121.102.6` | `projects.intelisis.com.ar` |

`138.121.101.4` has no observed External A record but does have an External PTR.
It is therefore already represented in DNS and must not be considered an
available address.

An A record without a PTR does not prove a defect for HTTP services, and a PTR
without an A record does not prove that an address is unused. Forward/reverse
consistency should be decided according to each service's protocol and
operational requirements.

## Related DNS findings

- `138.121.100.4` is not available for the new ingress without first migrating
  both `aero.com.ar` and `intelisis.com.ar` apex traffic.
- `gestion.aero.com.ar`, `public.aero.com.ar`, and `www.aero.com.ar` are CNAMEs
  to `aero.com.ar`, so they also currently depend on `138.121.100.4`.
- `owncloud.aero.com.ar` and `wiki.aero.com.ar` are CNAMEs to
  `services.aero.com.ar`, but no External A record for
  `services.aero.com.ar` was observed. This should be investigated before
  migration or cleanup.
-   `web.intelisis.com.ar` is now externally published through
  `138.121.100.15:21160` to `192.168.25.60:21160`. The WEB SSH mapping remains
  planned and disabled. Source restrictions for HTTPS are owned by the external
  firewall; RouterOS contains only the exact destination-NAT and forward rules.
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

Removing these records does not by itself make `138.121.100.8` available. Also
remove or reconcile any NAT, firewall, routing, monitoring, and provider-side
assignment before returning the address to the unassigned pool.

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
`/root/mailcow-pilot-dns-cleanup-20261012T154202Z/` on CT `25100`.
Provider allocation and external monitoring ownership for `138.121.100.8`
remain outside the router and DNS configuration and must be validated before
the address is reused.

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

### 1. Preserve infrastructure and protocol-specific addresses

Keep these roles outside the shared HTTP ingress:

- `138.121.100.1` and `138.121.102.1`: authoritative DNS.
- `138.121.100.5`: production mail.
- `138.121.100.3`: PBX unless a separate, protocol-aware migration is designed.

### 2. Allocate one dedicated ingress public address

Allocate a public IP used only for TCP ports 80 and 443, destination-NATed to
`192.168.25.60`. Do not expose Nginx UI's loopback backend port `9000`.

`138.121.100.6` is the preferred ingress candidate. A live validation on
2026-10-12 found no External A or PTR, router address, NAT rule, address-list
entry, filter rule, mangle rule, or route object for the address. ICMP received
no response, and TCP 22, 80, 443, and 9000 were closed or filtered. These checks
establish that no current declaration or listener was observed; assignment to
the ingress still requires operator approval.

If `138.121.100.6` fails validation, select another address only after the same
audit. Do not use `138.121.100.4` or `138.121.101.4` as fallback choices.

### 3. Publish the ingress management name

After the selected address is validated:

- Add External `web.intelisis.com.ar A <ingress-public-ip>`.
- Add or update the matching PTR only if the address is owned and reverse DNS is
  operationally required.
- Permit only canonical endpoint TCP `21160` to `192.168.25.60`; do not retain
  compatibility listeners on TCP 80 or 443.
- Keep TCP 9000 unexposed.
- Retain application authentication and external-firewall policy for the web
  management endpoint.
- Verify the existing certificate, HTTPS identity, WebSocket operation, and
  Nginx UI authentication from an external network.

### 4. Migrate web services in controlled waves

Recommended order:

1. Remove the obsolete pilot forward/reverse DNS records and reconcile
   `138.121.100.8` network assignments.
2. `development.intelisis.com.ar` as a low-risk validation tenant.
3. `ceis.polodesalud.com.ar`, `pms.polodesalud.com.ar`, and
   `projects.intelisis.com.ar`; Mantis completed endpoint `150`.
4. `gps.aero.com.ar` and `iot.intelisis.com.ar` only after protocol and client
   compatibility checks.
5. Zone apexes and their aliases last:
   `aero.com.ar`, `intelisis.com.ar`, `polodesalud.com.ar`, and
   `pro3d.com.ar`.

For each migrated HTTP service:

- migrate any HTTP-01 certificate renewal to the scoped DNS-01 model before
  removing public TCP 80; Mantis completed this prerequisite on October 12,
  2026, with a single-name RFC2136 grant, successful 120-second staging
  renewal, local Apache deployment hook, and no residual challenge TXT;

- Configure and validate the Nginx UI site before changing DNS.
- Lower TTL in advance when rollback speed matters.
- Confirm upstream health, headers, sessions, uploads, and WebSockets.
- Change the public A/CNAME record to the ingress address.
- Verify externally over IPv4 and trusted TLS.
- Remove the old NAT/public exposure only after acceptance.
- Retain a documented DNS and firewall rollback.

## Proposed address-role policy

This policy describes the desired organization; it does not retroactively
declare unused addresses:

| Range / address | Intended role |
| --- | --- |
| `138.121.100.1` and `138.121.102.1` | Authoritative DNS |
| `138.121.100.5` | Production mail egress/ingress |
| `138.121.100.8` | Pilot declarations removed; keep unassigned pending provider-allocation confirmation |
| `138.121.100.15`, `138.121.101.15`, `138.121.102.15`, and `45.238.8.15` | Per-site cluster workload ingress |
| Candidate `138.121.100.6` | Unconfirmed spare; no longer the default shared-ingress proposal |
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

The routers themselves already listen on TCP `20022`, `28291`, `28728`, and
`28729`. Router management should be consolidated into the exclusive
`20000-20999` block before workload publication. RouterOS also uses several
dynamic routing, detection, and WireGuard ports above `30000`, so the initial
workload allocation should remain below `28000`.

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

Reserve `20000-20999` exclusively for services hosted by the edge router
itself. Use the following target standard:

| Router service | Target TCP port | Current common port |
| --- | ---: | ---: |
| SSH | `20022` | `20022` |
| HTTP management, if retained | `20080` | `8081` |
| HTTPS/reverse proxy, if retained | `20443` | `443` |
| Winbox | `20291` | `28291` |
| RouterOS API | `20728` | `28728` |
| RouterOS API TLS | `20729` | `28729` |

The target ports are `20000 + (native RouterOS port modulo 1000)`, retaining a
recognizable relationship with native services while keeping router ownership
inside one exclusive block. Routing protocols and WireGuard retain their
separately managed ports; they are not management services and must not be
folded into this block.

Router port migration must be performed one edge at a time:

1. Save a RouterOS export and preserve an out-of-band or already authenticated
   recovery path.
2. Add source-restricted input rules for the target port.
3. Change one RouterOS service port and verify access immediately.
4. Update MIKROTIK-MANAGER inventory, service-discovery defaults, and operator
   connection profiles before changing the next service.
5. Remove the old input rule only after the new path is proven.
6. Keep `28000-28999` unallocated during a defined observation period; release
   it only after every managed router and automation client has migrated.

All four CORE edge routers completed the management-port migration. SSH,
Winbox, and authenticated plain API pass on `20022`, `20291`, and `20728`; the
old `28xxx` ports are closed. The unused reverse-proxy records are disabled in
their `20443` reserved slots. API TLS is TCP-reachable on `20729` but is not
operational because the RouterOS services have no certificate.

CORE ROUTER TIC completed the pilot on 2026-10-12:

- SSH remained on `20022`.
- Winbox moved from `28291` to `20291`.
- API moved from `28728` to `20728`.
- API TLS moved from `28729` to `20729`.
- Authenticated API verification passed and all three old ports closed.
- Inventory and Winbox profiles were updated.
- The existing unrestricted provider exposure was preserved by explicit
  operator decision; source-policy hardening remains separate.
- Fleet normalization now declares the approved `20xxx` ports and TIC is no
  longer excluded for this migration.

### Deterministic external-port allocation

Each site has a separate public address, so the same external port can be
reused at different sites. Assign every published server a unique three-digit
site-local endpoint ID, `EEE`, and use these external slots:

| External port | Intended slot | Typical internal port |
| --- | --- | --- |
| `21000 + EEE` | Primary TLS service | `443`, `8006`, or another registered TLS port |
| `22000 + EEE` | SSH administration | `22` |
| `23000 + EEE` | Secondary TLS service | `8007` or another registered TLS port |
| `24000 + EEE` | Tertiary TLS service | `8443` or another registered TLS port |
| `25000 + EEE` | Application TCP slot 1 | Registry-defined |
| `26000 + EEE` | Application TCP slot 2 | Registry-defined |
| `27000 + EEE` | Application UDP slot 1 | Registry-defined |

Endpoint ID allocation:

| Endpoint IDs | Class |
| --- | --- |
| `001-099` | Physical cluster, backup, and management infrastructure |
| `100-799` | LXC and VM workloads |
| `800-899` | Network and security appliances |
| `900-999` | Temporary migrations, with an expiry date |

Infrastructure IDs may mirror the final address octet when that remains unique
within the reserved infrastructure class. Workload IDs are registry
allocations and are not derived from VMID, VLAN, or address. This avoids
collisions between servers such as `192.168.12.11` and `192.168.25.11`.

Reserve `20000-20999` exclusively for router management. Workloads use
`21000-27999`. Keep `28000-29999` unallocated during the router-port
migration and until each edge's routing and tunnel listeners have been
checked.

Examples:

| Public endpoint | Internal endpoint | Purpose |
| --- | --- | --- |
| `138.121.100.15:21160` | `192.168.25.60:21160` | Lujan WEB environment HTTPS, endpoint `160` |
| `138.121.100.15:22160` | `192.168.25.60:22` | Lujan WEB SSH, endpoint `160`, source-restricted |
| `138.121.100.15:21011` | `192.168.12.11:8006` | Lujan PVE node 1 |
| `138.121.100.15:21031` | `192.168.12.31:8006` | Lujan standalone PVE |
| `138.121.100.15:23031` | `192.168.12.31:8007` | Lujan PBS |
| `138.121.100.15:24031` | `192.168.12.31:8443` | Lujan PDM |

The formula allocates a slot, not an implicit internal service. Every mapping
must still be present in a reviewed registry containing site, public address,
external protocol/port, destination address/port, service owner, FQDN, source
policy, certificate lineage, change reference, and rollback rule. Reject a
mapping when its endpoint ID or calculated port is already allocated.
The recommended canonical registry is
`MIKROTIK-MANAGER/config/public_nat_registry.yaml`; it must contain no
credentials or certificate private material.

### TLS and DNS behavior

Destination NAT remains layer 4 and must not terminate or replace TLS. Each
external DNS name points to the site's `.15` address, while the client connects
to the allocated external port. The destination server continues presenting
its existing local certificate:

`https://service.example:external-port -> site .15:external-port -> internal-ip:native-port`

TLS certificates validate hostnames, not TCP port numbers. The certificate
must therefore contain the exact external FQDN. Keep DNS-01 renewal and the
existing local deployment hooks; no public port `80` or `443` is required for
renewal. Internal split DNS should continue resolving the same FQDN directly
to the private address and native service port where clients support separate
internal and external URLs.

Because DNS does not carry port numbers, one saved URL cannot transparently
use the high external port and the native internal port. Clients that move
between networks need separate endpoint definitions, or a separately designed
hairpin/redirect policy. The initial rollout should use separate external and
internal URLs and must not add broad hairpin NAT.

### Security and routing policy

- Create one explicit destination-NAT rule per protocol/port mapping. Match the
  exact `.15` destination address; never use a catch-all destination.
- Add a corresponding forward-chain allow rule and retain a default deny for
  unsolicited traffic.
- Require source-address allowlists for SSH, PVE, PBS, PDM, Nginx UI, database,
  and other administrative services. Public application services require an
  explicit owner decision.
- Keep source addresses visible to the server. Do not add source NAT to normal
  Internet destination-NAT flows merely to simplify return routing.
- Use the site's `.15` only for inbound consolidation. Outbound identity
  remains service-specific unless separately approved.
- Keep production Mailcow on `138.121.100.5`; mail reputation, SPF, PTR, and
  delivery make it an explicit exception to `.15` consolidation.
- Keep authoritative DNS and protocol-specific services such as PBX on their
  dedicated addresses unless their owners approve a separate migration.
- Rate-limit logging and alert on repeated denied connections; do not log
  credentials, request bodies, or message content.
- Preserve rollback as rule disablement plus DNS restoration. Do not delete
  the former public assignment until the observation period has passed.

### Minimal rollout and acceptance

1. Migrate one non-critical router's management services into
   `20000-20999`, update automation, and prove rollback.
2. Complete the router-port migration across all four edge routers.
3. Create the central mapping registry and enforce the router-owned block.
4. Pilot one HTTPS-only, non-critical workload at one site.
5. Publish its External A record to the site's `.15`, retain Internal split
   DNS, and add the exact destination-NAT and forward rules.
6. Verify from an independent Internet host: DNS answer, connected public IP
   and external port, trusted certificate/SAN, HTTP response, and source-policy
   enforcement.
7. Verify internally that the private endpoint uses the same canonical high
   port and that well-known compatibility listeners are closed.
8. Test renewal with the existing DNS-01 deploy hook.
9. Disable the new NAT rule and restore DNS to prove rollback before expanding
   to administrative or multi-port services.

The router-management migration is complete. The canonical registry defines
33 mappings: 24 PVE, three PBS, three PDM, two WEB mappings, and Mantis HTTPS.
WEB HTTPS at Lujan endpoint `160` and Mantis HTTPS at endpoint `150` are
active; WEB SSH remains disabled. Mantis uses the same canonical port `21150`
internally and externally. Its former `.7:443` publication is retained only
as a temporary DNS-cache rollback path to backend port `21150`.

## Required decisions

Before implementation, approve:

1. The `20000-20999` router-management service mapping and migration order.
2. The observation period before releasing the old `28xxx` router ports.
3. The deterministic workload port blocks and router-reserved exclusions.
4. The source allowlists for administrative service classes.
5. The first HTTPS-only pilot workload and its service owner.
6. The proposed `MIKROTIK-MANAGER/config/public_nat_registry.yaml` registry
   location and its change-approval owner.
7. The observation period before releasing each legacy public assignment.

No live DNS or network change is authorized by this proposal.
