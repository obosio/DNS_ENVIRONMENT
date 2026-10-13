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
        self.assertEqual(counts["services"], 16)
        self.assertEqual(counts["forward_addresses"], 14)
        self.assertEqual(counts["dedicated_exception"], 4)
        self.assertEqual(counts["migration_candidate"], 3)
        self.assertEqual(counts["owner_decision_required"], 4)
        self.assertEqual(counts["preserve_pending_dedicated_cutover"], 3)
        self.assertEqual(counts["active_shared_endpoint"], 1)
        self.assertEqual(counts["retirement_pending"], 1)

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
