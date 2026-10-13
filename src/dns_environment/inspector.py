from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import dns.message
import dns.query
import dns.rdatatype
import dns.resolver

AUTHORITATIVE_SERVERS = [
    {
        "id": "ns1-internal",
        "name": "ns1.intelisis.com.ar",
        "ip": "192.168.25.100",
        "view": "Internal",
        "role": "primary",
        "site": "Lujan (CT 25100)",
    },
    {
        "id": "ns2-internal",
        "name": "ns2.intelisis.com.ar",
        "ip": "192.168.26.100",
        "view": "Internal",
        "role": "secondary",
        "site": "Centro (CT 26100)",
    },
    {
        "id": "ns1-external",
        "name": "ns1.intelisis.com.ar",
        "ip": "138.121.100.1",
        "view": "External",
        "role": "primary",
        "site": "Lujan (Public)",
    },
    {
        "id": "ns2-external",
        "name": "ns2.intelisis.com.ar",
        "ip": "138.121.102.1",
        "view": "External",
        "role": "secondary",
        "site": "Centro (Public)",
    },
]

FORWARD_ZONES = [
    "intelisis.com.ar",
    "aero.com.ar",
    "polodesalud.com.ar",
    "pro3d.com.ar",
]

REVERSE_ZONES = [
    "100.121.138.in-addr.arpa",
    "101.121.138.in-addr.arpa",
    "102.121.138.in-addr.arpa",
    "103.121.138.in-addr.arpa",
]

PUBLIC_RESOLVERS = [
    {"name": "Cloudflare", "ip": "1.1.1.1"},
    {"name": "Google", "ip": "8.8.8.8"},
]


@dataclass
class SoaResult:
    zone: str
    server_id: str
    server_ip: str
    serial: int | None = None
    mname: str | None = None
    rname: str | None = None
    error: str | None = None


@dataclass
class InspectionReport:
    server_results: list[SoaResult] = field(default_factory=list)
    zone_synced: dict[str, bool] = field(default_factory=dict)
    summary_messages: list[str] = field(default_factory=list)
    all_ok: bool = True


def query_soa(zone: str, server_ip: str, timeout: float = 2.0) -> tuple[int | None, str | None, str | None, str | None]:
    try:
        query = dns.message.make_query(zone, dns.rdatatype.SOA)
        response = dns.query.udp(query, server_ip, timeout=timeout)
        if response.rcode() != dns.rcode.NOERROR:
            return None, None, None, f"RCODE: {dns.rcode.to_text(response.rcode())}"
        for rrset in response.answer:
            if rrset.rdtype == dns.rdatatype.SOA:
                soa_rr = rrset[0]
                return soa_rr.serial, str(soa_rr.mname), str(soa_rr.rname), None
        return None, None, None, "No SOA answer returned"
    except Exception as exc:
        return None, None, None, str(exc)


def inspect_zones(
    zones: list[str] | None = None,
    servers: list[dict[str, Any]] | None = None,
    timeout: float = 2.0,
) -> InspectionReport:
    target_zones = zones or FORWARD_ZONES
    target_servers = servers or AUTHORITATIVE_SERVERS
    report = InspectionReport()

    for zone in target_zones:
        zone_serials: dict[str, int] = {}
        for srv in target_servers:
            serial, mname, rname, err = query_soa(zone, srv["ip"], timeout=timeout)
            result = SoaResult(
                zone=zone,
                server_id=srv["id"],
                server_ip=srv["ip"],
                serial=serial,
                mname=mname,
                rname=rname,
                error=err,
            )
            report.server_results.append(result)
            if serial is not None:
                zone_serials[srv["id"]] = serial
            else:
                report.all_ok = False
                report.summary_messages.append(
                    f"FAILED: {zone} on {srv['id']} ({srv['ip']}): {err}"
                )

        unique_serials = set(zone_serials.values())
        if len(unique_serials) == 1 and len(zone_serials) == len(target_servers):
            report.zone_synced[zone] = True
            report.summary_messages.append(
                f"OK: {zone} synchronized at serial {list(unique_serials)[0]} across {len(target_servers)} servers"
            )
        else:
            report.zone_synced[zone] = False
            report.all_ok = False
            report.summary_messages.append(
                f"MISMATCH: {zone} serials differ or missing across servers: {zone_serials}"
            )

    return report
