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
        self.assertEqual(counts["preserve_pending_dedicated_cutover"], 1)
        self.assertEqual(counts["active_shared_endpoint"], 2)
        self.assertEqual(counts["retirement_pending"], 2)

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
        self.assertEqual(
            planned_gps["status"],
            "router_and_dns_verified_application_acceptance_pending",
        )

    def test_iot_cutover_is_blocked_by_live_service_validation(self) -> None:
        services = {
            service["public_address"]: service
            for service in self.doc["reconciliation"]["services"]
        }
        self.assertEqual(
            services["138.121.100.6"]["dns_a_names"], ["iot.intelisis.com.ar"]
        )
        self.assertIsNone(services["138.121.100.6"]["ptr_name"])
        self.assertEqual(services["138.121.101.3"]["dns_a_names"], [])
        self.assertEqual(
            services["138.121.101.3"]["ptr_name"], "iot.intelisis.com.ar"
        )

        iot = next(
            service
            for service in self.doc["reconciliation"]["planned_address_reassignments"]
            if service["service"] == "iot"
        )

        self.assertEqual(
            iot["status"],
            "external_a_published_service_validation_blocked",
        )
        self.assertTrue(
            any("expired certificate" in blocker for blocker in iot["blockers"])
        )

    def test_ceis_external_a_is_published_with_ptr_cleanup_pending(self) -> None:
        services = {
            service["public_address"]: service
            for service in self.doc["reconciliation"]["services"]
        }
        self.assertEqual(
            services["138.121.100.8"]["dns_a_names"],
            ["ceis.polodesalud.com.ar"],
        )
        self.assertIsNone(services["138.121.100.8"]["ptr_name"])
        self.assertEqual(services["138.121.101.6"]["dns_a_names"], [])
        self.assertEqual(
            services["138.121.101.6"]["ptr_name"], "ceis.polodesalud.com.ar"
        )
        self.assertEqual(
            services["138.121.101.6"]["disposition"], "retirement_pending"
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

        database = next(
            service
            for service in self.doc["reconciliation"]["services"]
            if service["public_address"] == "138.121.101.4"
        )
        self.assertIsNone(database["ptr_name"])

    def test_completed_retirements_and_operator_preservation_are_recorded(self) -> None:
        services = {
            service["public_address"]: service
            for service in self.doc["reconciliation"]["services"]
        }
        self.assertEqual(services["138.121.100.3"]["dns_a_names"], [])
        self.assertEqual(services["138.121.101.7"]["dns_a_names"], [])
        self.assertIsNone(services["138.121.101.7"]["ptr_name"])
        ollama = services["138.121.101.4"]
        self.assertEqual(
            ollama["role"], "ollama_selected_public_address_pending_reactivation"
        )
        self.assertEqual(ollama["access_class"], "public_native_protocol")
        self.assertEqual(ollama["disposition"], "preserve_pending_dedicated_cutover")
        self.assertIn(
            "removed from core-router-lujan loopback",
            ollama["router_assignment"].casefold(),
        )
        self.assertFalse(ollama["high_port_migration_eligible"])
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
