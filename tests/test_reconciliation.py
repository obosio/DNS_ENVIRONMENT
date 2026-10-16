from __future__ import annotations

import copy
import unittest
from pathlib import Path

import yaml

from dns_environment.reconciliation import (
    ReconciliationValidationError,
    load_reconciliation,
    validate_reconciliation,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ReconciliationValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        path = PROJECT_ROOT / "config" / "external_dns_reconciliation.yaml"
        cls.raw_doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        cls.doc = {"reconciliation": cls.raw_doc}

    def test_repository_reconciliation_is_valid(self) -> None:
        counts = validate_reconciliation(self.doc)
        self.assertEqual(counts["services"], 20)
        self.assertEqual(counts["forward_addresses"], 14)
        self.assertEqual(counts["dedicated_exception"], 13)
        self.assertEqual(counts["migration_candidate"], 1)
        self.assertEqual(counts["owner_decision_required"], 1)
        self.assertEqual(counts.get("preserve_pending_dedicated_cutover", 0), 0)
        self.assertEqual(counts["active_shared_endpoint"], 2)
        self.assertEqual(counts["retirement_pending"], 2)
        self.assertEqual(counts["retired"], 1)

    def test_all_public_addresses_have_valid_access_classification(self) -> None:
        services = self.doc["reconciliation"]["services"]

        self.assertTrue(
            all(
                service["access_class"]
                in self.doc["reconciliation"]["metadata"]["access_class_policy"]
                and isinstance(service["high_port_migration_eligible"], bool)
                for service in services
            )
        )

    def test_gps_keeps_its_dedicated_public_endpoint(self) -> None:
        gps = next(
            service
            for service in self.doc["reconciliation"]["services"]
            if service["public_address"] == "138.121.100.2"
        )

        self.assertEqual(gps["access_class"], "public_standard_service")
        self.assertEqual(gps["disposition"], "dedicated_exception")
        self.assertFalse(gps["migration_eligible"])
        self.assertFalse(gps["high_port_migration_eligible"])
        planned_gps = next(
            service
            for service in self.doc["reconciliation"]["planned_address_reassignments"]
            if service["service"] == "gps"
        )
        self.assertNotIn("tcp/8080", planned_gps["planned_ports"])
        self.assertIn("tcp/20083", planned_gps["planned_ports"])
        self.assertEqual(
            planned_gps["status"],
            "ssh_high_port_and_ingestion_operator_confirmed",
        )
        self.assertIn(
            "authorized removal of the unused TCP 8080 mapping",
            planned_gps["blockers"][2],
        )
        self.assertNotIn("8080", gps["nat_summary"])
        self.assertTrue(
            any(
                "operator confirms GPS protocol-level ingestion is already validated"
                in blocker
                for blocker in planned_gps["blockers"]
            )
        )

    def test_iot_services_and_high_port_ssh_are_verified_and_legacy_ssh_is_retired(
        self,
    ) -> None:
        services = {
            service["public_address"]: service
            for service in self.doc["reconciliation"]["services"]
        }
        self.assertEqual(
            services["138.121.100.6"]["dns_a_names"], ["iot.intelisis.com.ar"]
        )
        self.assertEqual(
            services["138.121.100.6"]["ptr_name"], "iot.intelisis.com.ar"
        )
        self.assertEqual(services["138.121.101.3"]["dns_a_names"], [])
        self.assertIsNone(services["138.121.101.3"]["ptr_name"])

        iot = next(
            service
            for service in self.doc["reconciliation"]["planned_address_reassignments"]
            if service["service"] == "iot"
        )

        self.assertEqual(
            iot["status"],
            "external_a_ptr_service_endpoints_and_cert_renewal_verified_admin_ssh_high_port_verified_legacy_path_retired",
        )
        self.assertTrue(
            any(
                "capped public firmware GET returned HTTP 200" in blocker
                for blocker in iot["blockers"]
            )
        )
        self.assertTrue(
            any(
                "renewed production certificate" in blocker
                for blocker in iot["blockers"]
            )
        )
        self.assertTrue(
            any(
                "local Home Assistant app local_iot_certbot_dns is started in production mode"
                in blocker
                for blocker in iot["blockers"]
            )
        )
        self.assertTrue(
            any(
                "app completed DNS-01/RFC2136 issuance, deployed the certificate to /ssl"
                in blocker
                for blocker in iot["blockers"]
            )
        )
        self.assertTrue(
            any(
                "operator approved a forced production renewal"
                in blocker
                for blocker in iot["blockers"]
            )
        )
        self.assertTrue(
            any(
                "deployed and served HTTPS/MQTT certificate fingerprints match"
                in blocker
                for blocker in iot["blockers"]
            )
        )
        self.assertTrue(
            any(
                "SOA serial is 2026101522 on primary and secondary"
                in blocker
                for blocker in iot["blockers"]
            )
        )
        self.assertFalse(
            any("blocks installation" in blocker for blocker in iot["blockers"])
        )
        self.assertTrue(
            any("TCP 20073" in blocker for blocker in iot["blockers"])
        )
        self.assertTrue(
            any(
                "dedicated IoT-admin public key" in blocker
                and "new .100.6:20073" in blocker
                and "public 8922 SSH forward was removed" in blocker
                for blocker in iot["blockers"]
            )
        )
        self.assertTrue(
            any(
                "external firewall owner confirmed the TCP 20073 source policy"
                in blocker
                for blocker in iot["blockers"]
            )
        )

    def test_prestoprenda_external_path_is_accepted_without_internal_publication(
        self,
    ) -> None:
        prestoprenda = next(
            service
            for service in self.doc["reconciliation"]["planned_address_reassignments"]
            if service["service"] == "prestoprenda"
        )

        self.assertEqual(
            prestoprenda["status"],
            "operator_confirmed_external_dns_and_service_verified",
        )
        self.assertEqual(prestoprenda["current_public_address"], "138.121.101.2")
        self.assertEqual(prestoprenda["target_public_address"], "138.121.100.7")
        self.assertEqual(prestoprenda["dns_owner"], "external")
        self.assertEqual(prestoprenda["internal_dns_publication"], "prohibited")
        self.assertEqual(
            prestoprenda["planned_ports"], ["tcp/22", "tcp/80", "tcp/443"]
        )
        self.assertTrue(
            any(
                "former 138.121.101.2 path has no current CORE assignment or NAT"
                in blocker
                for blocker in prestoprenda["blockers"]
            )
        )

    def test_ceis_is_operational_and_only_web_ports_are_published(
        self,
    ) -> None:
        services = {
            service["public_address"]: service
            for service in self.doc["reconciliation"]["services"]
        }
        self.assertEqual(
            services["138.121.100.8"]["dns_a_names"],
            ["ceis.polodesalud.com.ar"],
        )
        self.assertEqual(
            services["138.121.100.8"]["ptr_name"],
            "ceis.polodesalud.com.ar",
        )
        self.assertEqual(services["138.121.101.6"]["dns_a_names"], [])
        self.assertIsNone(services["138.121.101.6"]["ptr_name"])
        self.assertEqual(
            services["138.121.101.6"]["disposition"], "retirement_pending"
        )
        ceis = next(
            service
            for service in self.doc["reconciliation"]["planned_address_reassignments"]
            if service["service"] == "ceis"
        )
        self.assertEqual(
            ceis["status"],
            "external_a_ptr_published_operator_confirmed_operational_web_only",
        )
        self.assertTrue(
            any(
                "The operator confirms CEIS was and remains operational"
                in blocker
                for blocker in ceis["blockers"]
            )
        )
        self.assertEqual(
            ceis["planned_ports"],
            ["tcp/80", "tcp/443"],
        )
        self.assertTrue(
            any(
                "Only TCP 80 and 443 are forwarded to the guest"
                and "TCP 12321 and 12323 were removed as unused"
                in blocker
                for blocker in ceis["blockers"]
            )
        )
        self.assertEqual(
            services["138.121.100.8"]["nat_summary"],
            "TCP ports 80 and 443 only to 192.168.25.151",
        )

    def test_public_standard_service_cannot_be_high_port_migrated(self) -> None:
        doc = copy.deepcopy(self.doc)
        service = next(
            service
            for service in doc["reconciliation"]["services"]
            if service["public_address"] == "138.121.100.2"
        )
        service["high_port_migration_eligible"] = True

        with self.assertRaisesRegex(
            ReconciliationValidationError,
            "only restricted_admin services may be high-port migration candidates",
        ):
            validate_reconciliation(doc)

    def test_unknown_access_class_is_rejected(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["reconciliation"]["services"][0]["access_class"] = "unknown"

        with self.assertRaisesRegex(
            ReconciliationValidationError, "unknown access_class"
        ):
            validate_reconciliation(doc)

    def test_duplicate_address_rejected(self) -> None:
        doc = copy.deepcopy(self.doc)
        services = doc["reconciliation"]["services"]
        services.append(copy.deepcopy(services[0]))
        doc["reconciliation"]["metadata"]["counts"]["reconciled_public_addresses"] += 1
        with self.assertRaisesRegex(ReconciliationValidationError, "is duplicated"):
            validate_reconciliation(doc)

    def test_unknown_disposition_rejected(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["reconciliation"]["services"][0]["disposition"] = "invalid_disposition"
        with self.assertRaisesRegex(ReconciliationValidationError, "unknown disposition"):
            validate_reconciliation(doc)

    def test_retired_aero_names_are_tracked_as_retired(self) -> None:
        aliases = self.doc["reconciliation"]["aliases"]
        retired = aliases["retired_targets"]["services.aero.com.ar"]
        self.assertEqual(
            retired["verification"],
            "authoritative_nxdomain_both_views_both_authorities",
        )

        retired_public_address = next(
            service
            for service in self.doc["reconciliation"]["services"]
            if service["public_address"] == "138.121.101.4"
        )
        self.assertIsNone(retired_public_address["ptr_name"])

    def test_completed_retirements_and_operator_preservation_are_recorded(self) -> None:
        services = {
            service["public_address"]: service
            for service in self.doc["reconciliation"]["services"]
        }
        self.assertEqual(services["138.121.100.3"]["dns_a_names"], [])
        self.assertEqual(services["138.121.101.7"]["dns_a_names"], [])
        self.assertIsNone(services["138.121.101.7"]["ptr_name"])
        ollama = services["138.121.101.4"]
        self.assertEqual(ollama["role"], "retired_public_address")
        self.assertEqual(ollama["access_class"], "retired")
        self.assertEqual(ollama["disposition"], "retired")
        self.assertIn(
            "removed from core-router-lujan loopback",
            ollama["router_assignment"].casefold(),
        )
        self.assertFalse(ollama["high_port_migration_eligible"])
        self.assertIn(
            "internal-only test service",
            " ".join(ollama["blockers"]).casefold(),
        )
        prestoprenda = next(
            service
            for service in self.doc["reconciliation"]["planned_address_reassignments"]
            if service["service"] == "prestoprenda"
        )
        self.assertEqual(
            prestoprenda["status"],
            "operator_confirmed_external_dns_and_service_verified",
        )
        self.assertEqual(prestoprenda["internal_dns_publication"], "prohibited")
        self.assertEqual(
            services["138.121.101.242"]["disposition"],
            "dedicated_exception",
        )
        self.assertIn(
            "Operator-confirmed correct",
            services["138.121.101.242"]["blockers"][0],
        )

    def test_live_changes_authorization_must_remain_false(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["reconciliation"]["metadata"]["live_changes_authorized"] = True
        with self.assertRaisesRegex(
            ReconciliationValidationError, "must remain false"
        ):
            validate_reconciliation(doc)
