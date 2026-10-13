from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import dns.message
import dns.rdatatype
import dns.rrset

from dns_environment.inspector import (
    AUTHORITATIVE_SERVERS,
    FORWARD_ZONES,
    InspectionReport,
    inspect_zones,
    query_soa,
)


class InspectorUnitTests(unittest.TestCase):
    def test_authoritative_servers_definition(self) -> None:
        self.assertEqual(len(AUTHORITATIVE_SERVERS), 4)
        server_ids = [s["id"] for s in AUTHORITATIVE_SERVERS]
        self.assertIn("ns1-internal", server_ids)
        self.assertIn("ns2-internal", server_ids)
        self.assertIn("ns1-external", server_ids)
        self.assertIn("ns2-external", server_ids)

    def test_forward_zones_definition(self) -> None:
        self.assertIn("intelisis.com.ar", FORWARD_ZONES)
        self.assertIn("aero.com.ar", FORWARD_ZONES)
        self.assertIn("polodesalud.com.ar", FORWARD_ZONES)
        self.assertIn("pro3d.com.ar", FORWARD_ZONES)

    @patch("dns_environment.inspector.dns.query.udp")
    def test_inspect_zones_synchronized(self, mock_udp: MagicMock) -> None:
        # Mocking successful SOA response
        mock_resp = MagicMock()
        mock_resp.rcode.return_value = dns.rcode.NOERROR

        soa_rr = MagicMock()
        soa_rr.serial = 2026101202
        soa_rr.mname = "ns1.intelisis.com.ar."
        soa_rr.rname = "webmaster.intelisis.com.ar."

        rrset = MagicMock()
        rrset.rdtype = dns.rdatatype.SOA
        rrset.__iter__.return_value = [soa_rr]
        rrset.__getitem__.return_value = soa_rr

        mock_resp.answer = [rrset]
        mock_udp.return_value = mock_resp

        report = inspect_zones(zones=["intelisis.com.ar"], servers=AUTHORITATIVE_SERVERS[:2])
        self.assertTrue(report.all_ok)
        self.assertTrue(report.zone_synced["intelisis.com.ar"])

    @patch("dns_environment.inspector.dns.query.udp")
    def test_inspect_zones_mismatch(self, mock_udp: MagicMock) -> None:
        resp1 = MagicMock()
        resp1.rcode.return_value = dns.rcode.NOERROR
        soa1 = MagicMock(serial=2026101201, mname="ns1.", rname="admin.")
        rrset1 = MagicMock(rdtype=dns.rdatatype.SOA)
        rrset1.__getitem__.return_value = soa1
        resp1.answer = [rrset1]

        resp2 = MagicMock()
        resp2.rcode.return_value = dns.rcode.NOERROR
        soa2 = MagicMock(serial=2026101202, mname="ns1.", rname="admin.")
        rrset2 = MagicMock(rdtype=dns.rdatatype.SOA)
        rrset2.__getitem__.return_value = soa2
        resp2.answer = [rrset2]

        mock_udp.side_effect = [resp1, resp2]

        report = inspect_zones(zones=["intelisis.com.ar"], servers=AUTHORITATIVE_SERVERS[:2])
        self.assertFalse(report.all_ok)
        self.assertFalse(report.zone_synced["intelisis.com.ar"])
